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
   - Read the page title, type, navigation_group, purpose, scope, primary_mechanisms, key_entities, page_outline, answers, source_hints, parent page, child pages, and sibling pages.
   - Decide what source-backed mechanism, runtime flow, API family, responsibility boundary, configuration behavior, or developer workflow the page must explain.
   - Treat `answers` as acceptance criteria. Do not turn them into headings or make the content plan read like a FAQ.
   - Identify what belongs on the page and what should be delegated to parent, child, or sibling pages.

2. Evidence selection
   - Specify how the downstream source evidence selection prompt should be run for the page.
   - Start from verified source_hints.
   - Use `primary_mechanisms` and `key_entities` to search for implementation, public exports, tests, examples, and docs.
   - Expand to nearby tests, examples, configuration files, documentation, entrypoints, public exports, and implementation files when they are relevant.
   - Do not invent files or symbols.
   - Prefer evidence that explains handoffs, ownership, contracts, defaults, error paths, generated/manual boundaries, or workflow steps.

3. Page drafting
   - Specify how the downstream DeepWiki page content prompt should use the selected evidence pack.
   - Write a focused page, not a file summary.
   - Follow `page_outline` unless evidence shows a stronger section order.
   - Write sections around mechanisms and responsibilities, not around the planned questions.
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
      navigation_group: "<navigation group>"
      path: "<suggested wiki output path>"
      parent: "<parent title or null>"
      scope: "<what belongs on this page and what belongs elsewhere>"
      intent: "<one sentence>"
      primary_mechanisms:
        - "<mechanism, flow, API family, workflow, or responsibility>"
      key_entities:
        - "<symbol, package, command, config key, protocol, generated artifact, or runtime participant>"
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
        page_outline:
          - "<planned DeepWiki section>"
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
- Do not plan FAQ-style pages. Planned questions must remain acceptance checks, while sections should explain mechanisms, APIs, flows, responsibilities, and workflows.
- Prefer repository-specific terminology from `key_entities` and source evidence over generic section names.
