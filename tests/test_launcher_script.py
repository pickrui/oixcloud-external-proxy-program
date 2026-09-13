from pathlib import Path
import os
import plistlib
import sys
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

    @unittest.skipUnless(sys.platform == "darwin", "Requires macOS plutil and launch-agent semantics")
    def test_launch_agent_atomically_replaces_read_only_plist_and_escapes_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agents = root / "LaunchAgents"
            agents.mkdir()
            target = agents / "com.example.oixcloud-test.plist"
            target.write_text("old configuration")
            target.chmod(0o444)
            program = root / "oix & cloud <program>"
            result = self.run_launch_agent_fixture(root, target, program)
            self.assertEqual(result.returncode, 0, result.stderr)
            with target.open("rb") as handle:
                plist = plistlib.load(handle)
            self.assertEqual(plist["ProgramArguments"], [str(program), "--tray"])
            self.assertEqual(plist["StandardOutPath"], str(root / "logs" / "a&b<log>.log"))
            self.assertEqual(target.stat().st_mode & 0o777, 0o644)
            self.assertEqual(list(agents.iterdir()), [target])

    @unittest.skipUnless(sys.platform == "darwin" and os.geteuid() != 0, "Requires macOS user permissions")
    def test_failed_plist_write_does_not_stop_existing_service(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agents = root / "LaunchAgents"
            agents.mkdir()
            target = agents / "com.example.oixcloud-test.plist"
            target.write_text("keep existing configuration")
            agents.chmod(0o500)
            try:
                result = self.run_launch_agent_fixture(root, target, root / "program", start=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(target.read_text(), "keep existing configuration")
                self.assertFalse((root / "launchctl-called").exists())
            finally:
                agents.chmod(0o700)

    @unittest.skipUnless(sys.platform == "darwin", "Requires macOS launch-agent semantics")
    def test_launch_agent_does_not_overwrite_symlink_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agents = root / "LaunchAgents"
            agents.mkdir()
            existing = root / "other.plist"
            existing.write_text("unrelated configuration")
            target = agents / "com.example.oixcloud-test.plist"
            target.symlink_to(existing)
            result = self.run_launch_agent_fixture(root, target, root / "program")
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(target.is_symlink())
            self.assertEqual(existing.read_text(), "unrelated configuration")

    def run_launch_agent_fixture(self, root, target, program, start=False):
        # Any accidental service operation is recorded locally, never executed
        # against the real GUI session, even when testing a broken guard.
        stub = root / "launchctl-stub"
        stub.write_text("#!/bin/sh\ntouch " + self.shell_quote(str(root / "launchctl-called")) + "\nexit 1\n")
        stub.chmod(0o755)
        source = root / "launcher.command"
        source.write_text(SCRIPT.read_text().replace("/bin/launchctl", self.shell_quote(str(stub))))
        command = f"""
          export OIX_LAUNCHER_SOURCE_ONLY=1
          source {self.shell_quote(str(source))}
          PLIST_LABEL=com.example.oixcloud-test
          PLIST_PATH={self.shell_quote(str(target))}
          TRAY_LOG_DIR={self.shell_quote(str(root / 'logs'))}
          TRAY_LOG_FILE={self.shell_quote(str(root / 'logs' / 'a&b<log>.log'))}
          INSTALL_PATH={self.shell_quote(str(program))}
          log() {{ :; }}
          alert() {{ :; }}
          {'start_with_launch_agent' if start else 'write_launch_agent'}
        """
        return subprocess.run(["/bin/zsh", "-c", command], capture_output=True, text=True,
                              timeout=10, env={**os.environ, "OIX_LAUNCHER_SOURCE_ONLY": "1"})

    @unittest.skipUnless(sys.platform == "darwin", "Requires macOS launcher")
    def test_disabled_service_is_enabled_before_bootstrap(self):
        result, calls = self.run_service_fixture("disabled")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertLess(calls.index("enable"), calls.index("bootstrap"))
        self.assertIn("notify:oixCloud 已启动", result.stdout)

    @unittest.skipUnless(sys.platform == "darwin", "Requires macOS launcher")
    def test_registered_but_exited_service_is_not_reported_started(self):
        result, _ = self.run_service_fixture("exited")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("notify:oixCloud 已启动", result.stdout)
        self.assertIn("last exit code = 78", result.stdout)

    @unittest.skipUnless(sys.platform == "darwin", "Requires macOS launcher")
    def test_service_that_immediately_exits_is_not_reported_started(self):
        result, _ = self.run_service_fixture("exits_after_first_poll")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("notify:oixCloud 已启动", result.stdout)

    @unittest.skipUnless(sys.platform == "darwin", "Requires macOS launcher")
    def test_enable_failure_preserves_existing_service(self):
        result, calls = self.run_service_fixture("enable_failed")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("bootout", calls)
        self.assertNotIn("bootstrap", calls)

    @unittest.skipUnless(sys.platform == "darwin", "Requires macOS launcher")
    def test_bootstrap_and_kickstart_failures_are_reported(self):
        for scenario in ("bootstrap_failed", "kickstart_failed"):
            with self.subTest(scenario=scenario):
                result, calls = self.run_service_fixture(scenario)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn("notify:oixCloud 已启动", result.stdout)
                self.assertNotIn("load", calls)

    @unittest.skipUnless(sys.platform == "darwin", "Requires macOS launcher")
    def test_unwritable_service_log_preserves_plist_and_running_service(self):
        result, calls = self.run_service_fixture("unwritable_log")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(calls, [])
        self.assertIn("plist:original", result.stdout)

    def run_service_fixture(self, scenario):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            calls = root / "calls"
            marker = root / "enabled"
            polls = root / "polls"
            stub = root / "launchctl"
            stub.write_text("#!" + sys.executable + "\n" + f"""
import pathlib, sys
command = sys.argv[1]
with open({str(calls)!r}, "a") as out:
    out.write(command + "\\n")
scenario = {scenario!r}
if command == "enable":
    if scenario == "enable_failed": sys.exit(1)
    pathlib.Path({str(marker)!r}).touch()
elif command == "bootstrap":
    if scenario == "bootstrap_failed": sys.exit(1)
    if scenario == "disabled" and not pathlib.Path({str(marker)!r}).exists(): sys.exit(1)
elif command == "kickstart" and scenario == "kickstart_failed":
    sys.exit(1)
elif command == "load":
    sys.exit(1)
elif command == "print":
    counter = pathlib.Path({str(polls)!r})
    count = int(counter.read_text()) if counter.exists() else 0
    counter.write_text(str(count + 1))
    if scenario == "exited" or (scenario == "exits_after_first_poll" and count > 0):
        print("state = waiting\\nlast exit code = 78")
    else:
        print("state = running\\npid = {os.getpid()}")
""")
            stub.chmod(0o755)
            source = root / "launcher.command"
            source.write_text(SCRIPT.read_text().replace("/bin/launchctl", self.shell_quote(str(stub))))
            target = root / "service.plist"
            target.write_text("original")
            log_file = root / "tray.log"
            if scenario == "unwritable_log":
                log_file.mkdir()
            command = f"""
              export OIX_LAUNCHER_SOURCE_ONLY=1
              source {self.shell_quote(str(source))}
              PLIST_LABEL=com.example.oixcloud-test
              LAUNCHD_SERVICE=gui/501/com.example.oixcloud-test
              PLIST_PATH={self.shell_quote(str(target))}
              TRAY_LOG_DIR={self.shell_quote(str(root))}
              TRAY_LOG_FILE={self.shell_quote(str(log_file))}
              INSTALL_PATH={self.shell_quote(str(root / 'program'))}
              LOG_FILE={self.shell_quote(str(root / 'launcher.log'))}
              log() {{ print -r -- "$*"; }}
              alert() {{ print -r -- "alert:$*"; }}
              notify() {{ print -r -- "notify:$*"; }}
              sleep() {{ :; }}
              start_with_launch_agent
              result=$?
              print -r -- "plist:$(cat {self.shell_quote(str(target))})"
              exit $result
            """
            result = subprocess.run(["/bin/zsh", "-c", command], capture_output=True, text=True,
                                    timeout=10, env={**os.environ, "OIX_LAUNCHER_SOURCE_ONLY": "1"})
            return result, calls.read_text().splitlines() if calls.exists() else []

    @unittest.skipUnless(sys.platform == "darwin", "Requires macOS launcher")
    def test_api_failure_falls_back_to_pinned_release_and_checksum(self):
        result, urls = self.run_release_fixture()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("download:https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v0.0.31/oixcloud-external-proxy-program-arm64 sha256:" + "a" * 64 + " v0.0.31", result.stdout)
        self.assertEqual(urls[-1], "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v0.0.31/SHA256SUMS")

    @unittest.skipUnless(sys.platform == "darwin", "Requires macOS launcher")
    def test_fallback_rejects_invalid_missing_or_duplicate_checksum(self):
        for manifest in ("", "bad  oixcloud-external-proxy-program-arm64\n",
                         ("a" * 64 + "  oixcloud-external-proxy-program-arm64\n") * 2,
                         "b" * 64 + "  wrong-asset\n"):
            with self.subTest(manifest=manifest):
                result, _ = self.run_release_fixture(manifest=manifest)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertNotIn("download:", result.stdout)
                self.assertNotIn("installed", result.stdout)

    @unittest.skipUnless(sys.platform == "darwin", "Requires macOS launcher")
    def test_fallback_rejects_untrusted_or_nonstable_release_redirect(self):
        for url in ("https://example.com/releases/tag/v0.0.31",
                    "https://github.com/pickrui/oixcloud-external-proxy-program/releases/tag/v0.0.32-beta",
                    "https://github.com/pickrui/oixcloud-external-proxy-program/releases/tag/v0.0.31/extra"):
            with self.subTest(url=url):
                result, urls = self.run_release_fixture(release_url=url)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertNotIn("download:", result.stdout)
                self.assertFalse(any(item.endswith("/SHA256SUMS") for item in urls))

    @unittest.skipUnless(sys.platform == "darwin", "Requires macOS launcher")
    def test_failed_fallback_download_does_not_install(self):
        result, _ = self.run_release_fixture(download_fails=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn("installed", result.stdout)

    def run_release_fixture(self, manifest=None, release_url=None, download_fails=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            calls = root / "urls"
            if manifest is None:
                manifest = "a" * 64 + "  oixcloud-external-proxy-program-arm64\n"
            if release_url is None:
                release_url = "https://github.com/pickrui/oixcloud-external-proxy-program/releases/tag/v0.0.31"
            stub = root / "curl"
            stub.write_text("#!" + sys.executable + "\n" + f"""
import pathlib, sys
url = sys.argv[-1]
with open({str(calls)!r}, "a") as out:
    out.write(url + "\\n")
if "api.github.com" in url:
    sys.exit(22)
if url.endswith("/releases/latest"):
    print({release_url!r}, end="")
elif url.endswith("/SHA256SUMS"):
    output = sys.argv[sys.argv.index("--output") + 1]
    pathlib.Path(output).write_text({manifest!r})
else:
    sys.exit(99)
""")
            stub.chmod(0o755)
            source = root / "launcher.command"
            source.write_text(SCRIPT.read_text().replace("/usr/bin/curl", self.shell_quote(str(stub))))
            command = f"""
              export OIX_LAUNCHER_SOURCE_ONLY=1
              source {self.shell_quote(str(source))}
              ASSET_NAME=oixcloud-external-proxy-program-arm64
              PROGRAM_PATH={self.shell_quote(str(root / 'program'))}
              TAG_FILE={self.shell_quote(str(root / 'version'))}
              log() {{ print -r -- "$*"; }}
              download_and_install() {{ print -r -- "download:$*"; return {1 if download_fails else 0}; }}
              ensure_installed_command() {{ print installed; }}
              update_if_needed
            """
            result = subprocess.run(["/bin/zsh", "-c", command], capture_output=True, text=True,
                                    timeout=10, env={**os.environ, "OIX_LAUNCHER_SOURCE_ONLY": "1", "TMPDIR": str(root)})
            self.assertEqual(list(root.glob("oixcloud-release.*")), [])
            self.assertEqual(list(root.glob("oixcloud-checksums.*")), [])
            return result, calls.read_text().splitlines() if calls.exists() else []

    @staticmethod
    def shell_quote(value):
        return "'" + value.replace("'", "'\"'\"'") + "'"


if __name__ == "__main__":
    unittest.main()
