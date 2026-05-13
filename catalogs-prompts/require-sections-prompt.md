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
- use "Router Dispatch and Layer Matching" instead of "Router System" when routing dispatch is the real mechanism
- use "Client Resources and Request Builders" instead of "API" when an SDK exposes resource clients
- use "Workbench Services and Contributions" instead of "Architecture" when an editor platform is organized around services and contributions

Every included section should have a distinct purpose and should map to at least one important concept, subsystem, runtime flow, public API, extension point, or developer workflow.
Do not include a section only because it appears in this pool.
If a section remains generic after planning its children, rename it around the repository's real mechanism or merge it into a stronger parent.

Deep engineering wiki coverage:

- Overview pages should orient readers, but they should not absorb the details that deserve their own pages.
- Architecture pages should usually branch into component responsibilities, package/module boundaries, and the main runtime handoff points.
- Runtime or lifecycle pages should usually branch into entry points, dispatch/execution, error/failure handling, and output/response/finalization when those phases exist.
- Public API sections should usually branch by API family, object model, resource group, command group, or user-facing abstraction rather than listing every method in one page.
- Data/model/type sections should usually branch into schema/model definitions, transformation/validation, serialization, compatibility, or generated/manual boundaries when present.
- Development sections should usually branch into setup, test strategy, build/release, code generation, quality checks, and contribution workflows when those are evidenced.
- Advanced/extension sections should usually branch into plugins, adapters, protocol integrations, custom transports, template/rendering engines, or external tool integrations when present.

Page planning metadata:

- Every page should have a narrow `scope` that defines what belongs on the page and what belongs elsewhere.
- `primary_mechanisms` should name concrete source-backed mechanisms, not documentation categories.
- `key_entities` should capture terms that evidence selection can search for later: exported symbols, packages, commands, config names, protocols, generated artifacts, runtime participants, or product-domain names.
- `page_outline` should be written as future section headings such as "Dispatch Participants", "Configuration Sources", "Error Propagation", or "Resource Object Model"; do not use the planned `answers` questions as headings.
