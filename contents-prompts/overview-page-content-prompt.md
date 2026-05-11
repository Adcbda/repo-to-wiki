You are writing the top-level Overview page for a DeepWiki-style repository wiki.

The Overview page is the entrypoint into the wiki. It should explain what the repository is, how to think about it, and where to go next.

Inputs:
- Repository metadata:
  {{REPOSITORY_METADATA}}
- Repository classification:
  {{REPOSITORY_CLASSIFICATION}}
- Full wiki structure:
  {{WIKI_STRUCTURE}}
- Target page metadata:
  {{PAGE_METADATA}}
- Source evidence pack:
  {{SOURCE_EVIDENCE_PACK}}
- Optional generated child pages or summaries:
  {{CHILD_PAGE_SUMMARIES}}

Required content:
1. H1 title
2. `Relevant source files`
3. Purpose and scope
4. What the repository does
5. System or library architecture overview
6. Major subsystems
7. How the main runtime or usage flow works at a high level
8. Source navigation guide
9. Links to important next pages

Adapt by repository category:
- SDK / Client Library:
  Emphasize client construction, request lifecycle, resources, types, errors, retries, streaming, and generated/manual boundaries.
- Framework:
  Emphasize core abstractions, application lifecycle, extension points, configuration, and user-facing APIs.
- Developer Tooling or CLI Tool:
  Emphasize user workflows, command model, project/index model, execution pipeline, integrations, output formats, and debugging.
- Rendering Engine:
  Emphasize parsing/detection, internal model, layout, rendering, theming, security, and supported diagram/component types.
- AI / ML Framework:
  Emphasize model abstractions, model lifecycle, data/tokenization, training, inference/generation, architecture families, optimization, and integrations.
- Web Application:
  Emphasize product domains, frontend/backend boundary, routing, state management, API integration, auth, build, and deployment.
- Infrastructure, Runtime Platform, Database, or Distributed System:
  Emphasize process model, control/data plane, storage/networking/scheduling, lifecycle, configuration, observability, failure handling, and operations.

Citation rules:
- Every factual claim about purpose, packages, runtime model, supported features, public APIs, commands, or architecture must cite evidence.
- Use `Sources: [S1] [S2]` after each substantive section.
- If the README claims a capability but implementation evidence is absent, describe it as repository documentation, not proven behavior.

Output format:
Return only Markdown:

```markdown
# <Repository or Product Name> Overview

## Relevant source files
- `path/to/file.ext`

## Purpose and Scope
...
Sources: [S1]

## What This Repository Provides
...
Sources: [S1] [S2]

## High-Level Architecture
...
Sources: [S3] [S4]

## Major Subsystems
| Subsystem | Responsibility | Primary sources | Related wiki page |
| --- | --- | --- | --- |

## Main Flow
...
Sources: [S5]

## Source Navigation
...
Sources: [S2] [S6]

## Where to Go Next
- [Architecture](Architecture)
```

Avoid:
- Repeating the entire wiki table of contents.
- Explaining every file or folder.
- Overstating implementation details that belong on child pages.
- Creating a quick start unless the evidence and wiki structure call for one.
