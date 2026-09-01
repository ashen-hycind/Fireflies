# Antigravity Workspace Guidelines & Team Ownership

This document defines the team boundaries and development rules for the **Agentic Swarm** project. All Antigravity agents working in this repository MUST respect these module ownership rules and guidelines.

---

## 1. Team Ownership & File Scope

Each team member is responsible for specific modules. **Do NOT modify files outside of your assigned scope unless explicitly agreed upon.**

### Person A — Swarm Architect / Orchestrator
- **Owned Directories & Files:**
  - `orchestrator/`
  - `state/`
  - `agents/ceo/`
  - Overall end-to-end integration and workflow execution.
- **Responsibilities:** Core orchestration loop, shared state schemas, CEO synthesis, debate & challenge engine, surprise-condition injection, fallback mechanisms.

### Person B — Research + Finance
- **Owned Directories & Files:**
  - `agents/research/`
  - `agents/finance/`
  - `tests/test_research.py`, `tests/test_finance.py`
- **Responsibilities:** Research agent (market trends, risks, facts vs. assumptions), Finance agent (unit economics, budget, financial feasibility, ROI), structured output adherence.

### Person C — Marketing + Trace / Evidence
- **Owned Directories & Files:**
  - `agents/marketing/`
  - `traces/`
  - `tests/test_marketing.py`, `tests/test_traces.py`
- **Responsibilities:** Marketing & Sales agent (GTM strategy, customer acquisition, pricing positioning), execution trace logging, boardroom evidence format, and auditable demo views.

---

## 2. Shared Contracts & Schema Compliance

1. **State as Source of Truth:**
   - All agents must consume and produce structured data adhering strictly to the Pydantic schemas in `state/schemas.py`.
   - If a schema change is needed, it must be coordinated with Person A.

2. **Isolated Unit Testing:**
   - Each person should write dedicated unit tests for their agents under `tests/` without modifying other team members' test suites.

3. **No Overwriting Shared Modules:**
   - When generating an Implementation Plan for Person B or Person C, agents must **ONLY** propose changes within their respective owned directories.
   - Do not overwrite `orchestrator/engine.py` or `state/schemas.py` during individual agent development.
