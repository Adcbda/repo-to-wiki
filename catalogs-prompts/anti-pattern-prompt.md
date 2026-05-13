Avoid these anti-patterns:

BAD:
- Organizing pages directly from folder structure
- Mirroring src/ directories
- Creating one page per file
- Creating a flat wiki where every major topic is a top-level leaf page
- Hiding multiple important mechanisms inside broad pages such as "Core Concepts", "Architecture", "API", or "Development"
- Designing the navigation as a FAQ or interview-question list
- Using generic page titles when the repository exposes concrete mechanisms, APIs, protocols, pipelines, workflows, or object models
- Creating pages whose only structure is "What is X?", "How does X work?", and "What are the main features?"
- Generating low-level utility sections
- Over-documenting implementation details
- Under-documenting the system by stopping at a shallow overview/catalog level
- Producing exhaustive but unreadable structures
- Guessing source paths from class names or conceptual ownership
- Referencing files or directories that were not observed in the repository
- Letting source-hint validation turn the wiki back into a folder tree
- Removing useful conceptual pages only because exact file-level hints are uncertain

GOOD:
- Organizing by mental models
- Organizing by runtime behavior
- Organizing by responsibilities
- Organizing by developer workflows
- Organizing by architecture layers
- Organizing by domain concepts
- Expanding major subsystems into child pages that cover their APIs, lifecycle, configuration, data flow, errors, and extension points when those topics are present
- Giving large repositories enough breadth to feel like a real engineering wiki rather than a table of contents draft
- Naming child pages after source-backed mechanisms and public abstractions, such as request dispatch, transport configuration, parser pipelines, model loading, renderer registration, or command execution
- Planning each page with a scope, concrete mechanisms, key source entities, and an outline before drafting prose
- Using only verified repository paths in `source_hints`
- Falling back to verified directories or globs when exact files are uncertain
- Keeping the conceptual page structure stable while validating only the evidence pointers

The wiki should feel like:
"How to understand the system"

NOT:
"How the filesystem looks"

NOT:
"A list of questions to ask about the system"
