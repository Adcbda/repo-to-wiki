#!/usr/bin/env python3
"""Prepare repository context for DeepWiki-style wiki generation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any


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

DOC_NAMES = {"readme", "contributing", "architecture", "design", "overview"}
MANIFEST_NAMES = {
    "package.json",
    "pyproject.toml",
    "go.mod",
    "cargo.toml",
    "pom.xml",
    "build.gradle",
    "settings.gradle",
    "requirements.txt",
    "gemfile",
    "composer.json",
    "mix.exs",
    "deno.json",
    "bun.lockb",
    "pnpm-lock.yaml",
    "yarn.lock",
}
CONFIG_SUFFIXES = {".toml", ".yaml", ".yml", ".json", ".ini", ".cfg"}
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


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def classify(path: Path) -> str:
    name = path.name.lower()
    suffix = path.suffix.lower()
    parts = {p.lower() for p in path.parts}
    stem = path.stem.lower()

    if stem in DOC_NAMES or suffix in {".md", ".mdx", ".rst", ".adoc"}:
        return "docs"
    if name in MANIFEST_NAMES:
        return "manifest"
    if suffix in CONFIG_SUFFIXES or name.startswith(".env"):
        return "config"
    if "test" in parts or "tests" in parts or name.startswith("test_") or name.endswith("_test.go"):
        return "test"
    if "example" in parts or "examples" in parts or "demo" in parts:
        return "example"
    if suffix in SOURCE_SUFFIXES:
        return "source"
    if suffix in {".lock", ".sum"}:
        return "lock"
    return "asset"


def language(path: Path) -> str | None:
    suffix = path.suffix.lower()
    mapping = {
        ".py": "Python",
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".go": "Go",
        ".rs": "Rust",
        ".java": "Java",
        ".kt": "Kotlin",
        ".cs": "C#",
        ".cpp": "C++",
        ".c": "C",
        ".h": "C/C++ Header",
        ".hpp": "C++ Header",
        ".rb": "Ruby",
        ".php": "PHP",
        ".swift": "Swift",
        ".scala": "Scala",
        ".ex": "Elixir",
        ".exs": "Elixir",
        ".clj": "Clojure",
        ".md": "Markdown",
        ".mdx": "MDX",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".toml": "TOML",
    }
    return mapping.get(suffix)


def should_skip_dir(path: Path) -> bool:
    return path.name in SKIP_DIRS


def safe_read_excerpt(path: Path, max_chars: int) -> str | None:
    try:
        if path.stat().st_size > 500_000:
            return None
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    text = text.replace("\r\n", "\n")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated]"


def file_sha1(path: Path) -> str | None:
    try:
        h = hashlib.sha1()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def build_inventory(repo: Path) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for current, dirnames, filenames in os.walk(repo):
        current_path = Path(current)
        dirnames[:] = [d for d in dirnames if not should_skip_dir(current_path / d)]
        for filename in filenames:
            path = current_path / filename
            try:
                stat = path.stat()
            except OSError:
                continue
            inventory.append(
                {
                    "path": rel(path, repo),
                    "kind": classify(path),
                    "language": language(path),
                    "size": stat.st_size,
                    "sha1": file_sha1(path),
                }
            )
    inventory.sort(key=lambda item: item["path"])
    return inventory


def select_excerpt_files(inventory: list[dict[str, Any]], limit: int) -> list[str]:
    priority = {"docs": 0, "manifest": 1, "config": 2, "source": 3, "test": 4, "example": 5}
    candidates = [
        item
        for item in inventory
        if item["kind"] in priority and item["size"] <= 200_000
    ]
    candidates.sort(key=lambda item: (priority[item["kind"]], item["path"].count("/"), item["path"]))
    return [item["path"] for item in candidates[:limit]]


def prompt_listing(root: Path, base: Path) -> list[str]:
    return sorted(rel(p, base) for p in root.glob("*.md")) if root.is_dir() else []


def detect_prompts(workspace: Path) -> dict[str, Any]:
    skill_root = Path(__file__).resolve().parents[1]
    bundled_catalogs = skill_root / "references" / "prompts" / "catalogs-prompts"
    bundled_contents = skill_root / "references" / "prompts" / "contents-prompts"
    catalogs = workspace / "catalogs-prompts"
    contents = workspace / "contents-prompts"
    return {
        "bundled_catalogs_prompts": prompt_listing(bundled_catalogs, skill_root),
        "bundled_contents_prompts": prompt_listing(bundled_contents, skill_root),
        "workspace_catalogs_prompts": prompt_listing(catalogs, workspace),
        "workspace_contents_prompts": prompt_listing(contents, workspace),
        "resolution": "Use workspace prompt files as overrides when present; otherwise use bundled prompt files.",
    }


def run_git(repo: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value or None


def github_blob_base(remote_url: str, commit: str | None) -> str | None:
    if not commit:
        return None

    url = remote_url.strip()
    if url.startswith("git@github.com:"):
        repo_part = url.removeprefix("git@github.com:")
    elif url.startswith("https://github.com/"):
        repo_part = url.removeprefix("https://github.com/")
    elif url.startswith("http://github.com/"):
        repo_part = url.removeprefix("http://github.com/")
    else:
        return None

    repo_part = repo_part.removesuffix(".git").strip("/")
    if repo_part.count("/") != 1:
        return None
    return f"https://github.com/{repo_part}/blob/{commit}"


def detect_source_links(repo: Path) -> dict[str, Any]:
    remote_url = run_git(repo, "remote", "get-url", "origin")
    commit = run_git(repo, "rev-parse", "HEAD")
    source_link_base = github_blob_base(remote_url, commit) if remote_url else None
    return {
        "git_remote_url": remote_url,
        "git_commit": commit,
        "source_link_base": source_link_base,
        "source_link_strategy": (
            "github_blob_with_line_fragments"
            if source_link_base
            else "local_file_uri_with_line_fragments"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare repository context for wiki generation.")
    parser.add_argument("--repo", required=True, help="Repository root to document.")
    parser.add_argument("--workspace", default=".", help="Workspace containing prompt directories.")
    parser.add_argument("--out", default=None, help="Output run directory. Defaults to <workspace>/.wiki-run/<repo-name>.")
    parser.add_argument("--excerpt-limit", type=int, default=40, help="Maximum high-signal file excerpts.")
    parser.add_argument("--max-excerpt-chars", type=int, default=8000, help="Maximum characters per excerpt.")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    workspace = Path(args.workspace).expanduser().resolve()
    if not repo.is_dir():
        raise SystemExit(f"Repository does not exist: {repo}")
    if not workspace.is_dir():
        raise SystemExit(f"Workspace does not exist: {workspace}")

    run_dir = Path(args.out).expanduser().resolve() if args.out else workspace / ".wiki-run" / repo.name
    metadata_dir = run_dir / "metadata"
    evidence_dir = metadata_dir / "evidence"
    pages_dir = run_dir / "wiki-output" / "pages"
    for directory in (metadata_dir, evidence_dir, pages_dir):
        directory.mkdir(parents=True, exist_ok=True)

    inventory = build_inventory(repo)
    excerpt_paths = select_excerpt_files(inventory, args.excerpt_limit)
    excerpts = []
    for path_text in excerpt_paths:
        excerpt = safe_read_excerpt(repo / path_text, args.max_excerpt_chars)
        if excerpt is not None:
            excerpts.append({"path": path_text, "excerpt": excerpt})

    context = {
        "repository_metadata": {
            "name": repo.name,
            "root": str(repo),
            "file_count": len(inventory),
            "kind_counts": {},
            **detect_source_links(repo),
        },
        "repository_file_inventory": inventory,
        "repository_source_summaries": excerpts,
        "prompt_paths": detect_prompts(workspace),
        "output_paths": {
            "run_dir": str(run_dir),
            "wiki_output": str(run_dir / "wiki-output"),
            "pages": str(pages_dir),
            "metadata": str(metadata_dir),
            "evidence": str(evidence_dir),
        },
        "code_knowledge_context": {},
    }

    counts: dict[str, int] = {}
    for item in inventory:
        counts[item["kind"]] = counts.get(item["kind"], 0) + 1
    context["repository_metadata"]["kind_counts"] = counts

    (run_dir / "repository-context.json").write_text(
        json.dumps(context, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (run_dir / "generation-state.json").write_text(
        json.dumps(
            {
                "status": "prepared",
                "next_step": "Run repository classification prompt, then catalog generation.",
                "repo": str(repo),
                "run_dir": str(run_dir),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": "prepared", "run_dir": str(run_dir)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
