# Repository-to-Wiki Generation Workflow

This document connects `catalogs-prompts/` and `contents-prompts/` into one complete DeepWiki-style generation pipeline.

The pipeline has two major phases:

1. Catalog phase: decide what pages should exist.
2. Content phase: generate grounded documentation for each page.

The most important rule is that the catalog phase organizes human understanding, while the content phase proves each page with source evidence.

## Inputs

The workflow starts from a local or cloned repository.

Required inputs:

- `repo_root`: absolute or workspace-relative repository path
- `repo_name`: display name, usually owner/repo or folder name
- `repo_inventory`: file list with paths, sizes, and optionally language/type classification
- `repo_summaries`: short summaries of important files, docs, manifests, entrypoints, tests, and examples
- `code_knowledge_context`: optional symbol graph, call graph, dependency graph, embeddings/RAG hits, or GitNexus query output

Recommended inventory fields:

```json
{
  "path": "src/example.ts",
  "kind": "source | test | docs | config | manifest | example | build | generated | asset",
  "language": "TypeScript",
  "size": 12345,
  "symbols": ["optional", "symbol", "names"]
}
```

## Phase 1: Repository Reading

Before running prompts, collect enough evidence to let the model reason about the system without reading every file in full.

Steps:

1. Build file inventory.
2. Detect repository metadata from README, manifests, package files, build files, docs, and top-level config.
3. Detect likely entrypoints, public exports, command definitions, server/runtime startup files, examples, and tests.
4. Produce short source summaries for high-signal files.
5. Keep all paths relative to `repo_root`.

Output:

```json
{
  "repository_metadata": {},
  "repository_file_inventory": [],
  "repository_source_summaries": [],
  "code_knowledge_context": {}
}
```

## Phase 2: Catalog Generation

The catalog phase determines the wiki table of contents. It must not write page content.

### Step 2.1 Repository Classification

Prompt:

- `catalogs-prompts/repository-classification-prompt.md`

Inputs:

- repository metadata
- file inventory
- source summaries
- README/docs excerpts
- manifests/build/config excerpts

Output:

```json
{
  "primary_category": "Developer Tooling",
  "secondary_categories": ["CLI Tool"],
  "architecture_style": "...",
  "major_subsystems": [],
  "runtime_model": "...",
  "public_surface_area": [],
  "developer_workflows": [],
  "extensibility_model": "..."
}
```

### Step 2.2 Section Policy Assembly

Prompts used as constraints:

- `catalogs-prompts/require-sections-prompt.md`
- `catalogs-prompts/hierarchy-constraints-prompt.md`
- `catalogs-prompts/anti-pattern-prompt.md`

These are not usually run as separate LLM calls. Treat them as policy text injected into the catalog generation call.

### Step 2.3 Wiki Structure Generation

Prompt:

- `catalogs-prompts/catalogs-prompt.md`

Inputs:

- repository classification
- repository metadata
- file inventory
- source summaries
- section policy text

Output:

```markdown
# Wiki Structure

- Overview
  type: overview
  purpose: ...
  answers:
    - ...
  source_hints:
    - README.md
```

### Step 2.4 Catalog Validation

Validate the structure before content generation:

- every page has `title`, `type`, `purpose`, `answers`, and `source_hints`
- every `source_hints` path is verified or downgraded to a verified parent directory/glob
- hierarchy is usually no deeper than 3 levels
- pages are conceptual, not folder mirrors
- page titles are stable enough to become links

Output:

```json
{
  "wiki_structure": {},
  "catalog_validation": {
    "status": "pass",
    "warnings": []
  }
}
```

## Phase 3: Content Planning

This phase turns the catalog into an executable page generation manifest.

Prompt:

- `contents-prompts/content-generation-workflow-prompt.md`

Inputs:

- repository metadata
- repository classification
- validated wiki structure
- file inventory
- code knowledge context

Output:

```yaml
generation_manifest:
  repository_name: "<name>"
  primary_category: "<category>"
  pages:
    - title: "Overview"
      type: "overview"
      path: "overview.md"
      parent: null
      intent: "..."
      must_answer:
        - "..."
      evidence_strategy:
        primary_hints:
          - "README.md"
        expand_to:
          - "docs"
          - "entrypoints"
      content_shape:
        required_sections:
          - "Purpose and Scope"
        diagram_candidates: []
      review_focus:
        - "..."
```

## Phase 4: Page Content Generation

Run this phase once per page.

Pages should be generated in parent-before-child order so child pages can reuse terminology from parent pages.

Safe parallelism:

- evidence selection can run in parallel for many pages
- content drafting can run in parallel for sibling pages after parent pages exist
- review can run in parallel per page
- final cross-link validation should run after all pages exist

### Step 4.1 Source Evidence Selection

Prompt:

- `contents-prompts/source-evidence-selection-prompt.md`

Inputs:

- repository root
- repository classification
- target page metadata
- parent/child/sibling metadata
- file inventory
- code knowledge context

Output:

```json
{
  "page_title": "Request Lifecycle",
  "page_type": "lifecycle",
  "evidence_summary": "...",
  "primary_evidence": [
    {
      "id": "S1",
      "path": "src/server.ts",
      "line_range": "12-80",
      "kind": "entrypoint",
      "symbols": ["startServer"],
      "why_it_matters": "...",
      "key_facts": []
    }
  ],
  "secondary_evidence": [],
  "missing_or_replaced_hints": [],
  "open_questions": [],
  "recommended_queries": []
}
```

### Step 4.2 Page Drafting

Use different prompts by page type:

- Overview page: `contents-prompts/overview-page-content-prompt.md`
- All other pages: `contents-prompts/page-content-prompt.md`

Inputs:

- repository metadata
- repository classification
- full wiki structure
- target page metadata
- parent/child/related page metadata
- source evidence pack
- existing wiki context from generated parent pages

Output:

```markdown
# Page Title

## Relevant source files
- `src/server.ts`

## Purpose and Scope
...
Sources: [S1]
```

### Step 4.3 Diagram Generation

Prompt:

- `contents-prompts/diagram-generation-prompt.md`

Run this only when the page describes architecture, lifecycle, data flow, request flow, rendering flow, API delegation, or development pipelines.

Output:

```json
{
  "diagrams": [
    {
      "insert_after_heading": "## Request Flow",
      "title": "Request Flow",
      "reason": "...",
      "mermaid": "flowchart TD\n  A --> B",
      "sources": ["S1", "S2"]
    }
  ],
  "no_diagram_reason": null
}
```

The caller inserts approved diagrams into the page draft.

### Step 4.4 Page Review

Prompt:

- `contents-prompts/page-review-prompt.md`

Inputs:

- repository classification
- full wiki structure
- target page metadata
- generated page draft
- source evidence pack
- related page metadata

Output:

```json
{
  "status": "pass",
  "findings": [],
  "missing_answers": [],
  "unsupported_claims": [],
  "revised_page": "# Page Title\n..."
}
```

If status is `needs_revision`, use `revised_page` as the next draft or run one more repair pass.

## Phase 5: Wiki Assembly

After all reviewed pages are generated:

1. Write pages to `wiki/<repo_name>/`.
2. Generate sidebar/navigation from validated wiki structure.
3. Convert source evidence IDs into source links when possible.
4. Resolve page links by title.
5. Generate an index page if the overview is not already the landing page.
6. Store machine-readable metadata beside the markdown.

Recommended output layout:

```text
wiki/<repo_name>/
  index.md
  pages/
    overview.md
    architecture.md
    request-lifecycle.md
  metadata/
    repository.json
    wiki-structure.json
    generation-manifest.yaml
    evidence/
      overview.json
      request-lifecycle.json
```

## Phase 6: Quality Gates

Run these checks before presenting the wiki:

- Catalog checks:
  - no invented source hints
  - no folder-mirror structure
  - page hierarchy is not too deep
  - every page has a distinct purpose

- Evidence checks:
  - every evidence path exists
  - every cited source ID exists in that page evidence pack
  - broad pages have enough evidence diversity
  - unsupported planned questions are reported

- Content checks:
  - every page has `Relevant source files`
  - every page has `Purpose and Scope`
  - every substantive section has `Sources:`
  - no unsupported architecture/runtime/API claims
  - no long code excerpts
  - diagrams cite evidence

- Navigation checks:
  - all page links resolve
  - child pages are linked from parent pages where useful
  - repeated explanations are minimized
  - terminology is consistent across pages

## Orchestrator Pseudocode

```pseudo
function generateWiki(repoRoot):
  repoContext = readRepository(repoRoot)

  classification = runPrompt(
    "catalogs-prompts/repository-classification-prompt.md",
    repoContext
  )

  catalogPolicies = concatenate(
    "catalogs-prompts/require-sections-prompt.md",
    "catalogs-prompts/hierarchy-constraints-prompt.md",
    "catalogs-prompts/anti-pattern-prompt.md"
  )

  wikiStructure = runPrompt(
    "catalogs-prompts/catalogs-prompt.md",
    repoContext + classification + catalogPolicies
  )

  validatedStructure = validateCatalog(wikiStructure, repoContext.fileInventory)

  generationManifest = runPrompt(
    "contents-prompts/content-generation-workflow-prompt.md",
    repoContext + classification + validatedStructure
  )

  pages = sortParentsBeforeChildren(generationManifest.pages)
  generatedPages = {}

  for page in pages:
    evidence = runPrompt(
      "contents-prompts/source-evidence-selection-prompt.md",
      repoContext + classification + page + relatedPageMetadata(page)
    )

    if page.type == "overview":
      draft = runPrompt(
        "contents-prompts/overview-page-content-prompt.md",
        repoContext + classification + validatedStructure + page + evidence
      )
    else:
      draft = runPrompt(
        "contents-prompts/page-content-prompt.md",
        repoContext + classification + validatedStructure + page + evidence + parentContext(page)
      )

    diagramPatch = runPrompt(
      "contents-prompts/diagram-generation-prompt.md",
      page + draft + evidence + relatedPageMetadata(page)
    )

    draftWithDiagrams = insertDiagrams(draft, diagramPatch)

    review = runPrompt(
      "contents-prompts/page-review-prompt.md",
      classification + validatedStructure + page + draftWithDiagrams + evidence
    )

    generatedPages[page.path] = review.revised_page
    saveEvidence(page.path, evidence)

  assembledWiki = assembleWiki(validatedStructure, generationManifest, generatedPages)
  qualityReport = runQualityGates(assembledWiki)

  return assembledWiki, qualityReport
```

## Practical Prompt Wiring

Use these variable names consistently across calls:

- `{{REPOSITORY_METADATA}}`
- `{{REPOSITORY_CLASSIFICATION}}`
- `{{WIKI_STRUCTURE}}`
- `{{PAGE_METADATA}}`
- `{{PARENT_PAGE_METADATA}}`
- `{{CHILD_PAGE_METADATA}}`
- `{{SIBLING_PAGE_METADATA}}`
- `{{RELATED_PAGE_METADATA}}`
- `{{REPOSITORY_FILE_INVENTORY}}`
- `{{SOURCE_EVIDENCE_PACK}}`
- `{{CODE_KNOWLEDGE_CONTEXT}}`
- `{{EXISTING_WIKI_CONTEXT}}`

The bridge between both prompt directories is:

```text
catalogs-prompts output
  -> validated wiki structure
  -> contents-prompts/content-generation-workflow-prompt.md
  -> generation manifest
  -> per-page evidence/content/review prompts
  -> final wiki pages
```

In other words, `source_hints` from the catalog phase are not final citations. They are retrieval seeds. The content phase must turn them into verified evidence packs before writing prose.
