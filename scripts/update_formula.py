#!/usr/bin/env python3
"""Automatically check and update the Homebrew formula for oixcloud-external-proxy-program."""

import argparse
import json
from pathlib import Path
import re
import sys
import urllib.request

REPO = "pickrui/oixcloud-external-proxy-program"
DEFAULT_FORMULA_PATH = Path(__file__).resolve().parents[1] / "Formula" / "oixcloud-external-proxy-program.rb"


def get_current_formula_version(formula_path: Path) -> str:
    content = formula_path.read_text(encoding="utf-8")
    match = re.search(r'version "([0-9]+(?:\.[0-9]+)+)"', content)
    if not match:
        raise ValueError(f"Could not find version string in {formula_path}")
    return match.group(1)


def fetch_release_metadata(repo: str, tag: str | None = None) -> dict:
    if tag:
        tag_name = tag if tag.startswith("v") else f"v{tag}"
        url = f"https://api.github.com/repos/{repo}/releases/tags/{tag_name}"
    else:
        url = f"https://api.github.com/repos/{repo}/releases/latest"

    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "oixcloud-formula-updater",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_sha256sums_content(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2 and len(parts[0]) == 64:
            sha, filename = parts[0], parts[1].lstrip("*")
            result[filename] = sha.lower()
    return result


def fetch_sha256sums_from_release(release_data: dict, repo: str) -> dict[str, str]:
    tag_name = release_data.get("tag_name", "")
    sha256sums_url = None
    for asset in release_data.get("assets", []):
        if asset.get("name") == "SHA256SUMS":
            sha256sums_url = asset.get("browser_download_url")
            break

    if not sha256sums_url and tag_name:
        sha256sums_url = f"https://github.com/{repo}/releases/download/{tag_name}/SHA256SUMS"

    if not sha256sums_url:
        raise ValueError(f"Could not find SHA256SUMS asset in release {tag_name}")

    req = urllib.request.Request(
        sha256sums_url,
        headers={"User-Agent": "oixcloud-formula-updater"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return parse_sha256sums_content(resp.read().decode("utf-8"))


def update_formula_text(
    content: str,
    new_version: str,
    arm64_sha: str,
    amd64_sha: str,
    legacy_sha: str,
) -> str:
    # 1. Update version
    content, n_ver = re.subn(r'version "[^"]+"', f'version "{new_version}"', content, count=1)
    if n_ver != 1:
        raise ValueError("Failed to replace version in formula")

    # 2. Update arm64 sha256
    content, n_arm = re.subn(
        r'(on_arm do\s+url [^\n]+\n\s+sha256 )"[^"]+"',
        rf'\1"{arm64_sha}"',
        content,
        count=1,
    )
    if n_arm != 1:
        raise ValueError("Failed to replace arm64 sha256 in formula")

    # 3. Update amd64/intel sha256
    content, n_amd = re.subn(
        r'(on_intel do\s+url [^\n]+\n\s+sha256 )"[^"]+"',
        rf'\1"{amd64_sha}"',
        content,
        count=1,
    )
    if n_amd != 1:
        raise ValueError("Failed to replace amd64 sha256 in formula")

    # 4. Update legacy sha256
    content, n_leg = re.subn(
        r'(oixcloud-external-proxy-program-legacy"\n\s+sha256 )"[^"]+"',
        rf'\1"{legacy_sha}"',
        content,
        count=1,
    )
    if n_leg != 1:
        raise ValueError("Failed to replace legacy sha256 in formula")

    return content


def main() -> int:
    parser = argparse.ArgumentParser(description="Update Homebrew formula for oixcloud-external-proxy-program")
    parser.add_argument("--repo", default=REPO, help="GitHub repository (owner/repo)")
    parser.add_argument("--tag", help="Specific release tag to update to (e.g. v0.0.30)")
    parser.add_argument("--formula", type=Path, default=DEFAULT_FORMULA_PATH, help="Path to formula file")
    parser.add_argument("--check", action="store_true", help="Only check for updates, do not write changes")
    args = parser.parse_args()

    formula_path = args.formula
    if not formula_path.exists():
        print(f"Error: Formula file not found: {formula_path}", file=sys.stderr)
        return 1

    current_version = get_current_formula_version(formula_path)
    print(f"Current formula version: {current_version}")

    print(f"Fetching latest release from {args.repo}...")
    try:
        release_data = fetch_release_metadata(args.repo, args.tag)
    except Exception as e:
        print(f"Error fetching release metadata: {e}", file=sys.stderr)
        return 1

    tag_name = release_data.get("tag_name", "")
    target_version = tag_name.lstrip("v")
    if not target_version:
        print("Error: Could not determine release version from tag", file=sys.stderr)
        return 1

    print(f"Target release version: {target_version} ({tag_name})")

    checksums = fetch_sha256sums_from_release(release_data, args.repo)
    arm64_sha = checksums.get("oixcloud-external-proxy-program-arm64")
    amd64_sha = checksums.get("oixcloud-external-proxy-program-amd64")
    legacy_sha = checksums.get("oixcloud-external-proxy-program-legacy")

    if not (arm64_sha and amd64_sha and legacy_sha):
        print(
            f"Error: Missing required asset checksums in release {tag_name}.\nFound: {checksums}",
            file=sys.stderr,
        )
        return 1

    print(f"Found checksums:\n  arm64:  {arm64_sha}\n  amd64:  {amd64_sha}\n  legacy: {legacy_sha}")

    content = formula_path.read_text(encoding="utf-8")
    updated_content = update_formula_text(
        content,
        target_version,
        arm64_sha,
        amd64_sha,
        legacy_sha,
    )

    if content == updated_content:
        print(f"Formula {formula_path.name} is already up to date with {target_version}.")
        return 0

    if args.check:
        print(f"Update available: {current_version} -> {target_version}")
        return 0

    formula_path.write_text(updated_content, encoding="utf-8")
    print(f"Successfully updated {formula_path} to {target_version}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
