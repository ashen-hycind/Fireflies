"""
Unit & Integration tests for Finance Agent (Person B).
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
from agents.finance.agent import (
    FinanceAgent,
    run_finance_analysis,
    run_finance_adaptation,
)
from tests.mock_cases import (
    SAAS_EXPANSION_CASE,
    SAAS_SURPRISE_EVENT,
    D2C_LOGISTICS_CASE,
    D2C_SURPRISE_EVENT,
)


class TestFinanceAgent:
    """Test suite for FinanceAgent role, prompt formatting, analysis, and adaptation."""

    def test_agent_initialization(self):
        agent = FinanceAgent()
        assert agent.agent_id == "finance"
        assert agent.agent_role == "Chief Financial Officer"

    def test_agent_initialization_with_custom_model(self):
        agent = FinanceAgent(model="gemini-2.0-flash")
        assert agent.model == "gemini-2.0-flash"

    def test_prompt_includes_financial_data(self):
        agent = FinanceAgent()
        prompt = agent._build_analysis_prompt(SAAS_EXPANSION_CASE)

        assert "CloudMetrics AI" in prompt
        # Verify financial_baseline values are surfaced
        assert "$8.5M" in prompt or "8.5M" in prompt
        assert "$220,000" in prompt or "220,000" in prompt
        assert "78%" in prompt
        # Verify budget_limit is prominent
        assert "$3.5M" in prompt
        assert "CFO" in prompt

    def test_prompt_includes_budget_limit(self):
        agent = FinanceAgent()
        prompt = agent._build_analysis_prompt(SAAS_EXPANSION_CASE)

        # Budget limit should appear in the task section as well
        assert prompt.count("$3.5M") >= 2  # In context and in task instructions

    def test_prompt_includes_operational_metrics(self):
        agent = FinanceAgent()
        prompt = agent._build_analysis_prompt(SAAS_EXPANSION_CASE)

        assert "$28,000" in prompt or "28,000" in prompt  # CAC
        assert "$45,000" in prompt or "45,000" in prompt  # ACV

    def test_adaptation_prompt_includes_surprise(self):
        agent = FinanceAgent()
        prompt = agent._build_adaptation_prompt(
            case=SAAS_EXPANSION_CASE,
            surprise=SAAS_SURPRISE_EVENT,
        )

        assert "DataWatch Slashes Enterprise Pricing" in prompt
        assert "us_expected_cac" in prompt or "us_sales_cycle_days" in prompt
        assert "TASK FOR CFO" in prompt

    def test_adaptation_prompt_includes_financial_baseline(self):
        """Verify adaptation prompt surfaces original financial baseline for comparison."""
        agent = FinanceAgent()
        prompt = agent._build_adaptation_prompt(
            case=SAAS_EXPANSION_CASE,
            surprise=SAAS_SURPRISE_EVENT,
        )

        assert "Financial Baseline" in prompt or "financial_baseline" in prompt.lower()

    def test_adaptation_prompt_includes_previous_analysis(self):
        agent = FinanceAgent()
        previous = agent._generate_fallback_analysis(SAAS_EXPANSION_CASE)
        prompt = agent._build_adaptation_prompt(
            case=SAAS_EXPANSION_CASE,
            surprise=SAAS_SURPRISE_EVENT,
            previous_analysis=previous,
        )

        assert "PREVIOUS BASELINE ANALYSIS" in prompt
        assert previous.recommendation in prompt

    def test_fallback_analysis_schema_validity(self):
        agent = FinanceAgent()
        analysis = agent._generate_fallback_analysis(SAAS_EXPANSION_CASE)

        assert isinstance(analysis, AgentAnalysis)
        assert analysis.agent_id == "finance"
        assert analysis.agent_role == "Chief Financial Officer"
        assert len(analysis.findings) > 0
        assert len(analysis.evidence) > 0
        assert len(analysis.assumptions) > 0
        assert len(analysis.risks) > 0
        assert analysis.confidence is not None
        assert 0.0 <= analysis.confidence <= 1.0
        assert len(analysis.recommendation) > 10

    def test_fallback_analysis_grounded_in_financial_data(self):
        """Verify fallback uses actual financial_baseline data."""
        agent = FinanceAgent()
        analysis = agent._generate_fallback_analysis(SAAS_EXPANSION_CASE)

        # Findings should reference actual financial metrics
        findings_text = " ".join(analysis.findings)
        assert "$8.5M" in findings_text or "8.5M" in findings_text
        assert "$220,000" in findings_text or "220,000" in findings_text

        # Evidence should reference financial baseline
        evidence_text = " ".join(analysis.evidence)
        assert "annual_recurring_revenue" in evidence_text or "$3.5M" in evidence_text

    def test_fallback_analysis_references_budget_limit(self):
        agent = FinanceAgent()
        analysis = agent._generate_fallback_analysis(SAAS_EXPANSION_CASE)

        # Recommendation or evidence should reference budget limit
        assert "$3.5M" in analysis.recommendation or any("$3.5M" in e for e in analysis.evidence)

    def test_fallback_adaptation_schema_validity(self):
        agent = FinanceAgent()
        prev = agent._generate_fallback_analysis(SAAS_EXPANSION_CASE)
        adapted = agent._generate_fallback_adaptation(
            case=SAAS_EXPANSION_CASE,
            surprise=SAAS_SURPRISE_EVENT,
            previous_analysis=prev,
        )

        assert isinstance(adapted, AgentAnalysis)
        assert adapted.agent_id == "finance"
        assert len(adapted.findings) > 0
        assert len(adapted.risks) > 0
        assert 0.0 <= adapted.confidence <= 1.0

    def test_fallback_adaptation_references_surprise(self):
        agent = FinanceAgent()
        adapted = agent._generate_fallback_adaptation(
            case=SAAS_EXPANSION_CASE,
            surprise=SAAS_SURPRISE_EVENT,
        )

        surprise_referenced = any(
            SAAS_SURPRISE_EVENT.title in f for f in adapted.findings
        )
        assert surprise_referenced

    def test_analyze_with_mocked_llm(self):
        mock_output = AgentAnalysis(
            agent_id="finance",
            agent_role="Chief Financial Officer",
            findings=[
                "OPTION_A requires $2.1M allocation with projected 14-month CAC payback in EU.",
                "Current runway of 16 months supports execution if burn rate stays below $280k/mo.",
            ],
            recommendation="Execute OPTION_A with staged capital release: $800k Q1, $600k Q2, $700k Q3-Q4.",
            evidence=[
                "Annual recurring revenue: $8.5M with 78% gross margin.",
                "Budget limit: $3.5M over 12 months.",
            ],
            assumptions=[
                "EU CAC will be 25% lower than US baseline ($21k vs $28k).",
                "Gross margin holds above 75% during EU expansion.",
            ],
            risks=[
                "Currency risk (EUR/USD) could inflate costs by 5-8%.",
                "Burn rate may spike above $280k/mo during EU office buildout.",
            ],
            confidence=0.86,
        )

        with patch("agents.finance.agent.generate_structured", return_value=mock_output):
            result = run_finance_analysis(SAAS_EXPANSION_CASE)
            assert result.agent_id == "finance"
            assert result.agent_role == "Chief Financial Officer"
            assert result.confidence == 0.86
            assert "OPTION_A" in result.recommendation

    def test_adapt_with_mocked_llm(self):
        mock_adapted = AgentAnalysis(
            agent_id="finance",
            agent_role="Chief Financial Officer",
            findings=[
                "US CAC inflation to $42k makes OPTION_B financially unviable within budget.",
                "OPTION_A ROI improves relatively as EU costs remain stable.",
            ],
            recommendation="Redirect 80% of budget to OPTION_A, reserve 20% for defensive US retention.",
            evidence=[
                "US CAC increased from $28k to $42k due to competitive pricing pressure.",
            ],
            assumptions=[
                "EU costs remain unaffected by US competitive dynamics.",
            ],
            risks=[
                "Concentrated bet on single geography increases portfolio risk.",
            ],
            confidence=0.78,
        )

        with patch("agents.finance.agent.generate_structured", return_value=mock_adapted):
            result = run_finance_adaptation(
                business_case=SAAS_EXPANSION_CASE,
                surprise=SAAS_SURPRISE_EVENT,
            )
            assert result.agent_id == "finance"
            assert "OPTION_A" in result.recommendation
            assert result.confidence == 0.78

    def test_d2c_case_generalization(self):
        """Test with D2C logistics case to ensure no hardcoding."""
        agent = FinanceAgent()
        analysis = agent.analyze(D2C_LOGISTICS_CASE)

        assert isinstance(analysis, AgentAnalysis)
        assert analysis.agent_id == "finance"
        assert len(analysis.findings) > 0
        assert len(analysis.evidence) > 0

    def test_d2c_fallback_uses_d2c_financial_data(self):
        """Verify fallback adapts to D2C financial baseline, not SaaS."""
        agent = FinanceAgent()
        analysis = agent._generate_fallback_analysis(D2C_LOGISTICS_CASE)

        findings_text = " ".join(analysis.findings)
        assert "Lumina Health" in findings_text
        assert "$14.0M" in findings_text or "14.0M" in findings_text

    def test_budget_breach_surprise_adaptation(self):
        """Test D2C surprise where CapEx exceeds budget limit."""
        agent = FinanceAgent()
        adapted = agent.adapt(D2C_LOGISTICS_CASE, D2C_SURPRISE_EVENT)

        assert isinstance(adapted, AgentAnalysis)
        assert adapted.agent_id == "finance"
        assert len(adapted.findings) > 0
        # Should reference the budget breach
        findings_text = " ".join(adapted.findings)
        assert "Warehouse Lease" in findings_text or "capex" in findings_text.lower() or "parameter" in findings_text.lower()

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
                problem_statement="Determine initial funding allocation for pre-revenue product.",
                primary_objective="Reach break-even within 18 months.",
                timeline="18 months",
                hard_constraints=[],
            ),
            candidate_options=[
                StrategicOption(
                    option_id="OPTION_A",
                    name="Bootstrap Growth",
                    description="Grow organically from consulting revenue.",
                    intended_mechanism="Self-funded via services revenue.",
                ),
                StrategicOption(
                    option_id="OPTION_B",
                    name="Seed Round Fundraise",
                    description="Raise $2M seed round.",
                    intended_mechanism="Venture capital funding.",
                ),
            ],
        )

        agent = FinanceAgent()
        prompt = agent._build_analysis_prompt(sparse_case)
        assert "None provided" in prompt or "Stealth Labs" in prompt

        analysis = agent.analyze(sparse_case)
        assert isinstance(analysis, AgentAnalysis)
        assert analysis.agent_id == "finance"
        assert len(analysis.findings) > 0

    def test_sparse_case_fallback_handles_missing_budget(self):
        """Test fallback with no budget_limit specified."""
        no_budget_case = InitialBusinessCase(
            case_id="case_no_budget",
            facts=BusinessFacts(
                company_name="NoBudget Corp",
                industry="EdTech",
            ),
            context=DecisionContext(
                problem_statement="Scale or optimize?",
                primary_objective="Double user base.",
                timeline="6 months",
            ),
            candidate_options=[
                StrategicOption(
                    option_id="OPTION_A",
                    name="Scale",
                    description="Invest in growth.",
                    intended_mechanism="Marketing spend.",
                ),
            ],
        )

        agent = FinanceAgent()
        analysis = agent._generate_fallback_analysis(no_budget_case)
        assert isinstance(analysis, AgentAnalysis)
        assert "not specified" in analysis.recommendation.lower() or "available" in analysis.recommendation.lower()

    def test_single_option_case(self):
        """Test with only one candidate option."""
        single_option_case = InitialBusinessCase(
            case_id="case_single_001",
            facts=BusinessFacts(
                company_name="MonoPath Inc",
                industry="Logistics Tech",
                financial_baseline={"revenue": "$5M", "runway_months": 12},
            ),
            context=DecisionContext(
                problem_statement="Should we build a new warehouse?",
                primary_objective="Reduce fulfillment costs.",
                budget_limit="$1M",
                timeline="12 months",
            ),
            candidate_options=[
                StrategicOption(
                    option_id="OPTION_A",
                    name="Build Warehouse",
                    description="Construct a regional fulfillment center.",
                    intended_mechanism="Direct ownership.",
                ),
            ],
        )

        agent = FinanceAgent()
        analysis = agent._generate_fallback_analysis(single_option_case)
        assert isinstance(analysis, AgentAnalysis)
        assert "OPTION_A" in analysis.recommendation

    def test_graceful_fallback_on_llm_exception(self):
        with patch("agents.finance.agent.generate_structured", side_effect=Exception("API Timeout")):
            agent = FinanceAgent()
            result = agent.analyze(SAAS_EXPANSION_CASE)
            assert isinstance(result, AgentAnalysis)
            assert result.agent_id == "finance"
            assert len(result.findings) > 0

    def test_graceful_fallback_on_adapt_exception(self):
        with patch("agents.finance.agent.generate_structured", side_effect=Exception("Rate Limited")):
            agent = FinanceAgent()
            result = agent.adapt(SAAS_EXPANSION_CASE, SAAS_SURPRISE_EVENT)
            assert isinstance(result, AgentAnalysis)
            assert result.agent_id == "finance"
            assert len(result.findings) > 0

    def test_interest_rate_surprise_adaptation(self):
        """Test surprise event involving cost of capital increase."""
        rate_surprise = SurpriseEvent(
            event_id="surprise_rate_001",
            title="Central Bank Rate Hike Doubles Cost of Capital",
            description="Unexpected rate hike increases borrowing costs from 6% to 12%, making debt-funded expansion significantly more expensive.",
            impacted_areas=[Department.FINANCE],
            parameter_deltas={
                "cost_of_capital": "12%",
                "debt_service_increase": "100%",
            },
        )

        agent = FinanceAgent()
        adapted = agent._generate_fallback_adaptation(
            case=SAAS_EXPANSION_CASE,
            surprise=rate_surprise,
        )

        assert isinstance(adapted, AgentAnalysis)
        assert "Central Bank Rate Hike" in adapted.findings[0]
        assert 0.0 <= adapted.confidence <= 1.0
