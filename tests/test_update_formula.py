from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from update_formula import (
    get_current_formula_version,
    parse_sha256sums_content,
    update_formula_text,
)


class UpdateFormulaTest(unittest.TestCase):
    def setUp(self):
        self.formula_path = ROOT / "Formula" / "oixcloud-external-proxy-program.rb"

    def test_get_current_formula_version(self):
        version = get_current_formula_version(self.formula_path)
        self.assertRegex(version, r"^[0-9]+(\.[0-9]+)+$")

    def test_parse_sha256sums_content(self):
        text = """
30fc2e5c8c4cafa049d4a283bc6444123adf38bda304ff4d8c4af9f0005d16d3  oixcloud-external-proxy-program-arm64
6cfa1e5e3ab71443a34d2dc9e523d783b4737a32d0d71db665b39b891a95e8d6  oixcloud-external-proxy-program-amd64
afd585202b9e55ce361774c66e267e15c2d9f447767c7fa34f262655b8129269  oixcloud-external-proxy-program-legacy
"""
        sums = parse_sha256sums_content(text)
        self.assertEqual(
            sums["oixcloud-external-proxy-program-arm64"],
            "30fc2e5c8c4cafa049d4a283bc6444123adf38bda304ff4d8c4af9f0005d16d3",
        )
        self.assertEqual(
            sums["oixcloud-external-proxy-program-amd64"],
            "6cfa1e5e3ab71443a34d2dc9e523d783b4737a32d0d71db665b39b891a95e8d6",
        )
        self.assertEqual(
            sums["oixcloud-external-proxy-program-legacy"],
            "afd585202b9e55ce361774c66e267e15c2d9f447767c7fa34f262655b8129269",
        )

    def test_update_formula_text(self):
        sample_formula = """class OixcloudExternalProxyProgram < Formula
  desc "Connect oixCloud nodes to Surge, or build a DHCP/DNS gateway with OpenSurge"
  homepage "https://github.com/pickrui/oixcloud-external-proxy-program"
  version "0.0.30"
  license :cannot_represent

  on_macos do
    if MacOS.version >= :sonoma
      on_arm do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-external-proxy-program-arm64"
        sha256 "old_arm_sha"

        def install
          bin.install "oixcloud-external-proxy-program-arm64" => "oixcloud-external-proxy-program"
          bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"
        end
      end

      on_intel do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-external-proxy-program-amd64"
        sha256 "old_amd_sha"

        def install
          bin.install "oixcloud-external-proxy-program-amd64" => "oixcloud-external-proxy-program"
          bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"
        end
      end
    else
      url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-external-proxy-program-legacy"
      sha256 "old_legacy_sha"

      def install
        bin.install "oixcloud-external-proxy-program-legacy" => "oixcloud-external-proxy-program"
        bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"
      end
    end
  end
end
"""
        updated = update_formula_text(
            sample_formula,
            "0.0.31",
            "new_arm_sha",
            "new_amd_sha",
            "new_legacy_sha",
        )
        self.assertIn('version "0.0.31"', updated)
        self.assertIn('sha256 "new_arm_sha"', updated)
        self.assertIn('sha256 "new_amd_sha"', updated)
        self.assertIn('sha256 "new_legacy_sha"', updated)
        self.assertNotIn("old_arm_sha", updated)
        self.assertNotIn("old_amd_sha", updated)
        self.assertNotIn("old_legacy_sha", updated)


if __name__ == "__main__":
    unittest.main()
