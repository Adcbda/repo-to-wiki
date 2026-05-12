#!/usr/bin/env python3
"""Validate DeepWiki page citations against per-page evidence packs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote


SOURCE_ID_RE = re.compile(r"\[(S\d+)\]")
SOURCE_LINK_RE = re.compile(r"\[(S\d+)\]\(([^)]+)\)")
SOURCE_LINE_RE = re.compile(r"^Sources:\s*(.+)$", re.MULTILINE)
LINE_RANGE_RE = re.compile(r"^\s*(\d+)(?:-(\d+))?\s*$")


def slug_from_page_path(path: Path) -> str:
    return path.stem


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def evidence_items(pack: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for key in ("primary_evidence", "secondary_evidence"):
        value = pack.get(key, [])
        if not isinstance(value, list):
            raise ValueError(f"evidence field {key!r} must be a list")
        for item in value:
            if not isinstance(item, dict):
                raise ValueError(f"evidence field {key!r} contains a non-object item")
            items.append(item)
    return items


def cited_ids(markdown: str) -> set[str]:
    ids: set[str] = set()
    for match in SOURCE_LINE_RE.finditer(markdown):
        ids.update(SOURCE_ID_RE.findall(match.group(1)))
    return ids


def source_lines(markdown: str) -> list[str]:
    return [match.group(1) for match in SOURCE_LINE_RE.finditer(markdown)]


def linked_citations(markdown: str) -> dict[str, list[str]]:
    links: dict[str, list[str]] = {}
    for line in source_lines(markdown):
        for evidence_id, target in SOURCE_LINK_RE.findall(line):
            links.setdefault(evidence_id, []).append(target)
    return links


def normalize_link_target(target: str) -> str:
    target = target.strip().strip("<>")
    return unquote(target).replace("\\", "/")


def expected_line_fragments(line_range: Any) -> list[str]:
    if not isinstance(line_range, str):
        return []
    match = LINE_RANGE_RE.fullmatch(line_range)
    if not match:
        return []
    start = match.group(1)
    end = match.group(2) or start
    fragments = [f"#L{start}"]
    if end != start:
        fragments.append(f"#L{start}-L{end}")
    return fragments


def validate_link_target(page_name: str, evidence_id: str, target: str, item: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    normalized = normalize_link_target(target)
    evidence_path = str(item.get("path", "")).replace("\\", "/")
    if evidence_path and evidence_path not in normalized:
        errors.append(
            f"{page_name}: citation [{evidence_id}] link does not point to evidence path {evidence_path}: {target}"
        )

    fragments = expected_line_fragments(item.get("line_range"))
    if fragments and not any(fragment in normalized for fragment in fragments):
        errors.append(
            f"{page_name}: citation [{evidence_id}] link is missing line fragment for range {item.get('line_range')}: {target}"
        )
    return errors


def validate_page(page_path: Path, evidence_path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    if not evidence_path.is_file():
        return [f"{page_path.name}: missing evidence pack {evidence_path}"]

    markdown = page_path.read_text(encoding="utf-8", errors="replace")
    try:
        pack = load_json(evidence_path)
        if not isinstance(pack, dict):
            raise ValueError("evidence pack must be a JSON object")
        items = evidence_items(pack)
    except ValueError as exc:
        return [f"{page_path.name}: {exc}"]

    evidence_by_id: dict[str, dict[str, Any]] = {}
    for item in items:
        evidence_id = item.get("id")
        evidence_path_text = item.get("path")
        if not isinstance(evidence_id, str) or not SOURCE_ID_RE.fullmatch(f"[{evidence_id}]"):
            errors.append(f"{page_path.name}: evidence item has invalid id {evidence_id!r}")
            continue
        if evidence_id in evidence_by_id:
            errors.append(f"{page_path.name}: duplicate evidence id {evidence_id}")
        evidence_by_id[evidence_id] = item
        if not isinstance(evidence_path_text, str) or not evidence_path_text:
            errors.append(f"{page_path.name}: evidence {evidence_id} is missing path")
            continue
        if not (repo_root / evidence_path_text).exists():
            errors.append(f"{page_path.name}: evidence {evidence_id} path does not exist: {evidence_path_text}")

    ids = cited_ids(markdown)
    if "Sources:" in markdown and not ids:
        errors.append(f"{page_path.name}: has Sources lines but no [Sx] citations")

    links = linked_citations(markdown)
    for line in source_lines(markdown):
        bare_ids = set(SOURCE_ID_RE.findall(line))
        linked_ids = {evidence_id for evidence_id, _ in SOURCE_LINK_RE.findall(line)}
        for evidence_id in sorted(bare_ids - linked_ids):
            errors.append(f"{page_path.name}: citation [{evidence_id}] is not a clickable Markdown link")

    for evidence_id in sorted(ids):
        if evidence_id not in evidence_by_id:
            errors.append(f"{page_path.name}: citation [{evidence_id}] is missing from {evidence_path.name}")
        elif evidence_id not in links:
            errors.append(f"{page_path.name}: citation [{evidence_id}] is missing a Markdown link target")
        else:
            for target in links[evidence_id]:
                errors.extend(validate_link_target(page_path.name, evidence_id, target, evidence_by_id[evidence_id]))

    if not ids:
        errors.append(f"{page_path.name}: no Sources citations found")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate wiki pages against evidence JSON files.")
    parser.add_argument("--repo", required=True, help="Repository root used for evidence paths.")
    parser.add_argument("--pages", required=True, help="Directory containing generated Markdown pages.")
    parser.add_argument("--evidence", required=True, help="Directory containing per-page evidence JSON files.")
    args = parser.parse_args()

    repo_root = Path(args.repo).expanduser().resolve()
    pages_dir = Path(args.pages).expanduser().resolve()
    evidence_dir = Path(args.evidence).expanduser().resolve()

    if not repo_root.is_dir():
        raise SystemExit(f"Repository does not exist: {repo_root}")
    if not pages_dir.is_dir():
        raise SystemExit(f"Pages directory does not exist: {pages_dir}")
    if not evidence_dir.is_dir():
        raise SystemExit(f"Evidence directory does not exist: {evidence_dir}")

    errors: list[str] = []
    page_paths = sorted(p for p in pages_dir.glob("*.md") if p.is_file())
    if not page_paths:
        errors.append(f"No Markdown pages found in {pages_dir}")

    for page_path in page_paths:
        evidence_path = evidence_dir / f"{slug_from_page_path(page_path)}.json"
        errors.extend(validate_page(page_path, evidence_path, repo_root))

    extra_evidence = sorted(
        p.name for p in evidence_dir.glob("*.json") if pages_dir.joinpath(f"{p.stem}.md").is_file() is False
    )
    for name in extra_evidence:
        errors.append(f"{name}: evidence file has no matching page")

    if errors:
        print(json.dumps({"status": "fail", "errors": errors}, indent=2, ensure_ascii=False))
        return 1

    print(json.dumps({"status": "pass", "pages": len(page_paths)}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
