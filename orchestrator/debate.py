"""
Debate & Challenge Engine for Fireflies Swarm.

Coordinates structured cross-department challenges, critiques, defenses, and concessions
to ensure critical assumptions are stress-tested before executive decision-making.
"""

import json
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from state.schemas import (
    InitialBusinessCase,
    AgentAnalysis,
    DebateMessage,
)
from utils.llm import generate_structured, DEFAULT_FAST_MODEL


class DebateRoundOutput(BaseModel):
    """Container for a generated round of debate messages."""
    messages: List[DebateMessage] = Field(
        description="List of structured challenge and response messages"
    )


DEBATE_COORDINATOR_PROMPT = """You are the Boardroom Debate Coordinator.
Your objective is to examine the analyses from Research, Finance, and Marketing departments, identify conflicting assumptions, high-risk trade-offs, or unsupported claims, and generate a structured cross-examination exchange.

Guidelines:
1. Ensure at least one explicit, high-stakes disagreement is highlighted (e.g., Marketing's optimistic growth vs. Finance's cash burn, or Research's market risks vs. Marketing's target channel).
2. For every challenge, include the target agent's structured response/defense (or concession).
3. Set appropriate message_type ('challenge', 'response', 'clarification', 'objection', 'agreement').
4. Keep arguments concise, analytical, and grounded in the business case facts.
"""


class DebateEngine:
    """Coordinates boardroom challenges and responses between department agents."""

    def __init__(self, model: Optional[str] = None):
        self.model = model or DEFAULT_FAST_MODEL

    def _generate_fallback_debate(
        self,
        business_case: InitialBusinessCase,
        department_analyses: Dict[str, AgentAnalysis],
    ) -> List[DebateMessage]:
        """Deterministic fallback debate exchange if LLM is offline or encounters error."""
        fin = department_analyses.get("finance")
        mkt = department_analyses.get("marketing")
        res = department_analyses.get("research")

        mkt_rec = mkt.recommendation if mkt else "growth strategy"
        fin_rec = fin.recommendation if fin else "conservative runway strategy"

        return [
            DebateMessage(
                message_id="deb_001",
                from_agent="finance",
                to_agent="marketing",
                message_type="challenge",
                content=f"Finance challenges Marketing: The projected acquisition timeline in '{mkt_rec}' may exceed the {business_case.context.timeline} horizon and strain monthly cash burn without proven conversion metrics.",
                referenced_agent="marketing",
                referenced_claim="Customer acquisition velocity and payback timeline",
                requires_response=True,
            ),
            DebateMessage(
                message_id="deb_002",
                from_agent="marketing",
                to_agent="finance",
                message_type="response",
                content=f"Marketing defends to Finance: Initial channel testing indicates multi-channel diversification offsets customer acquisition risk. We will gate marketing spend against strict monthly CAC milestones.",
                referenced_agent="finance",
                referenced_claim="Acquisition timeline and cash burn risk",
                requires_response=False,
            ),
            DebateMessage(
                message_id="deb_003",
                from_agent="research",
                to_agent="all",
                message_type="clarification",
                content=f"Research notes: Verified market trends in {business_case.facts.industry} support selective initial rollout while monitoring competitive retaliation.",
                referenced_agent="all",
                referenced_claim="Market timing and competitive landscape",
                requires_response=False,
            ),
        ]

    def run_debate(
        self,
        business_case: InitialBusinessCase,
        department_analyses: Dict[str, AgentAnalysis],
    ) -> List[DebateMessage]:
        """
        Executes a structured debate round between department analyses.
        """
        analyses_formatted = []
        for role, analysis in department_analyses.items():
            analyses_formatted.append(
                f"=== {role.upper()} AGENT ===\n"
                f"Recommendation: {analysis.recommendation}\n"
                f"Findings: {json.dumps(analysis.findings)}\n"
                f"Assumptions: {json.dumps(analysis.assumptions)}\n"
                f"Risks: {json.dumps(analysis.risks)}\n"
                f"Confidence: {analysis.confidence}\n"
            )
        analyses_text = "\n".join(analyses_formatted)

        prompt = f"""
## BUSINESS CASE:
Company: {business_case.facts.company_name}
Objective: {business_case.context.primary_objective}
Budget Limit: {business_case.context.budget_limit}

## DEPARTMENT ANALYSES:
{analyses_text}

---
TASK: Generate a structured debate sequence (2 to 4 messages) where department agents challenge each other's assumptions and defend their positions.
Every challenge MUST have a corresponding response message referencing the claim.
"""
        try:
            result = generate_structured(
                prompt=prompt,
                response_model=DebateRoundOutput,
                system_prompt=DEBATE_COORDINATOR_PROMPT,
                model=self.model,
            )
            return result.messages
        except Exception:
            return self._generate_fallback_debate(business_case, department_analyses)
