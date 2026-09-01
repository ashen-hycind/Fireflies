"""
CEO Agent module for Fireflies Swarm.

Synthesizes multi-department analytical inputs, debate challenges, and strategy evaluations
into an authoritative, evidence-backed executive decision adhering to the CEODecision schema.
"""

import json
from typing import Dict, List, Optional
from state.schemas import (
    InitialBusinessCase,
    AgentAnalysis,
    DebateMessage,
    StrategyComparison,
    CEODecision,
    SurpriseEvent,
)
from utils.llm import generate_structured, DEFAULT_REASONING_MODEL


CEO_SYSTEM_PROMPT = """You are the Chief Executive Officer (CEO) of an enterprise in a high-stakes strategic boardroom.
Your role is to synthesize analytical findings from your department heads (Research, Finance, Marketing), resolve inter-departmental disagreements, evaluate candidate strategic options, and deliver an authoritative, clear, and actionable executive decision.

Guidelines for your decision:
1. Ground your rationale strictly in the evidence and findings provided by department agents.
2. Explicitly explain why rejected alternatives were not chosen.
3. Highlight critical trade-offs, underlying assumptions, and identified risks with mitigations.
4. Define concrete tactical implementation steps.
5. Define at least three (3) distinct, measurable business KPIs with clear targets.
6. If adapting to a surprise event, clearly explain what changed in your strategy and what remained stable.
"""


class CEOAgent:
    """Executive synthesizer and decision-maker agent."""

    def __init__(self, model: Optional[str] = None):
        self.model = model or DEFAULT_REASONING_MODEL

    def synthesize_baseline_decision(
        self,
        business_case: InitialBusinessCase,
        department_analyses: Dict[str, AgentAnalysis],
        debate_messages: List[DebateMessage],
        strategy_comparison: StrategyComparison,
    ) -> CEODecision:
        """
        Produces the baseline CEO decision based on initial case analysis, debate, and strategy matrix.
        """
        # Format department analyses summary
        dept_summary_lines = []
        for role, analysis in department_analyses.items():
            dept_summary_lines.append(
                f"### {role.upper()} ANALYSIS:\n"
                f"- Recommendation: {analysis.recommendation}\n"
                f"- Findings: {json.dumps(analysis.findings)}\n"
                f"- Evidence: {json.dumps(analysis.evidence)}\n"
                f"- Assumptions: {json.dumps(analysis.assumptions)}\n"
                f"- Risks: {json.dumps(analysis.risks)}\n"
                f"- Confidence: {analysis.confidence}\n"
            )
        dept_text = "\n".join(dept_summary_lines)

        # Format debate history
        debate_lines = []
        for msg in debate_messages:
            to_str = f" to {msg.to_agent}" if msg.to_agent else ""
            ref_str = f" [Claim: {msg.referenced_claim}]" if msg.referenced_claim else ""
            debate_lines.append(f"[{msg.from_agent}{to_str} ({msg.message_type})]{ref_str}: {msg.content}")
        debate_text = "\n".join(debate_lines) if debate_lines else "No debate logged."

        # Format strategy comparison
        eval_lines = []
        for ev in strategy_comparison.evaluations:
            eval_lines.append(
                f"Option '{ev.option_id}':\n"
                f"  Advantages: {json.dumps(ev.advantages)}\n"
                f"  Disadvantages: {json.dumps(ev.disadvantages)}\n"
                f"  Financial Impact: {ev.financial_impact}\n"
                f"  Market Impact: {ev.market_impact}\n"
                f"  Operational Impact: {ev.operational_impact}\n"
                f"  Risks: {json.dumps(ev.risks)}\n"
                f"  Supporting Departments: {json.dumps(ev.supporting_agents)}"
            )
        strat_text = (
            f"Preferred Option post-debate: {strategy_comparison.preferred_option}\n"
            f"Trade-offs: {json.dumps(strategy_comparison.trade_offs)}\n"
            f"Unresolved Uncertainties: {json.dumps(strategy_comparison.unresolved_uncertainties)}\n"
            + "\n".join(eval_lines)
        )

        prompt = f"""
## BUSINESS CASE CONTEXT:
Company: {business_case.facts.company_name} ({business_case.facts.industry})
Problem: {business_case.context.problem_statement}
Primary Objective: {business_case.context.primary_objective}
Budget Limit: {business_case.context.budget_limit}
Timeline: {business_case.context.timeline}
Hard Constraints: {json.dumps(business_case.context.hard_constraints)}

## CANDIDATE STRATEGIC OPTIONS:
{json.dumps([opt.model_dump() for opt in business_case.candidate_options], indent=2)}

## DEPARTMENT HEAD ANALYSES:
{dept_text}

## BOARDROOM DEBATE & CHALLENGES:
{debate_text}

## STRATEGY COMPARISON MATRIX:
{strat_text}

---
TASK: Formulate your definitive Baseline CEODecision.
Ensure you populate selected_option_id, decision_statement, rationale, rejected_options, rejection_reasons, trade_offs, risks, assumptions, implementation_steps, and at least 3 measurable business KPIs.
"""
        return generate_structured(
            prompt=prompt,
            response_model=CEODecision,
            system_prompt=CEO_SYSTEM_PROMPT,
            model=self.model,
        )

    def synthesize_adapted_decision(
        self,
        business_case: InitialBusinessCase,
        baseline_decision: CEODecision,
        surprise_event: SurpriseEvent,
        adapted_analyses: Dict[str, AgentAnalysis],
        adapted_strategy_comparison: StrategyComparison,
    ) -> CEODecision:
        """
        Produces the adapted CEO decision after a surprise condition is injected.
        """
        # Format adapted analyses
        adapted_summary_lines = []
        for role, analysis in adapted_analyses.items():
            adapted_summary_lines.append(
                f"### {role.upper()} REVISED ANALYSIS:\n"
                f"- Recommendation: {analysis.recommendation}\n"
                f"- Revised Findings: {json.dumps(analysis.findings)}\n"
                f"- Assumptions: {json.dumps(analysis.assumptions)}\n"
                f"- Risks: {json.dumps(analysis.risks)}\n"
            )
        adapted_dept_text = "\n".join(adapted_summary_lines)

        prompt = f"""
## PREVIOUS BASELINE CEO DECISION:
Selected Option: {baseline_decision.selected_option_id}
Decision Statement: {baseline_decision.decision_statement}
Baseline Rationale: {json.dumps(baseline_decision.rationale)}
Baseline KPIs: {json.dumps(baseline_decision.kpis)}

## INJECTED SURPRISE EVENT (DISRUPTIVE RUNTIME EVENT):
Title: {surprise_event.title}
Description: {surprise_event.description}
Impacted Departments: {json.dumps([dept.value for dept in surprise_event.impacted_areas])}
Parameter Deltas: {json.dumps(surprise_event.parameter_deltas)}

## RE-EVALUATED DEPARTMENT ANALYSES:
{adapted_dept_text}

## RE-EVALUATED STRATEGY COMPARISON:
Preferred Option: {adapted_strategy_comparison.preferred_option}
Evaluations: {json.dumps([e.model_dump() for e in adapted_strategy_comparison.evaluations], indent=2)}

---
TASK: Re-evaluate your strategy and formulate the Adapted CEODecision.
Explain if the original strategy remains viable or if a pivot/adjustment is required, detailing the trade-offs, updated risks, updated implementation steps, and updated KPIs (minimum 3).
"""
        return generate_structured(
            prompt=prompt,
            response_model=CEODecision,
            system_prompt=CEO_SYSTEM_PROMPT,
            model=self.model,
        )
