#!/usr/bin/env python3
"""Validate metadata/wiki-structure.json for the repo-wiki pipeline."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


PAGE_TYPES = {
    "overview",
    "architecture",
    "concept",
    "lifecycle",
    "subsystem",
    "api",
    "extension",
    "configuration",
    "workflow",
    "development",
    "testing",
    "deployment",
    "reference",
}

CLASSIFICATION_FIELDS = {
    "primary_category",
    "secondary_categories",
    "architecture_style",
    "major_subsystems",
    "runtime_model",
    "public_surface_area",
    "developer_workflows",
    "extensibility_model",
}

PAGE_FIELDS = {"title", "type", "purpose", "answers", "source_hints", "children"}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def reject_markdown(raw: str, errors: list[str]) -> None:
    stripped = raw.strip()
    if not stripped:
        fail(errors, "file is empty")
        return
    if not stripped.startswith("{") or not stripped.endswith("}"):
        fail(errors, "root must be a JSON object; first non-space char must be '{' and last must be '}'")
    if re.search(r"(^|\n)```", raw):
        fail(errors, "must not contain fenced code blocks")
    if re.search(r"(^|\n)#{1,6}\s+", raw):
        fail(errors, "must not contain Markdown headings")
    if re.search(r"(^|\n)\s*-\s+\S+(\n\s+type:|\n\s+purpose:)", raw):
        fail(errors, "must not contain Markdown/YAML-style bullet catalog entries")


def parse_json(raw: str, errors: list[str]) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(errors, f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
        return None


def validate_string_list(value: Any, path: str, errors: list[str], *, allow_empty: bool = True) -> None:
    if not isinstance(value, list):
        fail(errors, f"{path} must be an array")
        return
    if not allow_empty and not value:
        fail(errors, f"{path} must not be empty")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            fail(errors, f"{path}[{index}] must be a non-empty string")


def source_hint_parent(hint: str) -> str:
    path_part = hint.split(" (", 1)[0].strip()
    glob_index = min([i for i in (path_part.find("*"), path_part.find("?")) if i >= 0], default=-1)
    if glob_index >= 0:
        slash_index = max(path_part.rfind("/", 0, glob_index), path_part.rfind("\\", 0, glob_index))
        return "." if slash_index < 0 else path_part[:slash_index]
    if path_part.endswith(("/", "\\")):
        return path_part.rstrip("/\\")
    parent = Path(path_part).parent.as_posix()
    return "." if parent == "." else parent


def validate_source_hints(hints: list[str], path: str, errors: list[str], repo_root: Path | None) -> None:
    for index, hint in enumerate(hints):
        if Path(hint.split(" (", 1)[0]).is_absolute():
            fail(errors, f"{path}[{index}] must be relative to the analyzed repository root")
            continue
        if repo_root is None:
            continue
        parent = source_hint_parent(hint)
        candidate = repo_root if parent == "." else repo_root / parent
        if not candidate.exists():
            fail(errors, f"{path}[{index}] parent path does not exist: {parent}")


def validate_page(page: Any, path: str, errors: list[str], repo_root: Path | None) -> None:
    if not isinstance(page, dict):
        fail(errors, f"{path} must be an object")
        return

    missing = sorted(PAGE_FIELDS - set(page))
    if missing:
        fail(errors, f"{path} missing required fields: {', '.join(missing)}")

    for field in ("title", "type", "purpose"):
        if field in page and (not isinstance(page[field], str) or not page[field].strip()):
            fail(errors, f"{path}.{field} must be a non-empty string")

    if isinstance(page.get("type"), str) and page["type"] not in PAGE_TYPES:
        fail(errors, f"{path}.type has invalid value: {page['type']}")

    if "answers" in page:
        validate_string_list(page["answers"], f"{path}.answers", errors, allow_empty=False)
        if isinstance(page["answers"], list) and len(page["answers"]) > 5:
            fail(errors, f"{path}.answers should contain 2-5 questions")

    if "source_hints" in page:
        validate_string_list(page["source_hints"], f"{path}.source_hints", errors, allow_empty=False)
        if isinstance(page["source_hints"], list):
            validate_source_hints(page["source_hints"], f"{path}.source_hints", errors, repo_root)

    children = page.get("children")
    if not isinstance(children, list):
        fail(errors, f"{path}.children must be an array")
        return
    for index, child in enumerate(children):
        validate_page(child, f"{path}.children[{index}]", errors, repo_root)


def validate_root(data: Any, errors: list[str], repo_root: Path | None) -> None:
    if not isinstance(data, dict):
        fail(errors, "root must be a JSON object")
        return

    classification = data.get("repository_classification")
    if not isinstance(classification, dict):
        fail(errors, "repository_classification must be an object")
    else:
        missing = sorted(CLASSIFICATION_FIELDS - set(classification))
        if missing:
            fail(errors, "repository_classification missing required fields: " + ", ".join(missing))

    structure = data.get("wiki_structure")
    if not isinstance(structure, list) or not structure:
        fail(errors, "wiki_structure must be a non-empty array")
        return

    for index, page in enumerate(structure):
        validate_page(page, f"wiki_structure[{index}]", errors, repo_root)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a repo wiki structure JSON file.")
    parser.add_argument("path", type=Path, help="Path to metadata/wiki-structure.json")
    parser.add_argument("--repo-root", type=Path, help="Analyzed repository root for source_hints checks")
    args = parser.parse_args()

    errors: list[str] = []
    raw = args.path.read_text(encoding="utf-8")
    reject_markdown(raw, errors)
    data = parse_json(raw, errors)
    if data is not None:
        validate_root(data, errors, args.repo_root)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
