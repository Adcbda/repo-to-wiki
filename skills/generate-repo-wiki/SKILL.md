---
name: generate-repo-wiki
description: Generate a grounded DeepWiki-style wiki from a source repository. Use when Codex needs to read a repo, classify it, connect catalogs-prompts with contents-prompts, plan a conceptual wiki structure, select source evidence, draft cited Markdown pages, review them, and assemble wiki output.
---

# Generate Repo Wiki

## Overview

Use this skill to turn a local repository into a source-grounded engineering wiki. The workflow connects catalog prompts to content prompts through one contract: catalog pages define scope, mechanisms, source entities, outlines, and retrieval seeds; content generation turns those plans into verified evidence packs and cited pages.

Use the bundled prompts by default:

- `references/prompts/catalogs-prompts/`
- `references/prompts/contents-prompts/`

If the workspace also contains `catalogs-prompts/` or `contents-prompts/`, treat those as user-provided overrides for iterative prompt development. Otherwise, use the bundled prompt copies so the skill remains portable.

## One-Command Setup

Run the bundled preparer first:

```powershell
python <skill-dir>/scripts/prepare_wiki_run.py --repo <repo-root> --workspace <workspace-root>
```

Use Codex bundled Python if plain `python` is unavailable.

The script creates:

- `.wiki-run/<repo-name>/repository-context.json`
- `.wiki-run/<repo-name>/generation-state.json`
- `.wiki-run/<repo-name>/wiki-output/`
- `.wiki-run/<repo-name>/metadata/evidence/`

`repository-context.json` also records source-link metadata when available:

- `repository_metadata.source_link_base` for GitHub blob URLs pinned to the current commit
- `repository_metadata.source_link_strategy` for the fallback strategy
- `repository_metadata.root` for local `file:///` links when no remote source link base is available

Read `repository-context.json` before invoking prompts. It contains repository metadata, inventory, high-signal file excerpts, detected prompt paths, and suggested output paths.

## Workflow

1. Read repository context.
   - Use `prepare_wiki_run.py` output as the baseline.
   - Inspect extra files only when the prompt stage needs more evidence.
   - Keep all source paths relative to the analyzed repo root.

2. Classify the repository.
   - Run `references/prompts/catalogs-prompts/repository-classification-prompt.md`.
   - Inputs: metadata, inventory, source excerpts, README/docs/manifests/build config.
   - Output: primary category, secondary categories, architecture style, major subsystems, runtime model, public surface area, developer workflows, extensibility model.
   - Capture concrete repository vocabulary: public abstractions, runtime participants, commands, protocols, resource groups, generated/manual boundaries, extension points, package families, or product domains.

3. Generate and validate the catalog.
   - Assemble policy text from:
     - `references/prompts/catalogs-prompts/require-sections-prompt.md`
     - `references/prompts/catalogs-prompts/hierarchy-constraints-prompt.md`
     - `references/prompts/catalogs-prompts/anti-pattern-prompt.md`
   - Run `references/prompts/catalogs-prompts/catalogs-prompt.md`.
   - Require the model response to be raw JSON only: no Markdown headings, no bullet-list catalog, no code fences, no explanatory prose.
   - Save the raw response as `metadata/wiki-structure.raw.md` until it passes validation.
   - Validate that the JSON root has `repository_classification` and a non-empty `wiki_structure` array.
   - Validate that every page has `title`, `type`, `navigation_group`, `purpose`, `scope`, `primary_mechanisms`, `key_entities`, `page_outline`, `answers`, `source_hints`, and `children`.
   - Validate that the structure uses 2 levels maximum: top-level pages and child pages only.
   - Validate that the structure is not a shallow top-level-only catalog for medium or large repositories.
   - Require major architecture, runtime, public API, subsystem, and development areas to expand into child pages when the repository evidence supports them.
   - Reject FAQ-shaped catalogs: `answers` are acceptance checks, not the navigation model or future section headings.
   - Prefer repository-specific page titles and outlines over generic pages such as "Core Concepts", "API", "Configuration", and "Development".
   - Preserve conceptual pages; only downgrade or remove unverifiable source hints.
   - Write `metadata/wiki-structure.json` only after validation succeeds.

Run the bundled structure validator before using the catalog in later steps:

```powershell
python <skill-dir>/scripts/validate_wiki_structure.py <metadata/wiki-structure.json> --repo-root <repo-root>
```

If validation fails, keep the invalid raw response in `metadata/wiki-structure.raw.md`, pass the validation errors into one retry prompt, and run the validator again. Do not continue to content planning with an invalid or Markdown-formatted `wiki-structure.json`.

4. Build the content generation manifest.
   - Run `references/prompts/contents-prompts/content-generation-workflow-prompt.md`.
   - Inputs: repository metadata, classification, validated wiki structure, inventory, optional code knowledge context.
   - Output: parent-before-child page manifest with paths, scope, mechanisms, key entities, intent, evidence strategy, content shape, diagram candidates, and review focus.
   - Carry `scope`, `primary_mechanisms`, `key_entities`, and `page_outline` forward; do not reduce pages to their `answers`.

5. Generate each page.
   - For every page, run `references/prompts/contents-prompts/source-evidence-selection-prompt.md`.
   - Evidence selection must cover the page's `primary_mechanisms` and search for the declared `key_entities` when possible.
   - Save the source evidence selection output immediately as `metadata/evidence/<page-slug>.json`.
   - Treat this saved evidence pack as a hard prerequisite for page drafting. Do not draft or save a page when its evidence JSON is missing, invalid, or contains paths outside the repository inventory.
   - For `overview` pages, run `references/prompts/contents-prompts/overview-page-content-prompt.md`.
   - For all other pages, run `references/prompts/contents-prompts/page-content-prompt.md`.
   - Draft pages from `scope`, `page_outline`, evidence, and related pages. Do not use `answers` as headings or produce Q&A pages.
   - Pass the saved JSON as `{{SOURCE_EVIDENCE_PACK}}`; do not substitute `source_hints` or `evidence_strategy` for it.
   - Run `references/prompts/contents-prompts/diagram-generation-prompt.md` only for architecture, lifecycle, flow, API delegation, configuration, development, testing, or deployment pages where a diagram is evidenced.
   - Run `references/prompts/contents-prompts/page-review-prompt.md` and use `revised_page` as the saved Markdown.

6. Assemble the wiki.
   - Write pages under `.wiki-run/<repo-name>/wiki-output/pages/` or the user's requested `wiki/<repo-name>/` directory.
   - Save metadata beside the pages:
     - `metadata/repository.json`
     - `metadata/wiki-structure.json`
     - `metadata/wiki-structure.raw.md` only when a failed raw catalog response must be preserved for debugging
     - `metadata/generation-manifest.yaml`
     - `metadata/evidence/<page>.json`
   - Generate `index.md` from the overview page and navigation from the validated structure.
   - Page navigation links must point to the actual generated Markdown files:
     - From `index.md` to a page under `pages/`, use `pages/<page-slug>.md`.
     - From one file under `pages/` to another sibling page, use `<page-slug>.md`.
     - Do not use extensionless links such as `[Overview](overview)` unless a file or directory named `overview` actually exists at that relative path.

7. Run quality gates before final response.
   - `metadata/wiki-structure.json` parses as JSON.
   - `metadata/wiki-structure.json` contains no Markdown headings, bullet-list catalog entries, or fenced code blocks.
   - `metadata/wiki-structure.json` passes `validate_wiki_structure.py`.
   - No invented source hints or evidence paths.
   - No folder-mirror wiki structure.
   - No FAQ-shaped page catalog or page body.
   - Catalog pages include concrete scopes, mechanisms, key entities, and page outlines.
   - Medium and large repositories use repository-specific child pages for concrete mechanisms, API families, runtime phases, workflows, or responsibility boundaries.
   - Every substantive content section has `Sources:`.
   - Every cited evidence ID exists in that page evidence pack.
   - Every `Sources:` citation is a clickable Markdown link, not a bare evidence ID.
   - Every citation link points to the cited source file and includes the line range when known.
   - Diagrams cite evidence.
   - Links between generated pages resolve.

Run the bundled evidence validator after pages are written:

```powershell
python <skill-dir>/scripts/validate_wiki_evidence.py --repo <repo-root> --pages <pages-dir> --evidence <metadata/evidence-dir>
```

Run the bundled link validator after `index.md` and pages are assembled:

```powershell
python <skill-dir>/scripts/validate_wiki_links.py --wiki-output <wiki-output-dir>
```

If either validator fails, repair the broken evidence, citation, or navigation links before presenting the wiki as complete.

## Prompt Bridge

Use this bridge exactly:

```text
repository context
  -> repository classification
  -> catalog policies + catalogs-prompt
  -> validated wiki structure
  -> content-generation-workflow-prompt
  -> generation manifest
  -> source evidence selection per page
  -> page draft per page
  -> optional diagram patch
  -> page review
  -> assembled wiki
```

Do not treat catalog `source_hints` as citations. They are only retrieval seeds. Final page citations must come from per-page evidence packs.

## Catalog JSON Contract

Use this contract for `metadata/wiki-structure.json`:

1. The catalog output is JSON, not Markdown or YAML.
2. The root object contains `repository_classification` and `wiki_structure`.
3. `repository_classification` contains `primary_category`, `secondary_categories`, `architecture_style`, `major_subsystems`, `runtime_model`, `public_surface_area`, `developer_workflows`, and `extensibility_model`.
4. `wiki_structure` is a non-empty array of page objects.
5. Every page object contains `title`, `type`, `navigation_group`, `purpose`, `scope`, `primary_mechanisms`, `key_entities`, `page_outline`, `answers`, `source_hints`, and `children`.
6. `scope` defines what belongs on the page and what belongs elsewhere.
7. `primary_mechanisms` names the source-backed mechanisms, flows, API families, workflows, or responsibility areas the page explains.
8. `key_entities` names concrete repository vocabulary for retrieval: symbols, packages, commands, config keys, protocols, generated artifacts, runtime participants, resources, or product-domain terms.
9. `page_outline` lists future DeepWiki-style sections; it must not be a copied list of questions from `answers`.
10. `answers` are acceptance criteria only, not navigation labels or section headings.
11. `children` is always present; use `[]` for leaf pages.
12. Non-trivial repositories should not have every page as a top-level leaf.
13. The maximum hierarchy depth is 2; child pages must not contain grandchildren.
14. Medium and large repositories should include enough child pages to cover architecture, runtime flow, public API families, important subsystems, and developer workflows at wiki depth.
15. All `source_hints` are relative to the analyzed repository root.
16. `metadata/wiki-structure.json` is created only from validated JSON. Invalid raw model output belongs in `metadata/wiki-structure.raw.md`.

## Evidence Contract

Use this contract for every page:

1. `source_hints` from the catalog identify files, directories, globs, or symbols to inspect.
2. `scope`, `primary_mechanisms`, `key_entities`, and `page_outline` describe what evidence must explain.
3. `evidence_strategy` in the generation manifest describes retrieval intent.
4. `source-evidence-selection-prompt.md` produces the only valid citation namespace for the page.
5. Save that output to `metadata/evidence/<page-slug>.json` before drafting the page.
6. Page Markdown may cite only IDs present in its evidence JSON.
7. Page Markdown must render citations as clickable links in `Sources:` lines:
   - Preferred format when `repository_metadata.source_link_base` exists: `Sources: [S1](<source_link_base>/lib/app.js#L10-L25)`.
   - Fallback format when no remote source link base exists: `Sources: [S1](file:///C:/absolute/repo/lib/app.js#L10-L25)`.
   - If an evidence `line_range` is `unknown`, link to the file without a line fragment.
   - Do not emit bare citations such as `Sources: [S1] [S2]`.

The evidence JSON file name must match the Markdown page stem. For example, `pages/request-flow.md` requires `metadata/evidence/request-flow.json`.

Expected evidence JSON shape:

```json
{
  "page_title": "Request Flow",
  "page_type": "lifecycle",
  "evidence_summary": "...",
  "primary_evidence": [
    {
      "id": "S1",
      "path": "lib/application.js",
      "line_range": "150-180",
      "kind": "implementation",
      "symbols": ["app.handle"],
      "why_it_matters": "...",
      "key_facts": ["..."]
    }
  ],
  "secondary_evidence": [],
  "missing_or_replaced_hints": [],
  "open_questions": [],
  "recommended_queries": []
}
```

Never allow a page to rely only on `source_hints`, `evidence_strategy`, file excerpts, or model memory for `Sources: [Sx]`. Those inputs may guide retrieval, but only saved per-page evidence packs define valid citation IDs.

## Execution Rules

- Organize pages by mental model, architecture, runtime behavior, responsibilities, and developer workflows.
- Generate DeepWiki-style depth: grouped navigation, concrete child pages, and scale-sensitive breadth.
- Drive page planning through scope, mechanisms, key entities, and outlines. Use questions only as acceptance checks.
- Do not mirror the filesystem or create one page per file.
- Do not accept a flat top-level-only catalog for a repository with multiple subsystems or a substantial public surface area.
- Do not accept a wiki that reads like FAQ prompts instead of engineering pages.
- Prefer parent-before-child page drafting; sibling evidence selection and review may run in parallel.
- Use exact repository names, commands, symbols, and files only when observed.
- If evidence cannot answer a planned question, record the gap instead of inventing behavior.
- Keep generated content focused on helping an engineer understand the system.
- Do not call the wiki complete while `metadata/evidence/` is empty or has fewer JSON files than generated Markdown pages.
