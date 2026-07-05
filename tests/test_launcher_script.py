from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "启动 oixCloud.command"


class LauncherScriptTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
