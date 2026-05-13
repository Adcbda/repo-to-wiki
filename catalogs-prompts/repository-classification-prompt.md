First classify the repository.

Possible categories:
- SDK / Client Library
- Framework
- Infrastructure System
- Developer Tooling
- Compiler / Parser
- Runtime Platform
- Web Application
- CLI Tool
- Rendering Engine
- AI / ML Framework
- Database System
- Distributed System

Then adapt the wiki structure accordingly.
The repository category should change both:
- which top-level sections appear
- which subsystem pages are considered important
- which repository-specific mechanisms should become page titles
- which public abstractions, runtime participants, commands, protocols, generated artifacts, or product domains should become `key_entities`

Use the following category-specific structure priorities when applicable:

SDK / Client Library:
- emphasize client configuration, authentication, request lifecycle, API resources, response models, errors, retries, pagination, streaming, and generated/manual code boundaries
- typical sections: Overview, Client Architecture, Public API Surface, Request Lifecycle, Resource Modules, Type System, Error Handling, Configuration, Testing

Framework:
- emphasize application lifecycle, user-facing abstractions, plugin or middleware systems, configuration, runtime integration, and extension points
- typical sections: Overview, Core Concepts, Runtime Lifecycle, Framework Architecture, Extension System, Configuration, Public APIs, Development Workflow

Infrastructure System:
- emphasize control plane/data plane split, runtime architecture, scheduling, storage, networking, observability, deployment, and operational workflows
- typical sections: Overview, System Architecture, Runtime Model, Control Plane, Data Plane, Configuration, Deployment, Observability, Failure Handling

Developer Tooling:
- emphasize CLI or editor workflows, project model, command execution, analysis/indexing pipeline, integrations, reporting, and debugging
- typical sections: Overview, User Workflows, Command Architecture, Project Model, Execution Pipeline, Integrations, Configuration, Build & Development, Testing

Compiler / Parser:
- emphasize source ingestion, lexing/parsing, AST or IR, semantic analysis, transformation, code generation/rendering, diagnostics, and extension points
- typical sections: Overview, Language Model, Parsing Pipeline, Intermediate Representation, Transformation Pipeline, Output Generation, Diagnostics, Extension Points, Testing

Runtime Platform:
- emphasize process model, lifecycle, scheduling, resource management, APIs, extension model, and operational concerns
- typical sections: Overview, Process Architecture, Runtime Lifecycle, Core Services, Scheduling, Resource Management, Public APIs, Configuration, Observability

Web Application:
- emphasize product domains, frontend/backend boundary, routing, state management, data fetching, API layer, authentication, build/deploy workflow, and testing
- typical sections: Overview, Product Domains, Application Architecture, Routing, State Management, API Integration, Authentication, Build & Development, Deployment

CLI Tool:
- emphasize command model, configuration discovery, execution flow, input/output formats, integrations, errors, and packaging
- typical sections: Overview, Command Architecture, Execution Flow, Configuration, Input & Output, Integrations, Error Handling, Packaging

Rendering Engine:
- emphasize document/model ingestion, parsing, layout, rendering pipeline, themes/styles, security, plugins, and supported output formats
- typical sections: Overview, Rendering Architecture, Parsing & Detection, Layout Pipeline, Rendering Pipeline, Diagram or Component Types, Theming, Security, Extension System

AI / ML Framework:
- emphasize model abstractions, data/tokenization pipeline, training/inference/generation lifecycle, architecture families, optimization, serialization/export, and integrations
- typical sections: Overview, Core Abstractions, Model Lifecycle, Data Pipeline, Training, Inference & Generation, Model Architectures, Optimization, Serialization, Integrations

Database System:
- emphasize query lifecycle, storage engine, indexing, transactions, replication, consistency, recovery, configuration, and operations
- typical sections: Overview, Database Architecture, Query Lifecycle, Storage Engine, Indexing, Transactions, Replication, Recovery, Configuration, Operations

Distributed System:
- emphasize node roles, cluster topology, coordination, messaging, consistency, fault tolerance, scaling, observability, and operations
- typical sections: Overview, Distributed Architecture, Node Lifecycle, Coordination, Messaging, Consistency Model, Fault Tolerance, Scaling, Observability, Operations

If a repository fits multiple categories, choose one primary category and optionally borrow sections from secondary categories.
Do not include category template sections that are not supported by the actual repository.
Do not force generic sections such as "Module System" or "Event System" unless they are meaningful for the repository.

Classification should capture more than the category label:
- Identify the main execution or usage lifecycle in concrete repository vocabulary.
- Identify public API families, command groups, resource groups, or object models when present.
- Identify generated/manual boundaries, adapters, plugins, transports, protocols, renderers, parsers, services, or model families when present.
- Prefer exact names observed in README, manifests, exports, examples, tests, package names, or high-signal source excerpts.
- Avoid generic labels like "Core", "Utils", "API", "Configuration", or "Development" unless those are actual named surfaces in the repository.
