from pathlib import Path
import re
import unittest
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    ROOT / "README.md",
    ROOT / "docs" / "configuration.md",
    ROOT / "docs" / "docker.md",
    ROOT / "docs" / "troubleshooting.md",
]
LINK_PATTERN = re.compile(r"\[[^]]+\]\(([^)]+)\)")


class DocumentationTest(unittest.TestCase):
    def test_readme_stays_a_short_entry_point(self):
        lines = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(len(lines), 200)

    def test_chinese_docs_have_no_full_stop(self):
        for path in DOCS:
            self.assertNotIn("。", path.read_text(encoding="utf-8"), path)

    def test_relative_links_exist(self):
        for path in DOCS:
            text = path.read_text(encoding="utf-8")
            for target in LINK_PATTERN.findall(text):
                file_target = unquote(target.split("#", 1)[0])
                if not file_target or "://" in file_target:
                    continue
                linked = (path.parent / file_target).resolve()
                self.assertTrue(linked.exists(), f"{path}: missing {target}")

    def test_code_fences_are_balanced(self):
        for path in DOCS:
            fences = sum(line.startswith("```") for line in path.read_text(encoding="utf-8").splitlines())
            self.assertEqual(fences % 2, 0, path)

    def test_docker_deployment_uses_latest_without_dead_port_environment(self):
        compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
        all_text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS) + compose
        self.assertIn("ghcr.io/pickrui/oixcloud-external-proxy-program:latest", compose)
        self.assertNotRegex(all_text, r"ghcr\.io/pickrui/oixcloud-external-proxy-program:v\d")
        self.assertNotIn("OIXCLOUD_SERVE_PORT", compose)


if __name__ == "__main__":
    unittest.main()
