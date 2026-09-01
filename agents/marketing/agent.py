"""
Marketing & Sales Agent for Fireflies Swarm.

Acts as the Chief Marketing Officer (CMO) in the multi-agent decision swarm.
Evaluates Go-To-Market (GTM) strategy, Ideal Customer Profile (ICP), customer
acquisition cost (CAC), sales cycle dynamics, pricing positioning, and distribution channels.
"""

from typing import Optional, List, Dict, Any
import json
from state.schemas import (
    InitialBusinessCase,
    SurpriseEvent,
    AgentAnalysis,
    StrategicOption,
)
from utils.llm import generate_structured


MARKETING_SYSTEM_PROMPT = """You are the Chief Marketing Officer (CMO) in an executive boardroom decision swarm.
Your responsibility is to analyze business opportunities, product expansions, and go-to-market strategies from the lens of marketing, sales efficiency, customer acquisition, and competitive positioning.

Key Responsibilities & Guidelines:
1. Focus on Target Customers (ICP), Go-To-Market (GTM) channels, Customer Acquisition Cost (CAC), CAC Payback, Sales Cycle duration, and Pricing & Brand Positioning.
2. Clearly separate verified market facts (data directly in the prompt) from strategic marketing assumptions.
3. Quantify marketing risks (e.g. competitor price undercutting, channel saturation, CAC spikes, brand dilution, sales execution hurdles).
4. Evaluate every candidate strategic option and provide an unambiguous recommendation with strong supporting evidence.
5. Provide a confidence score between 0.0 and 1.0 reflecting marketing certainty given the available data.
6. Output must strictly conform to the AgentAnalysis schema.
"""


MARKETING_ADAPTATION_SYSTEM_PROMPT = """You are the Chief Marketing Officer (CMO) reviewing a sudden runtime market disruption / surprise event.
Your responsibility is to re-evaluate your original marketing analysis, identify which assumptions were broken by the disruption, and adapt your GTM strategy, positioning, and recommendation accordingly.

Key Responsibilities:
1. Analyze the specific parameter deltas and narrative of the surprise event.
2. Directly address how the disruption impacts customer demand, sales velocity, acquisition costs (CAC), and competitive dynamics.
3. Update your findings, evidence, assumptions, risks, confidence score, and primary recommendation.
4. Output must strictly conform to the AgentAnalysis schema.
"""


class MarketingAgent:
    """
    Chief Marketing Officer (CMO) Agent responsible for GTM evaluation,
    customer acquisition economics, pricing positioning, and runtime adaptation.
    """

    def __init__(self, model: Optional[str] = None):
        self.model = model
        self.agent_id = "marketing"
        self.agent_role = "Chief Marketing Officer"

    def _build_options_text(self, options: List[StrategicOption]) -> str:
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
        facts = case.facts
        context = case.context

        market_facts_text = "\n".join(f"- {f}" for f in facts.market_facts) if facts.market_facts else "- No specific market data provided"
        constraints_text = "\n".join(f"  * {c}" for c in context.hard_constraints) if context.hard_constraints else "  * None"

        prompt = f"""### BUSINESS CASE: {case.case_id} - {facts.company_name}
**Industry:** {facts.industry}

#### Baseline Financial Metrics:
{json.dumps(facts.financial_baseline, indent=2) if facts.financial_baseline else "None provided"}

#### Operational & Sales Metrics:
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

### TASK FOR CMO:
Perform a comprehensive marketing and sales evaluation:
1. Identify key marketing findings, channel dynamics, ICP fit, and CAC/payback feasibility for each option.
2. Deliver a clear, authoritative recommendation on the best strategic option.
3. List direct evidence cited from the baseline facts supporting your view.
4. Document all explicit marketing assumptions (e.g. conversion rates, pipeline velocity).
5. Identify specific marketing, competitive, and execution risks.
6. Provide your confidence score (0.0 - 1.0).

Ensure agent_id is '{self.agent_id}' and agent_role is '{self.agent_role}'.
"""
        return prompt

    def _build_adaptation_prompt(
        self,
        case: InitialBusinessCase,
        surprise: SurpriseEvent,
        previous_analysis: Optional[AgentAnalysis] = None,
    ) -> str:
        prompt = f"""### RUNTIME MARKET DISRUPTION / SURPRISE EVENT
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
### TASK FOR CMO (REVISED STRATEGY):
Given the runtime disruption and changed parameters:
1. What marketing assumptions are now invalidated or altered?
2. How does this shock impact customer acquisition, conversion rates, sales cycle, and competitor pressure?
3. Should the company pivot its recommended option or modify its GTM execution path?
4. Output your revised findings, recommendation, evidence, assumptions, risks, and updated confidence score.

Ensure agent_id is '{self.agent_id}' and agent_role is '{self.agent_role}'.
"""
        return prompt

    def _generate_fallback_analysis(self, case: InitialBusinessCase) -> AgentAnalysis:
        """
        Deterministic fallback analysis when LLM API is unavailable or offline.
        """
        options = case.candidate_options
        primary_opt = options[0] if options else None
        opt_id = primary_opt.option_id if primary_opt else "OPTION_A"
        opt_name = primary_opt.name if primary_opt else "Default Strategy"

        findings = [
            f"Evaluated market opportunity for {case.facts.company_name} in {case.facts.industry}.",
            f"Customer acquisition metrics indicate CAC of {case.facts.operational_metrics.get('customer_acquisition_cost', 'baseline levels')}.",
            f"Market data shows key growth vectors aligned with candidate options ({', '.join(o.option_id for o in options)}).",
        ]

        evidence = list(case.facts.market_facts) if case.facts.market_facts else [
            f"Operating within {case.facts.industry} with current baseline metrics."
        ]

        assumptions = [
            "Customer conversion rates will remain consistent with historical pipeline performance.",
            "GTM channel efficiency can scale without immediate diminishing returns.",
            "Sales cycle lengths remain within projected timeframes under targeted marketing.",
        ]

        risks = [
            "Competitor counter-positioning or pricing pressure eroding lead conversion.",
            "Customer acquisition cost (CAC) inflation across key outbound and digital channels.",
            "Longer enterprise sales cycles delaying ARR realization.",
        ]

        return AgentAnalysis(
            agent_id=self.agent_id,
            agent_role=self.agent_role,
            findings=findings,
            recommendation=f"Execute {opt_id} ({opt_name}) as the primary GTM vector, focusing on high-intent customer segments and rigorous CAC payback monitoring.",
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
        target_name = target_opt.name if target_opt else "Defensive Growth Strategy"

        findings = [
            f"Disruption '{surprise.title}' fundamentally shifts competitive and acquisition dynamics.",
            f"Parameter deltas indicate direct pressure on key metrics: {json.dumps(surprise.parameter_deltas)}.",
            f"Original marketing assumptions require immediate revision to protect customer pipeline and margins.",
        ]

        evidence = [
            f"Surprise Event: {surprise.description}",
            f"Impacted areas confirmed: {[d.value if hasattr(d, 'value') else str(d) for d in surprise.impacted_areas]}",
        ]

        assumptions = [
            "Market demand remains viable if positioning is adjusted to avoid head-to-head price wars.",
            "Target accounts will respond favorably to differentiated value propositions over pure price competition.",
        ]

        risks = [
            "Heightened customer churn or stalled deals due to aggressive competitor tactics.",
            "Increased CAC in affected segments necessitating reallocation of marketing spend.",
        ]

        return AgentAnalysis(
            agent_id=self.agent_id,
            agent_role=self.agent_role,
            findings=findings,
            recommendation=f"Pivot marketing focus towards {target_id} ({target_name}) to mitigate disruption impact and capture less contested customer segments.",
            evidence=evidence,
            assumptions=assumptions,
            risks=risks,
            confidence=0.75,
        )

    def analyze(
        self,
        business_case: InitialBusinessCase,
        model: Optional[str] = None,
    ) -> AgentAnalysis:
        """
        Executes initial GTM and marketing evaluation for the given business case.
        """
        selected_model = model or self.model
        prompt = self._build_analysis_prompt(business_case)

        try:
            analysis = generate_structured(
                prompt=prompt,
                response_model=AgentAnalysis,
                system_prompt=MARKETING_SYSTEM_PROMPT,
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
        Executes post-surprise marketing re-evaluation and adaptation.
        """
        selected_model = model or self.model
        prompt = self._build_adaptation_prompt(business_case, surprise, previous_analysis)

        try:
            analysis = generate_structured(
                prompt=prompt,
                response_model=AgentAnalysis,
                system_prompt=MARKETING_ADAPTATION_SYSTEM_PROMPT,
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
def run_marketing_analysis(
    business_case: InitialBusinessCase,
    model: Optional[str] = None,
) -> AgentAnalysis:
    """Run marketing analysis with a default MarketingAgent instance."""
    agent = MarketingAgent(model=model)
    return agent.analyze(business_case, model=model)


def run_marketing_adaptation(
    business_case: InitialBusinessCase,
    surprise: SurpriseEvent,
    previous_analysis: Optional[AgentAnalysis] = None,
    model: Optional[str] = None,
) -> AgentAnalysis:
    """Run marketing adaptation with a default MarketingAgent instance."""
    agent = MarketingAgent(model=model)
    return agent.adapt(business_case, surprise, previous_analysis=previous_analysis, model=model)
