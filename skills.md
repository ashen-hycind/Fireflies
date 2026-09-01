# Agentic Swarm — Team Skills

## Person A — Swarm Architect / Orchestrator

### Required skills
- Multi-agent system architecture
- Workflow/orchestration design
- State management
- Structured data / JSON schemas
- LLM API integration
- Prompt and role design
- Routing and conditional execution
- Retry, timeout and fallback handling
- Decision synthesis
- Basic logging/tracing

### Should understand
- How to pass context between agents.
- How to determine which agents need to rerun after a changed condition.
- How to prevent uncontrolled agent loops.
- How to enforce a structured CEO decision format.

## Person B — Research + Finance

### Required skills
- Prompt engineering for specialized agents
- Business/market research reasoning
- Financial reasoning and basic modeling
- Structured-output generation
- Evidence vs assumption separation
- Data validation
- Testing LLM outputs
- Handling incomplete information

### Should understand
- Research Agent scope: market, customers, competitors, opportunity and risk.
- Finance Agent scope: cost, revenue, affordability, profitability and financial risk.
- How to make recommendations conditional on assumptions rather than inventing facts.

## Person C — Marketing + Trace / Evidence

### Required skills
- Marketing and go-to-market reasoning
- Prompt engineering
- Agent communication logging
- Execution tracing
- JSON/log parsing
- Evidence presentation
- Demo design
- Basic evaluation/testing

### Should understand
- Marketing & Sales scope: target customers, positioning, channels and acquisition strategy.
- What evidence judges need to see.
- How to make disagreements and responses visible.
- How to show baseline and surprise decisions clearly.

## Shared team skills

Everyone should understand:
- The overall swarm architecture.
- The generic business-case input.
- Agent boundaries and responsibilities.
- Shared-state and message formats.
- The Analyse → Share → Challenge → Compare → Decide protocol.
- Runtime surprise adaptation.
- Basic debugging and testing.
- Git/version control.
- How to run the complete system locally.

## Important design principle

The underlying LLM does not have to be different for every agent. Multiple agents may use the same model; they become distinct agents through separate role instructions, responsibilities, inputs and visible outputs.

The swarm should be designed as a reusable decision system. The business testcase should enter as runtime data rather than being encoded as a fixed answer.
