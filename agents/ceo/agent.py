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

    def _generate_fallback_baseline(
        self,
        business_case: InitialBusinessCase,
        department_analyses: Dict[str, AgentAnalysis],
        strategy_comparison: StrategyComparison,
    ) -> CEODecision:
        """Deterministic baseline decision fallback when LLM is offline or encounters error."""
        selected_id = strategy_comparison.preferred_option if strategy_comparison else business_case.candidate_options[0].option_id
        selected_opt = next((o for o in business_case.candidate_options if o.option_id == selected_id), business_case.candidate_options[0])
        rejected_opts = [o.option_id for o in business_case.candidate_options if o.option_id != selected_id]

        return CEODecision(
            selected_option_id=selected_id,
            decision_statement=f"Executive Decision: Execute {selected_id} ({selected_opt.name}) to achieve '{business_case.context.primary_objective}'.",
            rationale=[
                f"Supported by multi-department consensus: {selected_opt.intended_mechanism}.",
                f"Aligned with operating constraints within {business_case.context.timeline} timeframe.",
                f"Financial feasibility validated against {business_case.context.budget_limit or 'baseline reserves'}.",
            ],
            rejected_options=rejected_opts,
            rejection_reasons=[
                f"Alternative {opt_id} carries higher competitive friction or slower payback relative to primary strategic objective."
                for opt_id in rejected_opts
            ],
            trade_offs=[
                "Accepting upfront execution focus in exchange for high-margin defensible market leadership.",
                "Deprioritizing secondary product iterations during the initial rollout phase.",
            ],
            risks=[
                "Customer acquisition velocity lag in initial quarter.",
                "Competitor pricing pressure or aggressive counter-marketing.",
            ],
            assumptions=[
                f"Market demand in {business_case.facts.industry} continues along current growth vector.",
                "CAC payback remains within targets under disciplined channel allocation.",
            ],
            implementation_steps=[
                f"Phase 1 (Months 1-3): Finalize operational readiness and resource allocation for {selected_opt.name}.",
                f"Phase 2 (Months 4-8): Launch strategic rollout with strict monthly milestone gating.",
                f"Phase 3 (Months 9-12): Scale operations, evaluate ROI, and optimize unit economics.",
            ],
            kpis=[
                f"ARR / Revenue Growth: +35% YoY or reaching targets defined in {business_case.context.primary_objective}",
                "CAC Payback Period: < 12 months across primary acquisition channels",
                "Operating Net Margin / Runway: Maintain > 12 months cash runway post-execution",
            ],
        )

    def _generate_fallback_adapted(
        self,
        business_case: InitialBusinessCase,
        baseline_decision: CEODecision,
        surprise_event: SurpriseEvent,
        adapted_analyses: Dict[str, AgentAnalysis],
        adapted_strategy_comparison: StrategyComparison,
    ) -> CEODecision:
        """Deterministic adapted decision fallback."""
        selected_id = adapted_strategy_comparison.preferred_option if adapted_strategy_comparison else baseline_decision.selected_option_id
        selected_opt = next((o for o in business_case.candidate_options if o.option_id == selected_id), business_case.candidate_options[0])

        return CEODecision(
            selected_option_id=selected_id,
            decision_statement=f"Executive Adaptation: Reaffirm strategy {selected_id} with tactical pivot to neutralize surprise event: '{surprise_event.title}'.",
            rationale=[
                f"Surprise '{surprise_event.title}' required immediate assumption adjustments across impacted areas.",
                f"Core value proposition of {selected_opt.name} remains resilient against parameter shifts.",
                "Tactical spending gated and redirected towards high-conversion, defensible channels.",
            ],
            rejected_options=[o.option_id for o in business_case.candidate_options if o.option_id != selected_id],
            rejection_reasons=[
                "Alternative options become more capital-vulnerable under the changed market conditions."
            ],
            trade_offs=[
                "Short-term margin compression accepted to secure market share during disruption.",
                "Accelerated execution timeline to outpace competitor retaliation.",
            ],
            risks=[
                f"Extended impact from {surprise_event.title} requiring secondary contingency budgets.",
            ],
            assumptions=[
                "Disruption effects stabilize within the revised tactical planning window.",
            ],
            implementation_steps=[
                f"Step 1: Implement defensive measures addressing {surprise_event.title}.",
                "Step 2: Re-align departmental budgets with updated parameter deltas.",
                "Step 3: Execute accelerated rollout with weekly executive performance reviews.",
            ],
            kpis=[
                f"Adjusted Target ROI: > 2.0x on newly allocated funds",
                "Customer Retention Rate: > 92% throughout disruption window",
                "Defensive Margin Floor: Maintain gross margins above minimum operational threshold",
            ],
        )

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

        debate_lines = []
        for msg in debate_messages:
            to_str = f" to {msg.to_agent}" if msg.to_agent else ""
            ref_str = f" [Claim: {msg.referenced_claim}]" if msg.referenced_claim else ""
            debate_lines.append(f"[{msg.from_agent}{to_str} ({msg.message_type})]{ref_str}: {msg.content}")
        debate_text = "\n".join(debate_lines) if debate_lines else "No debate logged."

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
        try:
            return generate_structured(
                prompt=prompt,
                response_model=CEODecision,
                system_prompt=CEO_SYSTEM_PROMPT,
                model=self.model,
            )
        except Exception:
            return self._generate_fallback_baseline(business_case, department_analyses, strategy_comparison)

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
        try:
            return generate_structured(
                prompt=prompt,
                response_model=CEODecision,
                system_prompt=CEO_SYSTEM_PROMPT,
                model=self.model,
            )
        except Exception:
            return self._generate_fallback_adapted(
                business_case,
                baseline_decision,
                surprise_event,
                adapted_analyses,
                adapted_strategy_comparison,
            )
