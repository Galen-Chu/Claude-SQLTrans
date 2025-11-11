# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Spec Workflow-managed project** using the Spec Workflow MCP Server system. The project follows a specification-driven development approach where requirements, design, and tasks are documented before implementation.

## Spec Workflow System

### Directory Structure

```
.spec-workflow/
├── specs/              # Feature specifications (requirements, design, tasks)
├── steering/           # Project-level guidance documents
│   ├── product.md     # Product vision and goals
│   ├── tech.md        # Technology stack and standards
│   └── structure.md   # Code organization patterns
├── approvals/          # Approved specification snapshots
├── archive/            # Historical/deprecated specs
├── templates/          # Default document templates
├── user-templates/     # Custom overridden templates
└── config.toml         # Configuration (copy from config.example.toml)
```

### Configuration

Before starting development:
1. Copy `.spec-workflow/config.example.toml` to `.spec-workflow/config.toml`
2. Configure `projectDir`, `port`, and other settings as needed
3. Note: Use double slashes (`\\`) for Windows paths in TOML files

### Workflow Process

#### 1. Define Steering Documents (First-time setup)

Create these in `.spec-workflow/steering/`:
- **product.md**: Product purpose, target users, key features, success metrics
- **tech.md**: Technology stack, architecture, development tools, technical constraints
- **structure.md**: Directory organization, naming conventions, code patterns

#### 2. Create Feature Specifications

For each new feature, create a directory in `.spec-workflow/specs/[feature-name]/`:

**requirements.md** - Define what to build:
- User stories with acceptance criteria
- Requirements must align with `product.md`
- Use formal criteria format: `WHEN [event] THEN [system] SHALL [response]`
- Include non-functional requirements (performance, security, modularity)

**design.md** - Define how to build:
- Architecture and design patterns
- Must align with `tech.md` and `structure.md`
- Code reuse analysis (leverage existing components)
- Component interfaces and data models
- Error handling and testing strategy
- Emphasize modular design and single responsibility

**tasks.md** - Define implementation steps:
- Granular, ordered checklist of development tasks
- Each task includes:
  - File path to create/modify
  - What to implement
  - Code to leverage (reuse existing utilities/components)
  - Requirements covered
  - AI prompt for implementation (Role, Task, Restrictions, Success)

#### 3. Development Workflow

1. **Read steering documents** to understand project context
2. **Follow tasks.md sequentially** - each task is self-contained
3. **Leverage existing code** as indicated in each task
4. **Maintain modularity** - one responsibility per file
5. **Run tests** as tasks specify
6. **Update approvals/** when specs are finalized

### Template Customization

To customize document templates:
1. Copy template from `.spec-workflow/templates/` to `.spec-workflow/user-templates/`
2. Modify the template structure
3. Templates support variables: `{{projectName}}`, `{{featureName}}`, `{{date}}`, `{{author}}`
4. System loads user templates first, falls back to defaults

### Key Principles

#### Modular Architecture
- **Single Responsibility**: Each file has one clear purpose
- **Component Isolation**: Small, focused components over monolithic files
- **Service Layer Separation**: Separate data access, business logic, presentation
- **Code Reuse**: Leverage existing utilities and components

#### Specification-Driven Development
- Write specifications before code
- All code must trace back to requirements
- Design must align with technical and structural standards
- Tasks provide clear implementation path with AI prompts

#### Task Execution
Each task in `tasks.md` includes:
- **File**: Specific file to create/modify
- **Purpose**: Why this code exists
- **Leverage**: Existing code to build upon
- **Requirements**: Which requirements it satisfies
- **Prompt**: AI instruction with role, task, restrictions, and success criteria

### Dashboard (Optional)

The Spec Workflow system includes a web dashboard for viewing specifications:
- Set `autoStartDashboard = true` in config.toml to auto-launch
- Configure `port` for dashboard (default: ephemeral)
- Access at `http://localhost:[port]`
- Dashboard session info stored in `.spec-workflow/session.json`

### Integration with Development

When implementing features:
1. Check `.spec-workflow/steering/` for project-wide standards
2. Open `.spec-workflow/specs/[feature]/requirements.md` for what to build
3. Review `.spec-workflow/specs/[feature]/design.md` for architecture
4. Follow `.spec-workflow/specs/[feature]/tasks.md` step-by-step
5. Each task prompt guides AI-assisted implementation

### Common Patterns

**Before starting any feature:**
```
1. Read product.md, tech.md, structure.md
2. Understand requirements.md for the feature
3. Review design.md architecture
4. Follow tasks.md sequentially
```

**When creating new components:**
```
1. Check design.md for component specifications
2. Look for existing code to leverage (noted in tasks)
3. Follow naming conventions from structure.md
4. Maintain single responsibility principle
5. Write tests as specified in tasks
```

**When extending functionality:**
```
1. Review relevant specs for context
2. Identify integration points in design.md
3. Leverage existing utilities/base classes
4. Update tests to cover new behavior
```

## Development Commands

(To be added as the project codebase is implemented - these will vary based on the technology stack chosen in tech.md)

## Notes

- This project uses specification-driven development
- Always start with specs, not code
- Keep steering documents updated as project evolves
- Archive old specs when features change significantly
- Use approvals/ for snapshot of finalized specifications
