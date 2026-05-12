#!/usr/bin/env python3
"""Validate local Markdown links in generated wiki output."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse


MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
EXTERNAL_SCHEMES = {
    "http",
    "https",
    "mailto",
    "file",
    "ftp",
    "ftps",
    "data",
    "javascript",
}


def split_target(target: str) -> tuple[str, str]:
    target = target.strip().strip("<>")
    path, separator, fragment = target.partition("#")
    return unquote(path), fragment if separator else ""


def is_external_target(target: str) -> bool:
    parsed = urlparse(target.strip().strip("<>"))
    return parsed.scheme.lower() in EXTERNAL_SCHEMES


def markdown_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def validate_file(path: Path, wiki_root: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")

    for match in MARKDOWN_LINK_RE.finditer(text):
        label = match.group(1)
        target = match.group(2)
        if is_external_target(target):
            continue

        link_path, _fragment = split_target(target)
        if not link_path:
            continue

        if re.match(r"^[A-Za-z]:[\\/]", link_path) or link_path.startswith(("/", "\\")):
            resolved = Path(link_path)
        else:
            resolved = (path.parent / link_path).resolve()

        if not resolved.exists():
            display_path = path.relative_to(wiki_root).as_posix()
            errors.append(f"{display_path}: unresolved local link [{label}]({target})")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate generated wiki Markdown links.")
    parser.add_argument("--wiki-output", required=True, help="Directory containing index.md and pages/.")
    args = parser.parse_args()

    wiki_root = Path(args.wiki_output).expanduser().resolve()
    if not wiki_root.is_dir():
        raise SystemExit(f"Wiki output directory does not exist: {wiki_root}")

    errors: list[str] = []
    files = markdown_files(wiki_root)
    if not files:
        errors.append(f"No Markdown files found in {wiki_root}")

    for path in files:
        errors.extend(validate_file(path, wiki_root))

    if errors:
        print(json.dumps({"status": "fail", "errors": errors}, indent=2, ensure_ascii=False))
        return 1

    print(json.dumps({"status": "pass", "files": len(files)}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
