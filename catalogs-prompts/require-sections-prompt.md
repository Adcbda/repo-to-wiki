The wiki structure should usually include most of these section types when applicable.
Treat this as a section pool, not a fixed template:

- Overview
- Quick Start
- Architecture
- Core Concepts
- Runtime Flow
- Module System
- Public APIs
- Extension / Plugin System
- Configuration
- State Management
- Data Flow
- Event System
- Rendering Pipeline
- Request Lifecycle
- Build & Development
- Testing
- Debugging
- Deployment
- Source Navigation
- FAQ

Only include sections that are meaningful for this repository.

Prefer repository-specific section names over generic names when they are clearer.
For example:
- use "Request Lifecycle" for SDKs and web services
- use "Rendering Pipeline" for rendering engines
- use "Parsing Pipeline" for compilers and parser-heavy systems
- use "Model Lifecycle" for AI / ML frameworks
- use "Command Execution Flow" for CLI tools

Every included section should have a distinct purpose and should map to at least one important concept, subsystem, runtime flow, public API, extension point, or developer workflow.
