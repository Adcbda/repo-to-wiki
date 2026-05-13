Hierarchy constraints:

- Use 2 levels maximum: top-level section pages plus one level of child pages.
- Do not create grandchildren or any third-level pages.
- Avoid deep nesting; depth is for cognitive grouping, not for mirroring folders.
- Each top-level section should represent a major cognitive area such as architecture, runtime flow, public API, major subsystem, data model, extension model, operations, or development.
- Each subsection should explain a distinct source-backed mechanism, public abstraction, runtime phase, API family, workflow, or responsibility boundary and should be useful as its own wiki page.
- Avoid tiny sections with only one trivial child.
- Prefer conceptual grouping over implementation grouping.
- Merge low-value sections aggressively, but do not merge away major runtime phases, public API families, extension points, or developer workflows.
- Prefer repository-specific child titles over generic labels. A child page named only "Configuration", "Error Handling", "Examples", "Request API", or "Core Concepts" is usually too broad unless the repository itself exposes that as a named surface.

Depth and breadth expectations:

- For a non-trivial repository, do not return a flat list where every page has `children: []`.
- For medium repositories, target roughly 10-20 total pages with at least 2-4 top-level sections that contain children.
- For large framework, SDK, platform, compiler, infrastructure, or monorepo repositories, target roughly 20-50 total pages with 4-8 top-level sections that contain children.
- Important top-level sections should usually have 2-8 children.
- Leaf pages should be specific enough to guide evidence selection, but not so narrow that they become one-file summaries.
- If the repository exposes many public APIs, packages, protocols, model families, diagram types, integrations, or test/reporting tools, group them into child pages instead of collapsing them into one generic "API" or "Subsystem" page.
- When a subsection feels like it needs further nesting, split it into sibling child pages under the same top-level section instead.
- At least half of child pages in a medium or large repository should include concrete repository vocabulary from the observed metadata, README, package names, exported symbols, commands, protocols, product domains, or major subsystem names.
- Do not add a top-level page just because a topic is common in documentation. Add it only when it creates a better navigation cluster than placing the mechanism under an existing parent.
