#!/usr/bin/env python3
"""Validate metadata/wiki-structure.json for the repo-wiki pipeline."""

from __future__ import annotations

import argparse
import json
import os
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

PAGE_FIELDS = {
    "title",
    "type",
    "navigation_group",
    "purpose",
    "scope",
    "primary_mechanisms",
    "key_entities",
    "page_outline",
    "answers",
    "source_hints",
    "children",
}

GENERIC_TITLE_WORDS = {
    "api",
    "apis",
    "architecture",
    "concept",
    "concepts",
    "configuration",
    "debugging",
    "development",
    "examples",
    "extension",
    "extensions",
    "overview",
    "reference",
    "system",
}

GENERIC_EXACT_TITLES = {
    "api",
    "architecture",
    "configuration",
    "core concepts",
    "debugging",
    "development",
    "development and debugging",
    "error handling",
    "examples",
    "extension mechanism",
    "extensions",
    "public api",
    "public apis",
    "reference",
    "request api",
    "response api",
    "subsystems",
}

QUESTION_HEADING_RE = re.compile(
    r"^\s*(what|why|how|when|where|which|who|can|does|do|is|are)\b", re.IGNORECASE
)

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".wiki-run",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "target",
    ".next",
    ".turbo",
    ".cache",
}

SOURCE_SUFFIXES = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".cs",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".rb",
    ".php",
    ".swift",
    ".scala",
    ".ex",
    ".exs",
    ".clj",
}


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


def normalized_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def is_generic_title(title: str) -> bool:
    normalized = normalized_text(title)
    if normalized in GENERIC_EXACT_TITLES:
        return True
    words = set(re.findall(r"[a-z0-9]+", normalized))
    if not words:
        return False
    return words.issubset(GENERIC_TITLE_WORDS)


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

    for field in ("title", "type", "navigation_group", "purpose", "scope"):
        if field in page and (not isinstance(page[field], str) or not page[field].strip()):
            fail(errors, f"{path}.{field} must be a non-empty string")

    if isinstance(page.get("type"), str) and page["type"] not in PAGE_TYPES:
        fail(errors, f"{path}.type has invalid value: {page['type']}")

    if "answers" in page:
        validate_string_list(page["answers"], f"{path}.answers", errors, allow_empty=False)
        if isinstance(page["answers"], list) and not 2 <= len(page["answers"]) <= 5:
            fail(errors, f"{path}.answers should contain 2-5 questions")

    if "primary_mechanisms" in page:
        validate_string_list(page["primary_mechanisms"], f"{path}.primary_mechanisms", errors, allow_empty=False)
        if isinstance(page["primary_mechanisms"], list) and len(page["primary_mechanisms"]) > 8:
            fail(errors, f"{path}.primary_mechanisms should contain 1-8 mechanisms")

    if "key_entities" in page:
        validate_string_list(page["key_entities"], f"{path}.key_entities", errors, allow_empty=False)
        if isinstance(page["key_entities"], list) and len(page["key_entities"]) > 12:
            fail(errors, f"{path}.key_entities should contain 1-12 source-backed terms")

    if "page_outline" in page:
        validate_string_list(page["page_outline"], f"{path}.page_outline", errors, allow_empty=False)
        if isinstance(page["page_outline"], list):
            if len(page["page_outline"]) < 3:
                fail(errors, f"{path}.page_outline should contain at least 3 planned sections")
            if len(page["page_outline"]) > 10:
                fail(errors, f"{path}.page_outline should contain no more than 10 planned sections")
            answers = {
                normalized_text(answer.rstrip("?"))
                for answer in page.get("answers", [])
                if isinstance(answer, str)
            }
            for index, heading in enumerate(page["page_outline"]):
                if not isinstance(heading, str):
                    continue
                normalized_heading = normalized_text(heading.rstrip("?"))
                if heading.strip().endswith("?") or QUESTION_HEADING_RE.search(heading):
                    fail(errors, f"{path}.page_outline[{index}] must be a section heading, not a question")
                if normalized_heading in answers:
                    fail(errors, f"{path}.page_outline[{index}] must not duplicate an answers question")

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


def collect_page_stats(structure: list[Any]) -> dict[str, int]:
    stats = {
        "total_pages": 0,
        "top_level_pages": len(structure),
        "child_pages": 0,
        "branch_pages": 0,
        "max_depth": 0,
    }

    def walk(page: Any, depth: int) -> None:
        if not isinstance(page, dict):
            return
        stats["total_pages"] += 1
        stats["max_depth"] = max(stats["max_depth"], depth)
        if depth > 1:
            stats["child_pages"] += 1
        children = page.get("children")
        if isinstance(children, list) and children:
            stats["branch_pages"] += 1
            for child in children:
                walk(child, depth + 1)

    for page in structure:
        walk(page, 1)
    return stats


def flatten_pages(structure: list[Any]) -> list[tuple[dict[str, Any], int]]:
    pages: list[tuple[dict[str, Any], int]] = []

    def walk(page: Any, depth: int) -> None:
        if not isinstance(page, dict):
            return
        pages.append((page, depth))
        children = page.get("children")
        if isinstance(children, list):
            for child in children:
                walk(child, depth + 1)

    for page in structure:
        walk(page, 1)
    return pages


def repo_complexity(repo_root: Path | None) -> dict[str, int]:
    counts = {"total_files": 0, "source_files": 0}
    if repo_root is None or not repo_root.is_dir():
        return counts

    for current, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        counts["total_files"] += len(filenames)
        for filename in filenames:
            if Path(filename).suffix.lower() in SOURCE_SUFFIXES:
                counts["source_files"] += 1
    return counts


def validate_information_architecture(
    structure: list[Any], errors: list[str], repo_root: Path | None
) -> None:
    stats = collect_page_stats(structure)
    pages = flatten_pages(structure)
    complexity = repo_complexity(repo_root)
    source_files = complexity["source_files"]
    total_files = complexity["total_files"]

    if stats["max_depth"] > 2:
        fail(errors, "wiki_structure must use 2 levels maximum; child pages must not contain grandchildren")

    if stats["total_pages"] >= 8 and stats["child_pages"] == 0:
        fail(errors, "wiki_structure is too flat: non-trivial catalogs must include child pages")

    if stats["total_pages"] >= 10 and stats["branch_pages"] < 2:
        fail(errors, "wiki_structure needs at least two parent sections with children at this size")

    if stats["total_pages"] >= 12 and stats["top_level_pages"] * 10 > stats["total_pages"] * 8:
        fail(errors, "wiki_structure is too top-heavy: group related pages under parent sections")

    generic_pages = [
        page.get("title", "")
        for page, depth in pages
        if depth > 1 and isinstance(page.get("title"), str) and is_generic_title(page["title"])
    ]
    if stats["child_pages"] >= 4 and len(generic_pages) * 2 > stats["child_pages"]:
        fail(
            errors,
            "too many child pages have generic titles; use repository-specific mechanisms, APIs, workflows, or runtime phases",
        )

    generic_leaf_pages = [
        page.get("title", "")
        for page, _depth in pages
        if isinstance(page.get("title"), str)
        and is_generic_title(page["title"])
        and not page.get("children")
        and normalized_text(page["title"]) != "overview"
    ]
    if stats["total_pages"] >= 10 and len(generic_leaf_pages) * 5 > stats["total_pages"] * 2:
        fail(
            errors,
            "too many leaf pages are generic documentation categories; leaf pages should explain concrete mechanisms",
        )

    if source_files >= 100 or total_files >= 250:
        if stats["total_pages"] < 18:
            fail(errors, "large repositories should usually plan at least 18 wiki pages")
        if stats["branch_pages"] < 4:
            fail(errors, "large repositories should include at least four parent sections with children")
        if stats["child_pages"] < 8:
            fail(errors, "large repositories should include at least eight child pages")
        if stats["max_depth"] < 2:
            fail(errors, "large repositories need grouped navigation with child pages")
    elif source_files >= 25 or total_files >= 75:
        if stats["total_pages"] < 10:
            fail(errors, "medium repositories should usually plan at least 10 wiki pages")
        if stats["branch_pages"] < 2:
            fail(errors, "medium repositories should include at least two parent sections with children")
        if stats["child_pages"] < 3:
            fail(errors, "medium repositories should include several child pages for wiki-level depth")


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

    validate_information_architecture(structure, errors, repo_root)


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
