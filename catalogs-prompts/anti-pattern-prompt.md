Avoid these anti-patterns:

BAD:
- Organizing pages directly from folder structure
- Mirroring src/ directories
- Creating one page per file
- Generating low-level utility sections
- Over-documenting implementation details
- Producing exhaustive but unreadable structures
- Guessing source paths from class names or conceptual ownership
- Referencing files or directories that were not observed in the repository

GOOD:
- Organizing by mental models
- Organizing by runtime behavior
- Organizing by responsibilities
- Organizing by developer workflows
- Organizing by architecture layers
- Organizing by domain concepts
- Using only verified repository paths in `source_hints`
- Falling back to verified directories or globs when exact files are uncertain

The wiki should feel like:
"How to understand the system"

NOT:
"How the filesystem looks"
