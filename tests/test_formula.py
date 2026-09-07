from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
FORMULA = ROOT / "Formula" / "oixcloud-external-proxy-program.rb"
ALIAS = ROOT / "Aliases" / "oixcloud-helper"


class FormulaTest(unittest.TestCase):
    def test_formula_file_exists(self):
        self.assertTrue(FORMULA.exists(), f"Formula file not found at {FORMULA}")

    def test_alias_symlink_exists(self):
        self.assertTrue(ALIAS.is_symlink(), f"Alias at {ALIAS} is not a symlink")
        target = ALIAS.readlink()
        self.assertEqual(str(target), "../Formula/oixcloud-external-proxy-program.rb")
        self.assertTrue(ALIAS.resolve().exists(), f"Symlink target {ALIAS.resolve()} does not exist")

    def test_ruby_syntax_is_valid(self):
        result = subprocess.run(
            ["ruby", "-c", str(FORMULA)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, f"Ruby syntax check failed: {result.stderr}")
        self.assertIn("Syntax OK", result.stdout)

    def test_formula_structure_and_metadata(self):
        text = FORMULA.read_text(encoding="utf-8")

        self.assertIn("class OixcloudExternalProxyProgram < Formula", text)
        self.assertIn('homepage "https://github.com/pickrui/oixcloud-external-proxy-program"', text)
        self.assertIn("on_macos do", text)
        self.assertIn("if MacOS.version >= :sonoma", text)
        self.assertIn("on_arm do", text)
        self.assertIn("on_intel do", text)
        self.assertIn("oixcloud-external-proxy-program-legacy", text)
        self.assertIn('bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"', text)
        self.assertIn("service do", text)
        self.assertIn('run [opt_bin/"oixcloud-external-proxy-program", "--tray"]', text)
        self.assertIn("test do", text)
        self.assertIn('assert_match "oixcloud-external-proxy-program v#{version}", shell_output("#{bin}/oixcloud-external-proxy-program --version")', text)
        self.assertIn('assert_match "oixcloud-external-proxy-program v#{version}", shell_output("#{bin}/oixcloud-helper --version")', text)

    def test_checksums_and_version_format(self):
        text = FORMULA.read_text(encoding="utf-8")

        version_match = re.search(r'version "([0-9]+(?:\.[0-9]+)+)"', text)
        self.assertIsNotNone(version_match, "Valid version string not found in formula")

        sha256_matches = re.findall(r'sha256 "([0-9a-fA-F]{64})"', text)
        self.assertEqual(len(sha256_matches), 3, "Expected 3 sha256 checksums (arm64, intel, and legacy)")


if __name__ == "__main__":
    unittest.main()
