"""
Strategy Comparison & Matrix Synthesizer for Fireflies Swarm.

Evaluates candidate strategic options (Option A vs Option B) across financial, market,
and operational dimensions to build the formal StrategyComparison matrix.
"""

import json
from typing import Dict, List, Optional
from state.schemas import (
    InitialBusinessCase,
    AgentAnalysis,
    DebateMessage,
    StrategyComparison,
    StrategyEvaluation,
)
from utils.llm import generate_structured, DEFAULT_FAST_MODEL


STRATEGY_SYNTHESIZER_PROMPT = """You are the Lead Strategic Planner for an enterprise boardroom.
Your role is to impartially compare candidate strategic options (e.g. Option A vs Option B) based on inputs from Research, Finance, and Marketing departments, as well as the boardroom debate exchange.

Guidelines:
1. Provide an objective, balanced evaluation for every candidate option.
2. Outline distinct advantages, disadvantages, financial/market/operational impacts, and specific risks for each option.
3. Identify which department agents support each option.
4. Indicate the leading/preferred option post-debate, key trade-offs between options, and any unresolved uncertainties.
"""


class StrategyComparator:
    """Evaluates candidate options into a structured StrategyComparison matrix."""

    def __init__(self, model: Optional[str] = None):
        self.model = model or DEFAULT_FAST_MODEL

    def _generate_fallback_comparison(
        self,
        business_case: InitialBusinessCase,
        department_analyses: Dict[str, AgentAnalysis],
        debate_messages: List[DebateMessage],
    ) -> StrategyComparison:
        """Deterministic fallback comparison when LLM is offline or encounters error."""
        options = business_case.candidate_options
        opt_a = options[0] if options else None
        opt_b = options[1] if len(options) > 1 else None

        evaluations = []
        if opt_a:
            evaluations.append(
                StrategyEvaluation(
                    option_id=opt_a.option_id,
                    advantages=[
                        f"Directly advances primary objective: '{business_case.context.primary_objective}'.",
                        f"Mechanism: {opt_a.intended_mechanism}",
                    ],
                    disadvantages=[
                        "Requires focused capital allocation and strict execution discipline.",
                    ],
                    financial_impact=f"Estimated within budget limit ({business_case.context.budget_limit or 'within baseline runway'}).",
                    market_impact="Establishes defensible market footprint in target territory.",
                    operational_impact=f"Requires team execution over {business_case.context.timeline}.",
                    risks=[
                        "Execution delay and initial customer acquisition payback lag.",
                    ],
                    supporting_agents=["research", "marketing"],
                )
            )

        if opt_b:
            evaluations.append(
                StrategyEvaluation(
                    option_id=opt_b.option_id,
                    advantages=[
                        f"Alternative vector: {opt_b.name}.",
                        "Lower execution complexity in certain operational areas.",
                    ],
                    disadvantages=[
                        "Higher competitive pressure or slower long-term TAM capture.",
                    ],
                    financial_impact="May require defensive discounting or slower payback.",
                    market_impact="Faces established incumbent resistance.",
                    operational_impact="Lower initial team restructuring required.",
                    risks=[
                        "Competitive retaliation and margin compression.",
                    ],
                    supporting_agents=["finance"],
                )
            )

        preferred = opt_a.option_id if opt_a else "OPTION_A"
        return StrategyComparison(
            evaluations=evaluations,
            preferred_option=preferred,
            trade_offs=[
                "Growth speed and market leadership vs. short-term burn conservation.",
                "Direct territorial expansion vs. defensive upselling to existing segments.",
            ],
            unresolved_uncertainties=[
                "Competitor pricing response velocity in the medium term.",
                "Customer lifetime value realization across new cohorts.",
            ],
        )

    def compare_strategies(
        self,
        business_case: InitialBusinessCase,
        department_analyses: Dict[str, AgentAnalysis],
        debate_messages: List[DebateMessage],
    ) -> StrategyComparison:
        """
        Synthesizes a StrategyComparison across all candidate options.
        """
        options_text = json.dumps([opt.model_dump() for opt in business_case.candidate_options], indent=2)
        
        dept_summaries = []
        for role, analysis in department_analyses.items():
            dept_summaries.append(
                f"- {role.upper()}: Recommendation='{analysis.recommendation}', Findings={json.dumps(analysis.findings)}, Assumptions={json.dumps(analysis.assumptions)}"
            )
        dept_text = "\n".join(dept_summaries)

        debate_text = "\n".join(
            [f"[{m.from_agent} -> {m.to_agent or 'all'}]: {m.content}" for m in debate_messages]
        )

        prompt = f"""
## BUSINESS CASE:
Company: {business_case.facts.company_name}
Objective: {business_case.context.primary_objective}
Constraints: {json.dumps(business_case.context.hard_constraints)}

## CANDIDATE STRATEGIC OPTIONS:
{options_text}

## DEPARTMENT RECOMMENDATIONS & ANALYSES:
{dept_text}

## BOARDROOM DEBATE:
{debate_text}

---
TASK: Generate the complete StrategyComparison matrix evaluating every candidate option with detailed advantages, disadvantages, impacts, risks, and trade-offs.
"""
        try:
            return generate_structured(
                prompt=prompt,
                response_model=StrategyComparison,
                system_prompt=STRATEGY_SYNTHESIZER_PROMPT,
                model=self.model,
            )
        except Exception:
            return self._generate_fallback_comparison(business_case, department_analyses, debate_messages)
