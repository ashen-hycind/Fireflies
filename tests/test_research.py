"""
Unit & Integration tests for Research Agent (Person B).
Covers standard workflows, edge cases, surprise adaptations, and error resilience.
"""

import pytest
from unittest.mock import patch

from state.schemas import (
    InitialBusinessCase,
    BusinessFacts,
    DecisionContext,
    StrategicOption,
    SurpriseEvent,
    AgentAnalysis,
    Department,
)
from agents.research.agent import (
    ResearchAgent,
    run_research_analysis,
    run_research_adaptation,
)
from tests.mock_cases import (
    SAAS_EXPANSION_CASE,
    SAAS_SURPRISE_EVENT,
    D2C_LOGISTICS_CASE,
    D2C_SURPRISE_EVENT,
)


class TestResearchAgent:
    """Test suite for ResearchAgent role, prompt formatting, analysis, and adaptation."""

    def test_agent_initialization(self):
        agent = ResearchAgent()
        assert agent.agent_id == "research"
        assert agent.agent_role == "Chief Research Officer"

    def test_agent_initialization_with_custom_model(self):
        agent = ResearchAgent(model="gemini-2.0-flash")
        assert agent.model == "gemini-2.0-flash"

    def test_prompt_includes_key_context(self):
        agent = ResearchAgent()
        prompt = agent._build_analysis_prompt(SAAS_EXPANSION_CASE)

        assert "CloudMetrics AI" in prompt
        assert "OPTION_A" in prompt
        assert "OPTION_B" in prompt
        assert "CRO" in prompt
        assert "B2B Enterprise SaaS" in prompt
        # Verify market facts are included
        assert "34% YoY" in prompt or "observability" in prompt.lower()

    def test_prompt_includes_market_facts(self):
        agent = ResearchAgent()
        prompt = agent._build_analysis_prompt(SAAS_EXPANSION_CASE)

        for fact in SAAS_EXPANSION_CASE.facts.market_facts:
            assert fact in prompt

    def test_prompt_includes_budget_and_constraints(self):
        agent = ResearchAgent()
        prompt = agent._build_analysis_prompt(SAAS_EXPANSION_CASE)

        assert "$3.5M" in prompt
        assert "SOC2" in prompt or "GDPR" in prompt

    def test_adaptation_prompt_includes_surprise(self):
        agent = ResearchAgent()
        prompt = agent._build_adaptation_prompt(
            case=SAAS_EXPANSION_CASE,
            surprise=SAAS_SURPRISE_EVENT,
        )

        assert "DataWatch Slashes Enterprise Pricing" in prompt
        assert "us_expected_cac" in prompt or "us_sales_cycle_days" in prompt
        assert "TASK FOR CRO" in prompt

    def test_adaptation_prompt_includes_previous_analysis(self):
        agent = ResearchAgent()
        previous = agent._generate_fallback_analysis(SAAS_EXPANSION_CASE)
        prompt = agent._build_adaptation_prompt(
            case=SAAS_EXPANSION_CASE,
            surprise=SAAS_SURPRISE_EVENT,
            previous_analysis=previous,
        )

        assert "PREVIOUS BASELINE ANALYSIS" in prompt
        assert previous.recommendation in prompt

    def test_fallback_analysis_schema_validity(self):
        agent = ResearchAgent()
        analysis = agent._generate_fallback_analysis(SAAS_EXPANSION_CASE)

        assert isinstance(analysis, AgentAnalysis)
        assert analysis.agent_id == "research"
        assert analysis.agent_role == "Chief Research Officer"
        assert len(analysis.findings) > 0
        assert len(analysis.evidence) > 0
        assert len(analysis.assumptions) > 0
        assert len(analysis.risks) > 0
        assert analysis.confidence is not None
        assert 0.0 <= analysis.confidence <= 1.0
        assert len(analysis.recommendation) > 10

    def test_fallback_analysis_grounded_in_case_data(self):
        """Verify fallback uses actual case data, not hardcoded strings."""
        agent = ResearchAgent()
        analysis = agent._generate_fallback_analysis(SAAS_EXPANSION_CASE)

        assert "CloudMetrics AI" in analysis.findings[0]
        # Evidence should contain actual market facts
        for ev in analysis.evidence:
            assert ev in SAAS_EXPANSION_CASE.facts.market_facts or "baseline" in ev.lower()

    def test_fallback_adaptation_schema_validity(self):
        agent = ResearchAgent()
        prev = agent._generate_fallback_analysis(SAAS_EXPANSION_CASE)
        adapted = agent._generate_fallback_adaptation(
            case=SAAS_EXPANSION_CASE,
            surprise=SAAS_SURPRISE_EVENT,
            previous_analysis=prev,
        )

        assert isinstance(adapted, AgentAnalysis)
        assert adapted.agent_id == "research"
        assert len(adapted.findings) > 0
        assert len(adapted.risks) > 0
        assert 0.0 <= adapted.confidence <= 1.0

    def test_fallback_adaptation_references_surprise(self):
        agent = ResearchAgent()
        adapted = agent._generate_fallback_adaptation(
            case=SAAS_EXPANSION_CASE,
            surprise=SAAS_SURPRISE_EVENT,
        )

        # At least one finding should reference the surprise event
        surprise_referenced = any(
            SAAS_SURPRISE_EVENT.title in f for f in adapted.findings
        )
        assert surprise_referenced

    def test_analyze_with_mocked_llm(self):
        mock_output = AgentAnalysis(
            agent_id="research",
            agent_role="Chief Research Officer",
            findings=[
                "EU mid-market for observability is underserved with 3 viable competitors vs. 7 in US.",
                "AI-assisted observability demand grew 34% YoY, confirming secular tailwind.",
            ],
            recommendation="Execute OPTION_A: Aggressive European Mid-Market Expansion based on favorable competitive gap.",
            evidence=[
                "Enterprise demand for AI-assisted observability grew 34% YoY.",
                "European market has lower competition for mid-market tier.",
            ],
            assumptions=[
                "EU regulatory compliance (GDPR) will not delay market entry beyond 3 months.",
                "Competitive landscape in EU remains stable over the 12-month horizon.",
            ],
            risks=[
                "Regulatory change risk in EU data sovereignty laws.",
                "Incumbents may expand into EU within the planning period.",
            ],
            confidence=0.85,
        )

        with patch("agents.research.agent.generate_structured", return_value=mock_output):
            result = run_research_analysis(SAAS_EXPANSION_CASE)
            assert result.agent_id == "research"
            assert result.agent_role == "Chief Research Officer"
            assert result.confidence == 0.85
            assert "OPTION_A" in result.recommendation

    def test_adapt_with_mocked_llm(self):
        mock_adapted = AgentAnalysis(
            agent_id="research",
            agent_role="Chief Research Officer",
            findings=[
                "DataWatch 40% price cut reshapes US competitive dynamics significantly.",
                "EU market remains unaffected by US pricing war — competitive gap persists.",
            ],
            recommendation="Double down on OPTION_A (EU expansion) as US market becomes a price war zone.",
            evidence=[
                "DataWatch announced 40% price reduction on multi-year enterprise deals.",
            ],
            assumptions=[
                "DataWatch will not immediately replicate pricing strategy in EU.",
            ],
            risks=[
                "DataWatch may follow into EU market within 12 months.",
            ],
            confidence=0.82,
        )

        with patch("agents.research.agent.generate_structured", return_value=mock_adapted):
            result = run_research_adaptation(
                business_case=SAAS_EXPANSION_CASE,
                surprise=SAAS_SURPRISE_EVENT,
            )
            assert result.agent_id == "research"
            assert "OPTION_A" in result.recommendation
            assert result.confidence == 0.82

    def test_d2c_case_generalization(self):
        """Test with D2C logistics case to ensure no hardcoding."""
        agent = ResearchAgent()
        analysis = agent.analyze(D2C_LOGISTICS_CASE)

        assert isinstance(analysis, AgentAnalysis)
        assert analysis.agent_id == "research"
        assert len(analysis.findings) > 0
        assert len(analysis.evidence) > 0

    def test_d2c_adaptation(self):
        """Test adaptation with D2C surprise event."""
        agent = ResearchAgent()
        analysis = agent.adapt(D2C_LOGISTICS_CASE, D2C_SURPRISE_EVENT)

        assert isinstance(analysis, AgentAnalysis)
        assert analysis.agent_id == "research"
        assert len(analysis.findings) > 0

    def test_sparse_case_no_crashes(self):
        """Test minimal/empty metrics case to ensure zero NoneType or KeyError crashes."""
        sparse_case = InitialBusinessCase(
            case_id="case_stealth_001",
            facts=BusinessFacts(
                company_name="Stealth Labs",
                industry="Generative AI Tooling",
                financial_baseline={},
                operational_metrics={},
                market_facts=[],
            ),
            context=DecisionContext(
                problem_statement="Determine strategic positioning for pre-revenue product.",
                primary_objective="Establish market leadership in AI code generation.",
                timeline="6 months",
                hard_constraints=[],
            ),
            candidate_options=[
                StrategicOption(
                    option_id="OPTION_A",
                    name="Open Source Community Play",
                    description="Launch open-source SDK to build developer community.",
                    intended_mechanism="Organic community-driven adoption.",
                ),
                StrategicOption(
                    option_id="OPTION_B",
                    name="Enterprise Direct Sales",
                    description="Target Fortune 500 engineering teams directly.",
                    intended_mechanism="High-touch enterprise sales.",
                ),
            ],
        )

        agent = ResearchAgent()
        prompt = agent._build_analysis_prompt(sparse_case)
        assert "None provided" in prompt or "Stealth Labs" in prompt

        analysis = agent.analyze(sparse_case)
        assert isinstance(analysis, AgentAnalysis)
        assert analysis.agent_id == "research"
        assert len(analysis.findings) > 0

    def test_single_option_case(self):
        """Test with only one candidate option."""
        single_option_case = InitialBusinessCase(
            case_id="case_single_001",
            facts=BusinessFacts(
                company_name="MonoPath Inc",
                industry="Logistics Tech",
            ),
            context=DecisionContext(
                problem_statement="Should we expand to Asia-Pacific?",
                primary_objective="Establish APAC presence.",
                timeline="12 months",
            ),
            candidate_options=[
                StrategicOption(
                    option_id="OPTION_A",
                    name="APAC Direct Entry",
                    description="Open Singapore office.",
                    intended_mechanism="Direct market entry.",
                ),
            ],
        )

        agent = ResearchAgent()
        analysis = agent._generate_fallback_analysis(single_option_case)
        assert isinstance(analysis, AgentAnalysis)
        assert "OPTION_A" in analysis.recommendation

    def test_graceful_fallback_on_llm_exception(self):
        with patch("agents.research.agent.generate_structured", side_effect=Exception("API Timeout")):
            agent = ResearchAgent()
            result = agent.analyze(SAAS_EXPANSION_CASE)
            assert isinstance(result, AgentAnalysis)
            assert result.agent_id == "research"
            assert len(result.findings) > 0

    def test_graceful_fallback_on_adapt_exception(self):
        with patch("agents.research.agent.generate_structured", side_effect=Exception("Rate Limited")):
            agent = ResearchAgent()
            result = agent.adapt(SAAS_EXPANSION_CASE, SAAS_SURPRISE_EVENT)
            assert isinstance(result, AgentAnalysis)
            assert result.agent_id == "research"
            assert len(result.findings) > 0

    def test_regulatory_disruption_adaptation(self):
        """Test surprise event involving regulatory change."""
        regulatory_surprise = SurpriseEvent(
            event_id="surprise_reg_001",
            title="EU Imposes Strict AI Compliance Requirements",
            description="New EU AI Act mandates extensive model auditing and transparency requirements, increasing compliance costs by 40%.",
            impacted_areas=[Department.RESEARCH],
            parameter_deltas={
                "compliance_cost_increase": "40%",
                "market_entry_delay": "4 months",
            },
        )

        agent = ResearchAgent()
        adapted = agent._generate_fallback_adaptation(
            case=SAAS_EXPANSION_CASE,
            surprise=regulatory_surprise,
        )

        assert isinstance(adapted, AgentAnalysis)
        assert "EU Imposes Strict AI Compliance" in adapted.findings[0]
        assert 0.0 <= adapted.confidence <= 1.0
