from pathlib import Path
import sys
import contextlib
import hashlib
import io
import re
import json
import tempfile
import subprocess
from unittest.mock import patch
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import update_formula

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
  revision 1
  license :cannot_represent

  on_macos do
    if MacOS.version >= :sonoma
      on_arm do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-external-proxy-program-arm64"
        sha256 "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

        def install
          bin.install "oixcloud-external-proxy-program-arm64" => "oixcloud-external-proxy-program"
          bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"
        end
      end

      on_intel do
        url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-external-proxy-program-amd64"
        sha256 "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

        def install
          bin.install "oixcloud-external-proxy-program-amd64" => "oixcloud-external-proxy-program"
          bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"
        end
      end
    else
      url "https://github.com/pickrui/oixcloud-external-proxy-program/releases/download/v#{version}/oixcloud-external-proxy-program-legacy"
      sha256 "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"

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
            "1111111111111111111111111111111111111111111111111111111111111111",
            "2222222222222222222222222222222222222222222222222222222222222222",
            "3333333333333333333333333333333333333333333333333333333333333333",
        )
        self.assertIn('version "0.0.31"', updated)
        self.assertNotIn('revision 1', updated)
        same_version = update_formula_text(sample_formula, "v0.0.30", "1" * 64, "2" * 64, "3" * 64)
        self.assertIn('revision 1', same_version)
        self.assertIn('sha256 "1111111111111111111111111111111111111111111111111111111111111111"', updated)
        self.assertIn('sha256 "2222222222222222222222222222222222222222222222222222222222222222"', updated)
        self.assertIn('sha256 "3333333333333333333333333333333333333333333333333333333333333333"', updated)
        self.assertNotIn("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", updated)
        self.assertNotIn("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", updated)
        self.assertNotIn("cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc", updated)


class ReleaseValidationTest(unittest.TestCase):
    def upgrade_tag(self):
        """A tag one patch above whatever the checked-in formula carries.

        Tests that feed the real formula in as their fixture cannot also pin a
        release tag: the moment the formula is bumped past it the fixture turns
        into a downgrade, which update_formula rightly refuses, and the test
        starts failing for a reason that has nothing to do with what it covers.
        """
        current = get_current_formula_version(update_formula.DEFAULT_FORMULA_PATH)
        parts = [int(part) for part in current.split(".")]
        parts[-1] += 1
        return "v" + ".".join(str(part) for part in parts)

    def release(self, tag="v0.0.35"):
        assets = []
        for index, name in enumerate(update_formula.ASSETS):
            assets.append({"name": name, "digest": "sha256:" + str(index + 1) * 64,
                           "browser_download_url": f"https://github.com/{update_formula.REPO}/releases/download/{tag}/{name}"})
        text = "".join(f"{asset['digest'][7:]}  {asset['name']}\n" for asset in assets).encode()
        assets.append({"name": "SHA256SUMS", "digest": "sha256:" + hashlib.sha256(text).hexdigest(),
                       "browser_download_url": f"https://github.com/{update_formula.REPO}/releases/download/{tag}/SHA256SUMS"})
        return {"tag_name": tag, "draft": False, "prerelease": False, "assets": assets}, text

    def test_app_release_switches_formula_without_changing_commands_or_services(self):
        release, _ = self.release()
        for name in update_formula.APP_ASSETS:
            release["assets"].append({"name": name, "digest": "sha256:" + "e" * 64,
                "browser_download_url": f"https://github.com/{update_formula.REPO}/releases/download/{release['tag_name']}/{name}"})
        manifest = next(asset for asset in release["assets"] if asset["name"] == "SHA256SUMS")
        body = "".join(f"{asset['digest'][7:]}  {asset['name']}\n" for asset in release["assets"]
                       if asset is not manifest).encode()
        manifest["digest"] = "sha256:" + hashlib.sha256(body).hexdigest()
        with patch.object(update_formula, "download", return_value=body):
            checksums = update_formula.fetch_sha256sums_from_release(release, update_formula.REPO)
        self.assertTrue(set(update_formula.APP_ASSETS) <= checksums.keys())
        formula = update_formula.DEFAULT_FORMULA_PATH.read_text()
        updated = update_formula.update_formula_text(formula, "99.0.0", *(["e" * 64] * 3), app_bundle=True)
        for name in update_formula.APP_ASSETS:
            self.assertIn('/' + name + '"', updated)
        self.assertEqual(updated.count('(prefix/"oixCloud Helper.app").install "Contents"'), 3)
        self.assertEqual(updated.count('bin.install_symlink bin/"oixcloud-external-proxy-program" => "oixcloud-helper"'), 3)
        self.assertIn('run [opt_bin/"oixcloud-external-proxy-program", "--tray"]', updated)
        self.assertEqual(updated, update_formula.update_formula_text(updated, "99.0.0", *(["e" * 64] * 3), app_bundle=True))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "app.rb"
            path.write_text(updated)
            subprocess.run(["ruby", "-c", str(path)], check=True, capture_output=True)
        with self.assertRaises(ValueError):
            update_formula.update_formula_text(updated, "99.0.1", *(["e" * 64] * 3))

    def test_same_version_app_migration_is_upgradeable_and_idempotent(self):
        formula = update_formula.DEFAULT_FORMULA_PATH.read_text()
        version = update_formula.get_current_formula_version(update_formula.DEFAULT_FORMULA_PATH)
        updated = update_formula.update_formula_text(formula, version, *(["e" * 64] * 3), app_bundle=True)
        before = re.search(r"revision ([0-9]+)", formula)
        expected = int(before[1]) + 1 if before else 1
        self.assertIn(f"revision {expected}", updated)
        self.assertEqual(updated, update_formula.update_formula_text(updated, version, *(["e" * 64] * 3), app_bundle=True))
        rebuilt = update_formula.update_formula_text(updated, version, *(["f" * 64] * 3), app_bundle=True)
        self.assertIn(f"revision {expected + 1}", rebuilt)

    def test_same_version_platform_digest_swap_increases_revision(self):
        formula = update_formula.DEFAULT_FORMULA_PATH.read_text()
        version = update_formula.get_current_formula_version(update_formula.DEFAULT_FORMULA_PATH)
        updated = update_formula.update_formula_text(formula, version, "a" * 64, "b" * 64, "c" * 64, app_bundle=True)
        revision = int(re.search(r"revision ([0-9]+)", updated)[1])
        swapped = update_formula.update_formula_text(updated, version, "b" * 64, "a" * 64, "c" * 64, app_bundle=True)
        self.assertIn(f"revision {revision + 1}", swapped)
        self.assertEqual(swapped, update_formula.update_formula_text(swapped, version, "b" * 64, "a" * 64, "c" * 64, app_bundle=True))

    def test_incomplete_app_release_is_rejected(self):
        release, _ = self.release()
        name = update_formula.APP_ASSETS[0]
        release["assets"].append({"name": name,
            "browser_download_url": f"https://github.com/{update_formula.REPO}/releases/download/{release['tag_name']}/{name}"})
        with self.assertRaises(ValueError):
            update_formula.release_assets(release, update_formula.REPO)

    def test_rejects_unsafe_tags_before_network_access(self):
        for tag in ['v1.2.3"; touch /tmp/invalid', "$(id)", "v1.2.3-beta", "../latest", "vv1.2.3"]:
            with self.subTest(tag=tag), patch.object(update_formula, "download") as network:
                with self.assertRaises(ValueError):
                    update_formula.fetch_release_metadata(update_formula.REPO, tag)
                network.assert_not_called()

    def test_rejects_draft_prerelease_and_mismatched_metadata(self):
        for edit in [{"draft": True}, {"prerelease": True}, {"tag_name": "v0.0.36"}]:
            release, _ = self.release()
            release.update(edit)
            with self.subTest(edit=edit), patch.object(update_formula, "download", return_value=json.dumps(release).encode()):
                with self.assertRaises(ValueError):
                    update_formula.fetch_release_metadata(update_formula.REPO, "v0.0.35")

    def test_checksums_reject_nonhex_duplicates_and_malformed_lines(self):
        for body in ["z" * 64 + "  binary", "a" * 64 + "  binary\n" + "b" * 64 + "  binary",
                     "a" * 64 + "  binary extra", "not-a-checksum"]:
            with self.subTest(body=body), self.assertRaises(ValueError):
                parse_sha256sums_content(body)

    def test_validates_manifest_and_all_binary_digests(self):
        release, body = self.release()
        with patch.object(update_formula, "download", return_value=body):
            self.assertEqual(len(update_formula.fetch_sha256sums_from_release(release, update_formula.REPO)), 3)
        for index in range(4):
            release, body = self.release()
            release["assets"][index]["digest"] = "sha256:" + "f" * 64
            with self.subTest(index=index), patch.object(update_formula, "download", return_value=body):
                with self.assertRaises(ValueError):
                    update_formula.fetch_sha256sums_from_release(release, update_formula.REPO)

    def test_rejects_missing_assets_and_untrusted_urls_before_download(self):
        for change in ["missing", "duplicate", "url"]:
            release, _ = self.release()
            if change == "missing":
                release["assets"].pop(0)
            elif change == "duplicate":
                release["assets"].append(dict(release["assets"][0]))
            else:
                release["assets"][-1]["browser_download_url"] = "https://example.invalid/SHA256SUMS"
            with self.subTest(change=change), patch.object(update_formula, "download") as network:
                with self.assertRaises(ValueError):
                    update_formula.fetch_sha256sums_from_release(release, update_formula.REPO)
                network.assert_not_called()

    def test_missing_or_duplicate_formula_asset_is_not_partially_rewritten(self):
        content = update_formula.DEFAULT_FORMULA_PATH.read_text()
        malformed = content.replace("-legacy\"", "-missing\"")
        for text in [malformed, content + content]:
            with self.assertRaises(ValueError):
                update_formula_text(text, "0.0.32", "1" * 64, "2" * 64, "3" * 64)

    def test_check_mode_and_failed_release_keep_formula_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            formula = Path(directory) / "formula.rb"
            original = update_formula.DEFAULT_FORMULA_PATH.read_text()
            formula.write_text(original)
            release, body = self.release(self.upgrade_tag())
            for check, fail in [(True, False), (False, True)]:
                argv = ["update_formula.py", "--formula", str(formula)] + (["--check"] if check else [])
                with patch.object(sys, "argv", argv), patch.object(update_formula, "fetch_release_metadata", return_value=release), \
                     patch.object(update_formula, "download", side_effect=OSError("unavailable") if fail else None, return_value=body), \
                     contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(update_formula.main(), 1 if fail else 0)
                self.assertEqual(formula.read_text(), original)

    def test_rejects_downgrade_without_fetching_checksums(self):
        with tempfile.TemporaryDirectory() as directory:
            formula = Path(directory) / "formula.rb"
            formula.write_text('version "0.0.31"\n')
            release, _ = self.release("v0.0.30")
            with patch.object(sys, "argv", ["update_formula.py", "--formula", str(formula)]), \
                 patch.object(update_formula, "fetch_release_metadata", return_value=release), \
                 patch.object(update_formula, "fetch_sha256sums_from_release") as checksums, \
                 contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(update_formula.main(), 1)
                checksums.assert_not_called()
            self.assertEqual(formula.read_text(), 'version "0.0.31"\n')

    def test_atomic_write_preserves_original_when_replace_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "formula.rb"
            path.write_text("original")
            with patch.object(Path, "replace", side_effect=OSError("denied")), self.assertRaises(OSError):
                update_formula.write_atomically(path, "new")
            self.assertEqual(path.read_text(), "original")
            self.assertEqual(list(Path(directory).iterdir()), [path])


if __name__ == "__main__":
    unittest.main()
