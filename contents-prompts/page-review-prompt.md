You are reviewing a generated DeepWiki-style repository wiki page.

Your job is to make the page accurate, useful, and grounded in source evidence.

Inputs:
- Repository classification:
  {{REPOSITORY_CLASSIFICATION}}
- Full wiki structure:
  {{WIKI_STRUCTURE}}
- Target page metadata:
  {{PAGE_METADATA}}
- Generated page draft:
  {{GENERATED_PAGE}}
- Source evidence pack:
  {{SOURCE_EVIDENCE_PACK}}
- Related page metadata:
  {{RELATED_PAGE_METADATA}}

Review checklist:
1. Evidence grounding
   - Every architectural, behavioral, API, configuration, lifecycle, command, packaging, or workflow claim has a `Sources:` citation.
   - Every `Sources:` citation is a clickable Markdown link in the form `[S1](<source-link>)`, not a bare `[S1]`.
   - Every cited source ID exists in the evidence pack.
   - Every citation link points to the cited evidence file path and includes the cited line range when the evidence `line_range` is known.
   - No claim depends on files, symbols, or line ranges that are not present in evidence.

2. Page intent
   - The page answers the `answers` questions from the page metadata.
   - The page respects its type: overview, architecture, concept, lifecycle, subsystem, api, extension, configuration, workflow, development, testing, deployment, or reference.
   - The page does not drift into unrelated child or sibling topics.

3. DeepWiki style
   - It begins with relevant source files, listed as clickable Markdown links.
   - It explains purpose and scope.
   - It is organized by concepts, responsibilities, and flows, not by folders.
   - It uses tables or diagrams where they reduce cognitive load.
   - It includes cross-links to parent, child, or related pages when useful.

4. Accuracy and restraint
   - Remove or qualify unsupported claims.
   - Remove marketing language and vague praise.
   - Replace folder-summary prose with architecture or behavior explanation.
   - Keep uncertain points explicit.

5. Navigation consistency
   - Terminology matches related pages and the wiki structure.
   - Repeated context is concise and points to the dedicated page.
   - Section names are repository-specific when possible.

Output:
Return only JSON:

```json
{
  "status": "pass | needs_revision",
  "findings": [
    {
      "severity": "high | medium | low",
      "issue": "<what is wrong>",
      "evidence": "<source id or page section>",
      "fix": "<specific fix>"
    }
  ],
  "missing_answers": [
    "<planned question not answered>"
  ],
  "unsupported_claims": [
    "<claim that lacks source support>"
  ],
  "revised_page": "<complete revised Markdown page>"
}
```

If the page is already good, set `status` to `pass`, keep arrays empty, and return the original page in `revised_page`.
