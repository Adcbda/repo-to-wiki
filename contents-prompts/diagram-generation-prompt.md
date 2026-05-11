You are generating diagrams for a DeepWiki-style repository wiki page.

Your job is to add only diagrams that make the page easier to understand and are directly supported by source evidence.

Inputs:
- Target page metadata:
  {{PAGE_METADATA}}
- Draft page:
  {{DRAFT_PAGE}}
- Source evidence pack:
  {{SOURCE_EVIDENCE_PACK}}
- Related page metadata:
  {{RELATED_PAGE_METADATA}}

When to generate a diagram:
- Architecture pages: component or layer relationship graph.
- Lifecycle pages: flowchart or sequence diagram.
- Request/data/event/rendering/parsing/generation pages: flowchart with handoff points.
- API pages: resource hierarchy, client delegation, or object model if useful.
- Configuration pages: configuration read/merge/apply flow if useful.
- Development/testing/deployment pages: pipeline or workflow if useful.

When not to generate a diagram:
- The evidence does not show relationships clearly.
- A table is clearer.
- The page is a glossary, FAQ, or narrow reference page.
- The diagram would merely mirror folder structure.

Rules:
- Use Mermaid.
- Keep diagrams compact: usually 5-12 nodes.
- Use exact component, class, module, command, or package names from evidence.
- Do not include files as nodes unless the file itself is a runtime participant or public entrypoint.
- Do not invent calls or data movement.
- Label uncertain relationships conservatively or omit them.
- Add a short `Sources:` line after each diagram.

Output:
Return JSON so the caller can insert diagrams into the page:

```json
{
  "diagrams": [
    {
      "insert_after_heading": "## <heading in draft page>",
      "title": "<diagram title>",
      "reason": "<why this diagram improves the page>",
      "mermaid": "flowchart TD\n  A[Component] --> B[Component]",
      "sources": ["S1", "S3"]
    }
  ],
  "no_diagram_reason": null
}
```

If no diagram should be added:

```json
{
  "diagrams": [],
  "no_diagram_reason": "<short reason>"
}
```
