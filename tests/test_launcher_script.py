from pathlib import Path
import os
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "启动 oixCloud.command"


class LauncherScriptTest(unittest.TestCase):
    def test_launcher_chinese_messages_have_no_terminal_full_stop(self):
        for line in SCRIPT.read_text(encoding="utf-8").splitlines():
            self.assertNotIn('。"', line)
            self.assertNotIn("。'", line)
            self.assertFalse(line.endswith("。"))

    def test_launcher_menu_orders_temporary_before_persistent(self):
        text = SCRIPT.read_text(encoding="utf-8")

        temporary = text.index("1. 临时启动")
        persistent = text.index("2. 常驻启动")
        uninstall = text.index("3. 卸载自动启动")

        self.assertLess(temporary, persistent)
        self.assertLess(persistent, uninstall)

    def test_launcher_can_select_uninstall_without_update(self):
        text = SCRIPT.read_text(encoding="utf-8")

        choose_before_update = text.index('launch_mode="$(choose_launch_mode)"')
        uninstall_before_update = text.index('if [[ "$launch_mode" == "uninstall" ]]')
        update_after_uninstall = text.index("update_if_needed || update_status=$?")

        self.assertLess(choose_before_update, uninstall_before_update)
        self.assertLess(uninstall_before_update, update_after_uninstall)
        self.assertIn("launchctl unload -w", text)
        self.assertIn('/bin/rm -f "$PLIST_PATH"', text)

    def test_launcher_bounds_and_verifies_release_download(self):
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('MAX_DOWNLOAD_BYTES=$((64 * 1024 * 1024))', text)
        self.assertIn('--max-filesize "$MAX_DOWNLOAD_BYTES"', text)
        self.assertIn(
            'verify_release_binary "$temp_bin" "$expected_digest" "$latest_tag"',
            text,
        )
        self.assertIn('is_valid_release_tag "$latest_tag"', text)
        self.assertIn('is_trusted_download_url "$download_url"', text)
        self.assertIn("/^v[0-9]+(?:\\.[0-9]+){1,2}$/", text)
        self.assertIn("/^sha256:[0-9a-f]{64}$/i", text)

    def test_launcher_restores_previous_command_after_failed_post_validation(self):
        text = SCRIPT.read_text(encoding="utf-8")
        start = text.index("install_command_atomically()")
        end = text.index("ensure_installed_command()", start)
        install = text[start:end]

        backup = install.index('/bin/cp -p "$INSTALL_PATH" "$install_backup"')
        replace = install.index('/bin/mv -f "$install_tmp" "$INSTALL_PATH"')
        validate = install.index(
            'verify_release_binary "$INSTALL_PATH" "$expected_digest" "$latest_tag"'
        )
        restore = install.index('/bin/mv -f "$install_backup" "$INSTALL_PATH"')

        self.assertLess(backup, replace)
        self.assertLess(replace, validate)
        self.assertLess(validate, restore)
        self.assertIn("setopt localtraps", install)
        self.assertIn(
            "trap 'trap - HUP INT TERM; rollback_installed_command; exit 130' HUP INT TERM",
            install,
        )

    def test_local_replacement_restores_previous_file_after_term(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            target = root / "target"
            source.write_text("new", encoding="utf-8")
            target.write_text("old", encoding="utf-8")
            source.chmod(0o755)
            target.chmod(0o755)
            command = f'''
              export OIX_LAUNCHER_SOURCE_ONLY=1
              source {self.shell_quote(str(SCRIPT))}
              verify_release_binary() {{
                if [[ "$1" == "$target_path" ]]; then kill -TERM $$; fi
                return 0
              }}
              replace_local_binary {self.shell_quote(str(source))} {self.shell_quote(str(target))} sha256:test v0.0.24
            '''
            result = subprocess.run(
                ["/bin/zsh", "-c", command],
                cwd=ROOT,
                env={**os.environ, "OIX_LAUNCHER_SOURCE_ONLY": "1"},
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 130, result.stderr)
            self.assertEqual(target.read_text(encoding="utf-8"), "old")
            self.assertEqual(list(root.glob("target.new.*")), [])
            self.assertEqual(list(root.glob("target.backup.*")), [])

    @staticmethod
    def shell_quote(value):
        return "'" + value.replace("'", "'\"'\"'") + "'"


if __name__ == "__main__":
    unittest.main()
