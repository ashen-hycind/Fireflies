# Agentic Swarm — Team Tasks

## Goal

Build a reusable multi-agent business decision swarm that can accept an unknown business testcase at runtime and produce an explainable, adaptable CEO decision.

The judged workflow must demonstrate:
**Analyse → Share → Challenge → Compare → Decide**, followed by adaptation to a new business condition.

## Team split

### Person A — Swarm Architect / Orchestrator
**Owns:** overall architecture, orchestration, shared state, CEO agent, debate flow, strategy comparison, surprise/adaptation.

Tasks:
- Define the generic business-case input schema.
- Define shared-state structure.
- Build the orchestrator/workflow skeleton.
- Build the CEO agent.
- Implement agent communication.
- Implement challenge/debate logic.
- Implement strategy A vs B comparison.
- Implement surprise-condition injection.
- Implement affected-agent reruns.
- Implement termination and retry/fallback controls.

Deliverables:
- `orchestrator/`
- `state/`
- `agents/ceo`
- End-to-end workflow skeleton.

### Person B — Research + Finance
**Owns:** two mandatory analytical department agents.

Tasks:
- Build Research Agent.
- Build Finance Agent.
- Define structured outputs.
- Ensure facts and assumptions are separated.
- Test both agents against multiple generic business cases.
- Document failure/fallback behavior.

Deliverables:
- `agents/research`
- `agents/finance`
- Agent prompts/instructions
- Test cases and expected output structure.

### Person C — Marketing + Trace / Evidence
**Owns:** Marketing & Sales Agent and the auditable boardroom trace.

Tasks:
- Build Marketing & Sales Agent.
- Capture agent inputs and outputs.
- Capture agent-to-agent messages.
- Capture disagreements and responses.
- Capture strategy comparison.
- Capture baseline CEO decision.
- Capture surprise and revised CEO decision.
- Create a readable trace/demo view.
- Prepare evidence required for judging.

Deliverables:
- `agents/marketing`
- `traces/`
- Evidence/demo output.

## Execution order

### Phase 1 — All 3 together
Before coding, agree on:
1. Generic business input.
2. Agent responsibilities.
3. Agent input/output schemas.
4. Shared state.
5. Communication protocol.
6. Challenge mechanism.
7. CEO decision format.
8. Surprise/adaptation mechanism.

### Phase 2 — Parallel build
- Person A: orchestrator + CEO + state.
- Person B: Research + Finance.
- Person C: Marketing + trace.

### Phase 3 — Integration
Connect:

`Research + Finance + Marketing → Shared State → Challenge → Compare → CEO`

Verify that every agent has a distinct responsibility, input, output, and visible trace.

### Phase 4 — Generalization testing
Test the same swarm architecture with several different hypothetical business cases, such as:
- Product launch
- Market expansion
- Pricing decision
- Capacity investment
- Competitor response

Do not hardcode answers for these cases.

### Phase 5 — Surprise testing
For an initial testcase:
1. Run the swarm.
2. Save the baseline decision.
3. Introduce a changed condition.
4. Identify affected assumptions.
5. Rerun materially affected agents.
6. Run another comparison/debate.
7. Produce a revised CEO decision.
8. Verify what changed and what remained stable.

## Integration checklist

- [ ] 4–8 identifiable agents.
- [ ] Research, Finance, Marketing & Sales, and CEO present.
- [ ] Distinct role instructions.
- [ ] Generic runtime business input.
- [ ] Visible agent outputs.
- [ ] Information exchange.
- [ ] At least one meaningful disagreement.
- [ ] Response/defence to disagreement.
- [ ] At least two viable strategies.
- [ ] CEO decision with evidence.
- [ ] Rejected alternative and reason.
- [ ] Trade-offs, risks, assumptions.
- [ ] Implementation steps.
- [ ] At least three measurable KPIs.
- [ ] Surprise adaptation.
- [ ] Execution trace.
- [ ] Failure/fallback path.
- [ ] No hardcoded final outcome.
