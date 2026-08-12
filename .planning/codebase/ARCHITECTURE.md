# Architecture Overview

**Analysis Date:** 2026-08-13

## Architectural Pattern
- **Plan-Driven Agentic Development:** Hierarchical specification and plan execution using `.planning/` directory context.
- **Modularity:** Workflow definitions, reference docs, and scripts stored in `.agents/gsd-core/`.

## Entry Points
- `c:\Users\hp\Documents\Projects\SecureFinTech` — Workspace root
- `.agents/gsd-core/bin/gsd-tools.cjs` — Core GSD CLI shim

## Data Flow
1. User Intent / Slash Command → GSD Skill (`.agents/skills/`)
2. Workflow Execution → `.agents/gsd-core/workflows/`
3. Artifact Synthesis → `.planning/` (`PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`)

---
*Codebase analysis: 2026-08-13*
<!-- refreshed: 2026-08-13 -->
