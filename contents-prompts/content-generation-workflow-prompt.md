You are designing the content generation phase for a DeepWiki-style repository wiki.

The catalog phase has already produced a conceptual wiki structure. Your task is to turn each page plan into grounded documentation content.

Do not write final page content in this prompt. Instead, plan the generation workflow and specify the execution order for downstream prompts.

Inputs:
- Repository metadata:
  {{REPOSITORY_METADATA}}
- Repository classification:
  {{REPOSITORY_CLASSIFICATION}}
- Wiki structure from the catalog phase:
  {{WIKI_STRUCTURE}}
- Repository file inventory:
  {{REPOSITORY_FILE_INVENTORY}}
- Optional code index, symbol graph, dependency graph, or search results:
  {{CODE_KNOWLEDGE_CONTEXT}}

Goal:
Generate a reliable page-by-page content plan that can be executed by an LLM, code index, or retrieval pipeline.

Plan these downstream stages for every page:

1. Page intent extraction
   - Read the page title, type, purpose, answers, source_hints, parent page, child pages, and sibling pages.
   - Decide what engineering question the page must answer.
   - Identify whether the page needs conceptual explanation, runtime flow, API reference, configuration behavior, developer workflow, or source navigation guidance.

2. Evidence selection
   - Specify how the downstream source evidence selection prompt should be run for the page.
   - Start from verified source_hints.
   - Expand to nearby tests, examples, configuration files, documentation, entrypoints, public exports, and implementation files when they are relevant.
   - Do not invent files or symbols.

3. Page drafting
   - Specify how the downstream DeepWiki page content prompt should use the selected evidence pack.
   - Write a focused page, not a file summary.
   - Use clickable source citations for every architectural, behavioral, lifecycle, or API claim.
   - Prefer repository remote links from `repository_metadata.source_link_base`; otherwise use local file URI links built from `repository_metadata.root`.
   - Prefer tables and concise diagrams where they reduce cognitive load.

4. Diagram generation
   - If the page describes architecture, lifecycle, control flow, data flow, request flow, rendering flow, package relationships, or API delegation, plan a downstream diagram prompt run.
   - Insert only diagrams that are supported by evidence.
   - Avoid diagrams for simple reference pages where prose or tables are clearer.

5. Page review
   - Specify how the downstream page review prompt should be run.
   - Remove unsupported claims.
   - Fix weak structure.
   - Verify that the page answers its planned questions.
   - Verify that every source citation maps to provided evidence and is a clickable Markdown link.

6. Cross-page consistency
   - Ensure that the page uses the same terminology as parent, child, and sibling pages.
   - Add cross-links to related wiki pages when they help navigation.
   - Avoid repeating long explanations that belong on a parent or dedicated child page.

Output:
Return a generation manifest in this format:

```yaml
generation_manifest:
  repository_name: "<name>"
  primary_category: "<category>"
  pages:
    - title: "<page title>"
      type: "<page type>"
      path: "<suggested wiki output path>"
      parent: "<parent title or null>"
      intent: "<one sentence>"
      must_answer:
        - "<question>"
      evidence_strategy:
        primary_hints:
          - "<verified source hint>"
        expand_to:
          - "<docs | tests | examples | config | entrypoints | public exports | implementation | generated types>"
        retrieval_queries:
          - "<query or symbol search>"
      content_shape:
        required_sections:
          - "<section>"
        optional_sections:
          - "<section>"
        diagram_candidates:
          - type: "<flowchart | sequence | class | graph | none>"
            purpose: "<why this diagram helps>"
      review_focus:
        - "<risk to check>"
```

Quality rules:
- The output is a plan for content generation, not final documentation.
- Preserve the conceptual hierarchy from the catalog phase.
- Do not reorganize the wiki by filesystem layout.
- Do not add pages unless a required explanation cannot fit the current structure.
- Do not remove pages only because exact evidence is not known yet; mark evidence gaps instead.
- Treat clickable source citations as mandatory for generated content.
