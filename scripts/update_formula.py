#!/usr/bin/env python3
"""Update the Homebrew formula from a verified stable GitHub release."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import urllib.request

REPO = "pickrui/oixcloud-external-proxy-program"
DEFAULT_FORMULA_PATH = Path(__file__).resolve().parents[1] / "Formula" / "oixcloud-external-proxy-program.rb"
ASSETS = tuple(f"oixcloud-external-proxy-program-{arch}" for arch in ("arm64", "amd64", "legacy"))
APP_ASSETS = tuple(f"oixcloud-helper-{arch}.zip" for arch in ("arm64", "amd64", "legacy"))
VERSION_PATTERN = r"(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){1,2}"


def normalize_tag(tag: str) -> str:
    if not isinstance(tag, str) or not re.fullmatch(rf"v?{VERSION_PATTERN}", tag):
        raise ValueError("Expected a stable numeric release tag, for example v0.0.31")
    return tag if tag.startswith("v") else f"v{tag}"


def validate_repo(repo: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+", repo) or repo.split("/")[1] in (".", ".."):
        raise ValueError("Expected a GitHub owner/repository")


def validate_sha256(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", value):
        raise ValueError("Invalid SHA-256 digest")
    return value.lower()


def get_current_formula_version(formula_path: Path) -> str:
    matches = re.findall(r'^\s*version "([^"\n]+)"\s*$', formula_path.read_text(encoding="utf-8"), re.MULTILINE)
    if len(matches) != 1:
        raise ValueError("Expected exactly one formula version")
    return normalize_tag(matches[0])[1:]


def download(url: str, *, limit: int, authenticated: bool = False) -> bytes:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "oixcloud-formula-updater"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if authenticated and token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read(limit + 1)
    if len(body) > limit:
        raise ValueError("Release response exceeds the size limit")
    return body


def fetch_release_metadata(repo: str, tag: str | None = None) -> dict:
    validate_repo(repo)
    suffix = f"tags/{normalize_tag(tag)}" if tag else "latest"
    release = json.loads(download(f"https://api.github.com/repos/{repo}/releases/{suffix}",
                                  limit=1024 * 1024, authenticated=True))
    if not isinstance(release, dict) or release.get("draft") or release.get("prerelease"):
        raise ValueError("Only published stable releases are supported")
    actual = normalize_tag(release.get("tag_name", ""))
    if not release["tag_name"].startswith("v") or (tag and actual != normalize_tag(tag)):
        raise ValueError("Release tag does not match the request")
    return release


def parse_sha256sums_content(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 2:
            raise ValueError("Malformed SHA256SUMS line")
        sha, filename = parts[0], parts[1].removeprefix("*")
        if not filename or filename in result:
            raise ValueError(f"Duplicate or empty checksum filename: {filename}")
        result[filename] = validate_sha256(sha)
    return result


def release_assets(release_data: dict, repo: str) -> dict[str, dict]:
    validate_repo(repo)
    tag = normalize_tag(release_data.get("tag_name", ""))
    assets = {}
    entries = release_data.get("assets", [])
    if not isinstance(entries, list):
        raise ValueError("Expected release assets to be a list")
    for asset in entries:
        if not isinstance(asset, dict):
            raise ValueError("Invalid release asset metadata")
        name = asset.get("name")
        if name not in (*ASSETS, *APP_ASSETS, "SHA256SUMS"):
            continue
        expected = f"https://github.com/{repo}/releases/download/{tag}/{name}"
        if name in assets or asset.get("browser_download_url") != expected:
            raise ValueError(f"Duplicate asset or unexpected download URL: {name}")
        assets[name] = asset
    missing = set((*ASSETS, "SHA256SUMS")) - assets.keys()
    if missing:
        raise ValueError(f"Missing release assets: {', '.join(sorted(missing))}")
    if set(APP_ASSETS) & assets.keys() and not set(APP_ASSETS) <= assets.keys():
        raise ValueError("Incomplete app bundle assets")
    return assets


def check_asset_digest(asset: dict, sha256: str) -> None:
    digest = asset.get("digest")
    if digest is None:
        return  # Older GitHub releases may not expose asset digests.
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise ValueError(f"Invalid GitHub asset digest: {asset['name']}")
    if validate_sha256(digest[7:]) != sha256:
        raise ValueError(f"GitHub asset digest disagrees with SHA256SUMS: {asset['name']}")


def fetch_sha256sums_from_release(release_data: dict, repo: str) -> dict[str, str]:
    assets = release_assets(release_data, repo)
    body = download(assets["SHA256SUMS"]["browser_download_url"], limit=64 * 1024)
    check_asset_digest(assets["SHA256SUMS"], hashlib.sha256(body).hexdigest())
    checksums = parse_sha256sums_content(body.decode("utf-8"))
    for name in (*ASSETS, *(name for name in APP_ASSETS if name in assets)):
        if name not in checksums:
            raise ValueError(f"Missing checksum: {name}")
        check_asset_digest(assets[name], checksums[name])
    return checksums


def update_formula_text(content: str, new_version: str, arm64_sha: str,
                        amd64_sha: str, legacy_sha: str, *, app_bundle: bool = False) -> str:
    version = normalize_tag(new_version)[1:]
    digests = [validate_sha256(value) for value in (arm64_sha, amd64_sha, legacy_sha)]
    versions = re.findall(r'^[ \t]*version "([^"\n]+)"', content, flags=re.MULTILINE)
    if len(versions) != 1:
        raise ValueError("Expected exactly one formula version")
    if normalize_tag(versions[0])[1:] != version:
        content = re.sub(r'^[ \t]*revision [0-9]+[ \t]*\n', '', content, flags=re.MULTILINE)
    elif app_bundle:
        previous_digests = {
            asset: digest.lower() for asset, digest in re.findall(
                r'^[ \t]*url "[^"\n]*/([^/"\n]+)"\n[ \t]*sha256 "([0-9a-fA-F]{64})"',
                content, flags=re.MULTILINE) if asset in APP_ASSETS
        }
        if previous_digests != dict(zip(APP_ASSETS, digests)):
            revision = re.search(r'^[ \t]*revision ([0-9]+)', content, flags=re.MULTILINE)
            next_revision = int(revision[1]) + 1 if revision else 1
            content = re.sub(r'^[ \t]*revision [0-9]+[ \t]*\n', '', content, flags=re.MULTILINE)
            content = re.sub(r'(^[ \t]*version "[^"\n]+"\n)',
                             lambda m: f'{m[1]}  revision {next_revision}\n', content, flags=re.MULTILINE)
    content = re.sub(r'(^[ \t]*version )"[^"\n]+"', lambda m: f'{m[1]}"{version}"',
                     content, flags=re.MULTILINE)
    if not app_bundle and any(asset in content for asset in APP_ASSETS):
        raise ValueError("Refusing to replace an app formula with standalone assets")
    if app_bundle:
        install_pattern = r'(?m)^([ \t]*)bin.install "oixcloud-external-proxy-program-(?:arm64|amd64|legacy)" => "oixcloud-external-proxy-program"$'
        content, count = re.subn(install_pattern, lambda m:
            f'{m[1]}(prefix/"oixCloud Helper.app").install "Contents"\n'
            f'{m[1]}bin.install_symlink prefix/"oixCloud Helper.app/Contents/MacOS/oixcloud-helper" => "oixcloud-external-proxy-program"', content)
        if count not in (0, 3) or content.count('(prefix/"oixCloud Helper.app").install "Contents"') != 3:
            raise ValueError("Expected three app installation blocks")
        for standalone, app in zip(ASSETS, APP_ASSETS):
            content = content.replace('/' + standalone + '"', '/' + app + '"')
    for asset, sha256 in zip(APP_ASSETS if app_bundle else ASSETS, digests):
        pattern = rf'(^[ \t]*url "[^"\n]*/{re.escape(asset)}"\n[ \t]*sha256 )"[^"\n]+"'
        content, count = re.subn(pattern, lambda m: f'{m[1]}"{sha256}"', content, flags=re.MULTILINE)
        if count != 1:
            raise ValueError(f"Expected exactly one formula URL/checksum for {asset}")
    return content


def version_tuple(version: str) -> tuple[int, ...]:
    parts = tuple(int(value) for value in normalize_tag(version)[1:].split("."))
    return parts + (0,) * (3 - len(parts))


def write_atomically(path: Path, text: str) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(text)
        temporary.chmod(path.stat().st_mode & 0o777)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=REPO)
    parser.add_argument("--tag", help="Specific stable release tag, or latest when omitted")
    parser.add_argument("--formula", type=Path, default=DEFAULT_FORMULA_PATH)
    parser.add_argument("--check", action="store_true", help="Check without changing the formula")
    args = parser.parse_args()
    try:
        validate_repo(args.repo)
        if args.tag:
            normalize_tag(args.tag)
        current_version = get_current_formula_version(args.formula)
        release = fetch_release_metadata(args.repo, args.tag)
        target_version = normalize_tag(release["tag_name"])[1:]
        if version_tuple(target_version) < version_tuple(current_version):
            raise ValueError(f"Refusing to downgrade {current_version} to {target_version}")
        checksums = fetch_sha256sums_from_release(release, args.repo)
        content = args.formula.read_text(encoding="utf-8")
        app_bundle = set(APP_ASSETS) <= release_assets(release, args.repo).keys()
        selected = APP_ASSETS if app_bundle else ASSETS
        updated = update_formula_text(content, target_version, *(checksums[name] for name in selected),
                                      app_bundle=app_bundle)
        if content == updated:
            print(f"Formula is already up to date: {target_version}")
        elif args.check:
            print(f"Update available: {current_version} -> {target_version}")
        else:
            write_atomically(args.formula, updated)
            print(f"Updated formula: {current_version} -> {target_version}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
