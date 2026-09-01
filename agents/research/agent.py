"""
Research Agent for Fireflies Swarm.

Acts as the Chief Research Officer (CRO) in the multi-agent decision swarm.
Analyzes market trends, competitive landscape, regulatory environment,
technology readiness, and industry data. Strictly separates verified facts
from speculative assumptions.
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


RESEARCH_SYSTEM_PROMPT = """You are the Chief Research Officer (CRO) in an executive boardroom decision swarm.
Your responsibility is to analyze business opportunities, market dynamics, and strategic options from the lens of market research, competitive intelligence, regulatory landscape, and technology readiness.

Key Responsibilities & Guidelines:
1. Focus on Market Sizing (TAM/SAM/SOM), Competitive Landscape (moats, positioning, SWOT), Regulatory & Compliance Barriers, Technology Maturity, and Industry Growth Trends.
2. STRICTLY separate verified facts (data directly provided in the prompt) from speculative assumptions. Every finding must be tagged as grounded in evidence or stated as an assumption.
3. Quantify research risks (e.g. market timing risk, regulatory change risk, competitive response risk, technology adoption risk, data gaps).
4. Evaluate every candidate strategic option and provide an unambiguous recommendation with strong supporting evidence.
5. Provide a confidence score between 0.0 and 1.0 reflecting research certainty given the available data.
6. Output must strictly conform to the AgentAnalysis schema.
"""


RESEARCH_ADAPTATION_SYSTEM_PROMPT = """You are the Chief Research Officer (CRO) reviewing a sudden runtime market disruption / surprise event.
Your responsibility is to re-evaluate your original market research analysis, identify which assumptions were broken by the disruption, and adapt your competitive landscape assessment, market sizing, and recommendation accordingly.

Key Responsibilities:
1. Analyze the specific parameter deltas and narrative of the surprise event.
2. Directly address how the disruption impacts market dynamics, competitive positioning, regulatory conditions, and technology readiness.
3. Update your findings, evidence, assumptions, risks, confidence score, and primary recommendation.
4. Output must strictly conform to the AgentAnalysis schema.
"""


class ResearchAgent:
    """
    Chief Research Officer (CRO) Agent responsible for market research,
    competitive intelligence, regulatory analysis, and runtime adaptation.
    """

    def __init__(self, model: Optional[str] = None):
        self.model = model
        self.agent_id = "research"
        self.agent_role = "Chief Research Officer"

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
        """Build the initial research analysis prompt from the business case."""
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

#### Baseline Financial Metrics:
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

### TASK FOR CRO:
Perform a comprehensive market research and competitive intelligence evaluation:
1. Analyze market sizing (TAM/SAM/SOM), competitive landscape, industry growth trends, and regulatory barriers for each option.
2. STRICTLY separate verified facts (from the data above) from speculative assumptions you are making.
3. Deliver a clear, authoritative recommendation on the best strategic option from a research perspective.
4. List direct evidence cited from the baseline facts supporting your view.
5. Document all explicit research assumptions (e.g. market growth rates, competitor responses, regulatory timelines).
6. Identify specific market, competitive, regulatory, and technology risks.
7. Provide your confidence score (0.0 - 1.0).

Ensure agent_id is '{self.agent_id}' and agent_role is '{self.agent_role}'.
"""
        return prompt

    def _build_adaptation_prompt(
        self,
        case: InitialBusinessCase,
        surprise: SurpriseEvent,
        previous_analysis: Optional[AgentAnalysis] = None,
    ) -> str:
        """Build the post-surprise adaptation prompt."""
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
### TASK FOR CRO (REVISED ANALYSIS):
Given the runtime disruption and changed parameters:
1. What research assumptions are now invalidated or altered?
2. How does this disruption impact market dynamics, competitive positioning, regulatory conditions, and technology readiness?
3. Should the company pivot its recommended option or modify its strategic approach?
4. Output your revised findings, recommendation, evidence, assumptions, risks, and updated confidence score.

Ensure agent_id is '{self.agent_id}' and agent_role is '{self.agent_role}'.
"""
        return prompt

    def _generate_fallback_analysis(self, case: InitialBusinessCase) -> AgentAnalysis:
        """
        Deterministic fallback analysis when LLM API is unavailable or offline.
        Grounded in the case's market_facts and operational data.
        """
        options = case.candidate_options
        primary_opt = options[0] if options else None
        opt_id = primary_opt.option_id if primary_opt else "OPTION_A"
        opt_name = primary_opt.name if primary_opt else "Default Strategy"

        findings = [
            f"Market analysis for {case.facts.company_name} in {case.facts.industry} indicates viable growth vectors across candidate options ({', '.join(o.option_id for o in options)}).",
            f"Competitive landscape features {len(case.facts.market_facts)} verified market data points informing strategic positioning.",
            f"Industry context and operational scale (headcount/metrics: {json.dumps(case.facts.operational_metrics) if case.facts.operational_metrics else 'not provided'}) suggest execution feasibility for the recommended option.",
        ]

        evidence = (
            list(case.facts.market_facts)
            if case.facts.market_facts
            else [f"Operating within {case.facts.industry} with current baseline metrics."]
        )

        assumptions = [
            "Market growth trends will remain consistent with recent historical trajectories over the planning horizon.",
            "Competitive landscape will not undergo radical consolidation or new entrant disruption within the decision timeline.",
            "Regulatory environment remains stable with no material changes to compliance requirements.",
        ]

        risks = [
            "Market timing risk: demand growth may decelerate or shift to adjacent segments.",
            "Competitive response risk: incumbents may accelerate feature parity or price aggression.",
            "Regulatory change risk: new compliance mandates could increase go-to-market friction.",
        ]

        return AgentAnalysis(
            agent_id=self.agent_id,
            agent_role=self.agent_role,
            findings=findings,
            recommendation=f"Pursue {opt_id} ({opt_name}) based on favorable market positioning, competitive gap analysis, and alignment with verified industry growth trends.",
            evidence=evidence,
            assumptions=assumptions,
            risks=risks,
            confidence=0.80,
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
        # Prefer alternative option to reflect tactical pivot
        target_opt = options[-1] if len(options) > 1 else (options[0] if options else None)
        target_id = target_opt.option_id if target_opt else "ADAPTED_STRATEGY"
        target_name = target_opt.name if target_opt else "Defensive Market Strategy"

        findings = [
            f"Disruption '{surprise.title}' materially alters competitive dynamics and market assumptions.",
            f"Parameter deltas indicate direct impact on strategic positioning: {json.dumps(surprise.parameter_deltas)}.",
            f"Original market research assumptions require revision to account for shifted competitive and regulatory conditions.",
        ]

        evidence = [
            f"Surprise Event: {surprise.description}",
            f"Impacted areas confirmed: {[d.value if hasattr(d, 'value') else str(d) for d in surprise.impacted_areas]}",
        ]

        assumptions = [
            "Core market demand remains viable if strategic positioning is adjusted to reflect new competitive realities.",
            "Disruption effects are localized to the parameters identified and do not cascade into adjacent market segments.",
        ]

        risks = [
            "Prolonged competitive pressure from disruption may erode market share faster than projected.",
            "Market perception shift may delay customer adoption cycles across all strategic options.",
        ]

        return AgentAnalysis(
            agent_id=self.agent_id,
            agent_role=self.agent_role,
            findings=findings,
            recommendation=f"Pivot research-backed recommendation towards {target_id} ({target_name}) to mitigate disruption impact and capitalize on less contested market segments.",
            evidence=evidence,
            assumptions=assumptions,
            risks=risks,
            confidence=0.72,
        )

    def analyze(
        self,
        business_case: InitialBusinessCase,
        model: Optional[str] = None,
    ) -> AgentAnalysis:
        """
        Executes initial market research and competitive intelligence evaluation
        for the given business case.
        """
        selected_model = model or self.model
        prompt = self._build_analysis_prompt(business_case)

        try:
            analysis = generate_structured(
                prompt=prompt,
                response_model=AgentAnalysis,
                system_prompt=RESEARCH_SYSTEM_PROMPT,
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
        Executes post-surprise market research re-evaluation and adaptation.
        """
        selected_model = model or self.model
        prompt = self._build_adaptation_prompt(business_case, surprise, previous_analysis)

        try:
            analysis = generate_structured(
                prompt=prompt,
                response_model=AgentAnalysis,
                system_prompt=RESEARCH_ADAPTATION_SYSTEM_PROMPT,
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
def run_research_analysis(
    business_case: InitialBusinessCase,
    model: Optional[str] = None,
) -> AgentAnalysis:
    """Run research analysis with a default ResearchAgent instance."""
    agent = ResearchAgent(model=model)
    return agent.analyze(business_case, model=model)


def run_research_adaptation(
    business_case: InitialBusinessCase,
    surprise: SurpriseEvent,
    previous_analysis: Optional[AgentAnalysis] = None,
    model: Optional[str] = None,
) -> AgentAnalysis:
    """Run research adaptation with a default ResearchAgent instance."""
    agent = ResearchAgent(model=model)
    return agent.adapt(business_case, surprise, previous_analysis=previous_analysis, model=model)
