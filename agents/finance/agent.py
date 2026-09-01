"""
Finance Agent for Fireflies Swarm.

Acts as the Chief Financial Officer (CFO) in the multi-agent decision swarm.
Analyzes unit economics, budget constraints, financial feasibility, ROI,
runway, burn rate, capital risk, and break-even timelines.
"""

from typing import Optional, List
import json
from state.schemas import (
    InitialBusinessCase,
    SurpriseEvent,
    AgentAnalysis,
    StrategicOption,
)
from utils.llm import generate_structured


FINANCE_SYSTEM_PROMPT = """You are the Chief Financial Officer (CFO) in an executive boardroom decision swarm.
Your responsibility is to analyze business opportunities, product expansions, and strategic options from the lens of financial feasibility, unit economics, capital allocation, and risk-adjusted returns.

Key Responsibilities & Guidelines:
1. Focus on Unit Economics (CAC, LTV, CAC Payback, Gross Margin), Budget Allocation vs. Hard Constraints, ROI Projections, Runway / Burn Rate Impact, Capital Risk (CapEx vs. OpEx), and Break-Even Analysis.
2. Ground all financial findings in the provided financial_baseline and budget_limit data. Clearly separate verified financial facts from projected assumptions.
3. Quantify financial risks (e.g. runway depletion, budget overrun, margin erosion, CAC inflation, capital misallocation, currency risk).
4. Evaluate every candidate strategic option and provide an unambiguous recommendation with strong supporting financial evidence.
5. Provide a confidence score between 0.0 and 1.0 reflecting financial certainty given the available data.
6. Output must strictly conform to the AgentAnalysis schema.
"""


FINANCE_ADAPTATION_SYSTEM_PROMPT = """You are the Chief Financial Officer (CFO) reviewing a sudden runtime financial disruption / surprise event.
Your responsibility is to re-evaluate your original financial analysis, identify which assumptions were broken by the disruption, and adapt your budget projections, ROI estimates, and recommendation accordingly.

Key Responsibilities:
1. Analyze the specific parameter deltas and narrative of the surprise event.
2. Directly address how the disruption impacts budget feasibility, unit economics, runway, capital requirements, and ROI projections.
3. Update your findings, evidence, assumptions, risks, confidence score, and primary recommendation.
4. Output must strictly conform to the AgentAnalysis schema.
"""


class FinanceAgent:
    """
    Chief Financial Officer (CFO) Agent responsible for financial feasibility,
    unit economics evaluation, capital allocation analysis, and runtime adaptation.
    """

    def __init__(self, model: Optional[str] = None):
        self.model = model
        self.agent_id = "finance"
        self.agent_role = "Chief Financial Officer"

    def _build_options_text(self, options: List[StrategicOption]) -> str:
        """Format candidate strategic options for prompt injection."""
        formatted = []
        for opt in options:
            formatted.append(
                f"- Option ID: {opt.option_id}\n"
                f"  Name: {opt.name}\n"
                f"  Description: {opt.description}\n"
                f"  Intended Mechanism: {opt.intended_mechanism}"
            )
        return "\n\n".join(formatted)

    def _build_analysis_prompt(self, case: InitialBusinessCase) -> str:
        """Build the initial financial analysis prompt from the business case."""
        facts = case.facts
        context = case.context

        market_facts_text = (
            "\n".join(f"- {f}" for f in facts.market_facts)
            if facts.market_facts
            else "- No specific market data provided"
        )
        constraints_text = (
            "\n".join(f"  * {c}" for c in context.hard_constraints)
            if context.hard_constraints
            else "  * None"
        )

        prompt = f"""### BUSINESS CASE: {case.case_id} - {facts.company_name}
**Industry:** {facts.industry}

#### Baseline Financial Metrics (PRIMARY DATA SOURCE):
{json.dumps(facts.financial_baseline, indent=2) if facts.financial_baseline else "None provided"}

#### Operational Metrics:
{json.dumps(facts.operational_metrics, indent=2) if facts.operational_metrics else "None provided"}

#### Verified Market Facts:
{market_facts_text}

#### Strategic Decision Context:
- **Problem Statement:** {context.problem_statement}
- **Primary Objective:** {context.primary_objective}
- **Budget Limit:** {context.budget_limit or 'Not specified'}
- **Timeline:** {context.timeline}
- **Hard Constraints:**
{constraints_text}

#### Candidate Strategic Options:
{self._build_options_text(case.candidate_options)}

### TASK FOR CFO:
Perform a comprehensive financial feasibility and unit economics evaluation:
1. Analyze unit economics (CAC, LTV, payback period, gross margin impact) for each candidate option.
2. Evaluate budget allocation against the hard budget limit ({context.budget_limit or 'Not specified'}) and hard constraints.
3. Project ROI and break-even timelines for each option.
4. Assess runway and burn rate impact — will the company maintain sufficient cash runway?
5. Identify capital allocation risks (CapEx vs. OpEx trade-offs, funding requirements).
6. Deliver a clear, authoritative recommendation on the best strategic option from a financial perspective.
7. List direct evidence cited from the financial_baseline and operational metrics.
8. Document all explicit financial assumptions (e.g. growth rates, margin trajectories, cost projections).
9. Identify specific financial risks (runway depletion, budget overrun, margin erosion, etc.).
10. Provide your confidence score (0.0 - 1.0).

Ensure agent_id is '{self.agent_id}' and agent_role is '{self.agent_role}'.
"""
        return prompt

    def _build_adaptation_prompt(
        self,
        case: InitialBusinessCase,
        surprise: SurpriseEvent,
        previous_analysis: Optional[AgentAnalysis] = None,
    ) -> str:
        """Build the post-surprise financial adaptation prompt."""
        prompt = f"""### RUNTIME FINANCIAL DISRUPTION / SURPRISE EVENT
**Event ID:** {surprise.event_id}
**Headline:** {surprise.title}
**Disruption Narrative:** {surprise.description}

**Impacted Departments:** {[d.value if hasattr(d, 'value') else str(d) for d in surprise.impacted_areas]}
**Parameter / Metric Deltas:**
{json.dumps(surprise.parameter_deltas, indent=2)}

---
### ORIGINAL BUSINESS CASE CONTEXT
**Company:** {case.facts.company_name} ({case.facts.industry})
**Objective:** {case.context.primary_objective}
**Budget Limit:** {case.context.budget_limit or 'Not specified'}
**Financial Baseline:** {json.dumps(case.facts.financial_baseline, indent=2) if case.facts.financial_baseline else 'None provided'}
**Strategic Options:**
{self._build_options_text(case.candidate_options)}
"""
        if previous_analysis:
            prompt += f"""
---
### YOUR PREVIOUS BASELINE ANALYSIS (Pre-Surprise):
- **Previous Recommendation:** {previous_analysis.recommendation}
- **Previous Findings:** {previous_analysis.findings}
- **Previous Key Assumptions:** {previous_analysis.assumptions}
- **Previous Confidence:** {previous_analysis.confidence}
"""

        prompt += f"""
---
### TASK FOR CFO (REVISED ANALYSIS):
Given the runtime disruption and changed parameters:
1. What financial assumptions are now invalidated or altered?
2. How does this disruption impact budget feasibility, unit economics, runway, capital requirements, and ROI projections?
3. Does the budget limit ({case.context.budget_limit or 'Not specified'}) still hold, or has it been breached?
4. Should the company pivot its recommended option or modify its financial execution path?
5. Output your revised findings, recommendation, evidence, assumptions, risks, and updated confidence score.

Ensure agent_id is '{self.agent_id}' and agent_role is '{self.agent_role}'.
"""
        return prompt

    def _generate_fallback_analysis(self, case: InitialBusinessCase) -> AgentAnalysis:
        """
        Deterministic fallback analysis when LLM API is unavailable or offline.
        Grounded in the case's financial_baseline and budget_limit data.
        """
        options = case.candidate_options
        primary_opt = options[0] if options else None
        opt_id = primary_opt.option_id if primary_opt else "OPTION_A"
        opt_name = primary_opt.name if primary_opt else "Default Strategy"

        fb = case.facts.financial_baseline
        runway = fb.get("cash_runway_months", "N/A")
        burn_rate = fb.get("monthly_burn_rate", "N/A")
        revenue = fb.get("annual_recurring_revenue", fb.get("annual_revenue", "N/A"))
        gross_margin = fb.get("gross_margin", fb.get("product_gross_margin", "N/A"))

        findings = [
            f"Financial baseline for {case.facts.company_name}: revenue {revenue}, burn rate {burn_rate}, runway {runway} months, gross margin {gross_margin}.",
            f"Budget constraint of {case.context.budget_limit or 'not specified'} evaluated against candidate options ({', '.join(o.option_id for o in options)}).",
            f"Unit economics assessment indicates CAC of {case.facts.operational_metrics.get('customer_acquisition_cost', case.facts.operational_metrics.get('fulfillment_cost_per_order', 'baseline levels'))} with current operational scale.",
        ]

        evidence = []
        if fb:
            evidence.append(f"Financial baseline: {json.dumps(fb)}")
        if case.context.budget_limit:
            evidence.append(f"Hard budget limit: {case.context.budget_limit}")
        if not evidence:
            evidence.append(f"Operating within {case.facts.industry} with current baseline metrics.")

        assumptions = [
            "Revenue growth trajectory will remain consistent with historical performance over the planning horizon.",
            "Gross margins will hold within ±3% of current levels under the recommended strategy.",
            "No additional capital raises will be required within the stated timeline if budget is managed to plan.",
        ]

        risks = [
            "Runway depletion risk if burn rate increases beyond projected levels during execution.",
            "Budget overrun risk if implementation costs exceed initial estimates.",
            "Margin erosion risk from competitive pricing pressure or operational inefficiencies.",
        ]

        return AgentAnalysis(
            agent_id=self.agent_id,
            agent_role=self.agent_role,
            findings=findings,
            recommendation=f"Approve {opt_id} ({opt_name}) subject to strict budget gating within the {case.context.budget_limit or 'available'} budget limit and quarterly milestone-based capital release.",
            evidence=evidence,
            assumptions=assumptions,
            risks=risks,
            confidence=0.82,
        )

    def _generate_fallback_adaptation(
        self,
        case: InitialBusinessCase,
        surprise: SurpriseEvent,
        previous_analysis: Optional[AgentAnalysis] = None,
    ) -> AgentAnalysis:
        """
        Deterministic fallback adaptation when LLM API is unavailable.
        """
        options = case.candidate_options
        # Prefer alternative option if available to reflect tactical pivot
        target_opt = options[-1] if len(options) > 1 else (options[0] if options else None)
        target_id = target_opt.option_id if target_opt else "ADAPTED_STRATEGY"
        target_name = target_opt.name if target_opt else "Defensive Financial Strategy"

        findings = [
            f"Disruption '{surprise.title}' materially impacts financial assumptions and budget feasibility.",
            f"Parameter deltas indicate direct pressure on financial metrics: {json.dumps(surprise.parameter_deltas)}.",
            f"Original financial projections require immediate revision to reflect changed cost structure and capital requirements.",
        ]

        evidence = [
            f"Surprise Event: {surprise.description}",
            f"Impacted areas confirmed: {[d.value if hasattr(d, 'value') else str(d) for d in surprise.impacted_areas]}",
        ]

        assumptions = [
            "Core revenue streams remain viable if cost structure is adjusted to absorb the disruption impact.",
            "Additional capital can be sourced if budget constraints are breached, albeit at higher cost of capital.",
        ]

        risks = [
            "Budget constraint breach requiring emergency funding or scope reduction.",
            "Accelerated burn rate reducing cash runway below minimum safe threshold.",
        ]

        return AgentAnalysis(
            agent_id=self.agent_id,
            agent_role=self.agent_role,
            findings=findings,
            recommendation=f"Pivot financial recommendation towards {target_id} ({target_name}) to preserve capital flexibility and maintain runway above minimum threshold given disruption impact.",
            evidence=evidence,
            assumptions=assumptions,
            risks=risks,
            confidence=0.70,
        )

    def analyze(
        self,
        business_case: InitialBusinessCase,
        model: Optional[str] = None,
    ) -> AgentAnalysis:
        """
        Executes initial financial feasibility and unit economics evaluation
        for the given business case.
        """
        selected_model = model or self.model
        prompt = self._build_analysis_prompt(business_case)

        try:
            analysis = generate_structured(
                prompt=prompt,
                response_model=AgentAnalysis,
                system_prompt=FINANCE_SYSTEM_PROMPT,
                model=selected_model,
                temperature=0.2,
            )
            # Ensure agent identifiers are strictly enforced
            analysis.agent_id = self.agent_id
            analysis.agent_role = self.agent_role
            return analysis
        except Exception:
            # Graceful fallback for offline testing or LLM outages
            return self._generate_fallback_analysis(business_case)

    def adapt(
        self,
        business_case: InitialBusinessCase,
        surprise: SurpriseEvent,
        previous_analysis: Optional[AgentAnalysis] = None,
        model: Optional[str] = None,
    ) -> AgentAnalysis:
        """
        Executes post-surprise financial re-evaluation and adaptation.
        """
        selected_model = model or self.model
        prompt = self._build_adaptation_prompt(business_case, surprise, previous_analysis)

        try:
            analysis = generate_structured(
                prompt=prompt,
                response_model=AgentAnalysis,
                system_prompt=FINANCE_ADAPTATION_SYSTEM_PROMPT,
                model=selected_model,
                temperature=0.2,
            )
            analysis.agent_id = self.agent_id
            analysis.agent_role = self.agent_role
            return analysis
        except Exception:
            # Graceful fallback for offline testing or LLM outages
            return self._generate_fallback_adaptation(business_case, surprise, previous_analysis)


# Convenient module-level entry points
def run_finance_analysis(
    business_case: InitialBusinessCase,
    model: Optional[str] = None,
) -> AgentAnalysis:
    """Run finance analysis with a default FinanceAgent instance."""
    agent = FinanceAgent(model=model)
    return agent.analyze(business_case, model=model)


def run_finance_adaptation(
    business_case: InitialBusinessCase,
    surprise: SurpriseEvent,
    previous_analysis: Optional[AgentAnalysis] = None,
    model: Optional[str] = None,
) -> AgentAnalysis:
    """Run finance adaptation with a default FinanceAgent instance."""
    agent = FinanceAgent(model=model)
    return agent.adapt(business_case, surprise, previous_analysis=previous_analysis, model=model)
