"""
Unit & Integration tests for Marketing & Sales Agent (Person C).
Covers standard workflows, edge cases, severe disruptions, and error resilience.
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
from agents.marketing.agent import (
    MarketingAgent,
    run_marketing_analysis,
    run_marketing_adaptation,
)
from tests.mock_cases import (
    SAAS_EXPANSION_CASE,
    SAAS_SURPRISE_EVENT,
    D2C_LOGISTICS_CASE,
    D2C_SURPRISE_EVENT,
)


class TestMarketingAgent:
    """Test suite for MarketingAgent role, prompt formatting, analysis, and adaptation."""

    def test_agent_initialization(self):
        agent = MarketingAgent()
        assert agent.agent_id == "marketing"
        assert agent.agent_role == "Chief Marketing Officer"

    def test_prompt_generation_includes_key_context(self):
        agent = MarketingAgent()
        prompt = agent._build_analysis_prompt(SAAS_EXPANSION_CASE)

        assert "CloudMetrics AI" in prompt
        assert "OPTION_A" in prompt
        assert "OPTION_B" in prompt
        assert "primary_objective" in prompt.lower() or "objective" in prompt.lower()
        assert "Chief Marketing Officer" in prompt or "CMO" in prompt

    def test_adaptation_prompt_generation_includes_surprise(self):
        agent = MarketingAgent()
        prompt = agent._build_adaptation_prompt(
            case=SAAS_EXPANSION_CASE,
            surprise=SAAS_SURPRISE_EVENT,
        )

        assert "DataWatch Slashes Enterprise Pricing" in prompt
        assert "us_expected_cac" in prompt
        assert "TASK FOR CMO" in prompt

    def test_fallback_analysis_schema_validity(self):
        agent = MarketingAgent()
        analysis = agent._generate_fallback_analysis(SAAS_EXPANSION_CASE)

        assert isinstance(analysis, AgentAnalysis)
        assert analysis.agent_id == "marketing"
        assert analysis.agent_role == "Chief Marketing Officer"
        assert len(analysis.findings) > 0
        assert len(analysis.evidence) > 0
        assert len(analysis.assumptions) > 0
        assert len(analysis.risks) > 0
        assert analysis.confidence is not None
        assert 0.0 <= analysis.confidence <= 1.0
        assert len(analysis.recommendation) > 10

    def test_fallback_adaptation_schema_validity(self):
        agent = MarketingAgent()
        prev = agent._generate_fallback_analysis(SAAS_EXPANSION_CASE)
        adapted = agent._generate_fallback_adaptation(
            case=SAAS_EXPANSION_CASE,
            surprise=SAAS_SURPRISE_EVENT,
            previous_analysis=prev,
        )

        assert isinstance(adapted, AgentAnalysis)
        assert adapted.agent_id == "marketing"
        assert len(adapted.findings) > 0
        assert len(adapted.risks) > 0
        assert 0.0 <= adapted.confidence <= 1.0

    def test_analyze_with_mocked_llm(self):
        mock_output = AgentAnalysis(
            agent_id="marketing",
            agent_role="Chief Marketing Officer",
            findings=[
                "EU mid-market represents an uncrowded TAM with lower CAC.",
                "US enterprise sales cycle is 75 days with $28k CAC.",
            ],
            recommendation="Execute OPTION_A: Aggressive European Mid-Market Expansion.",
            evidence=[
                "Enterprise demand grew 34% YoY in observability.",
                "European market has lower competitor resistance.",
            ],
            assumptions=[
                "EU sales hub can be established within 4 months.",
                "GDPR compliance overhead will not delay product availability.",
            ],
            risks=[
                "Currency exchange fluctuation.",
                "Local hiring delays in London/Berlin.",
            ],
            confidence=0.88,
        )

        with patch("agents.marketing.agent.generate_structured", return_value=mock_output):
            result = run_marketing_analysis(SAAS_EXPANSION_CASE)
            assert result.agent_id == "marketing"
            assert result.agent_role == "Chief Marketing Officer"
            assert result.confidence == 0.88
            assert "OPTION_A" in result.recommendation

    def test_adapt_with_mocked_llm(self):
        mock_adapted = AgentAnalysis(
            agent_id="marketing",
            agent_role="Chief Marketing Officer",
            findings=[
                "Competitor 40% price cut increases US enterprise CAC to $42k.",
                "EU expansion becomes even more attractive as a defensive counter.",
            ],
            recommendation="Accelerate OPTION_A while avoiding price wars in US enterprise.",
            evidence=[
                "DataWatch announced 40% price reduction on multi-year deals.",
            ],
            assumptions=[
                "EU pricing power remains intact.",
            ],
            risks=[
                "DataWatch may follow into European market within 12 months.",
            ],
            confidence=0.84,
        )

        with patch("agents.marketing.agent.generate_structured", return_value=mock_adapted):
            result = run_marketing_adaptation(
                business_case=SAAS_EXPANSION_CASE,
                surprise=SAAS_SURPRISE_EVENT,
            )
            assert result.agent_id == "marketing"
            assert "OPTION_A" in result.recommendation
            assert result.confidence == 0.84

    def test_d2c_logistics_case_generalization(self):
        agent = MarketingAgent()
        analysis = agent.analyze(D2C_LOGISTICS_CASE)

        assert isinstance(analysis, AgentAnalysis)
        assert analysis.agent_id == "marketing"
        assert len(analysis.findings) > 0
        assert len(analysis.evidence) > 0

    def test_multi_option_conglomerate_case(self):
        """Test with 5 distinct candidate options."""
        five_option_case = InitialBusinessCase(
            case_id="case_conglomerate_005",
            facts=BusinessFacts(
                company_name="Apex Global Tech",
                industry="Enterprise Cloud Infrastructure",
                financial_baseline={"revenue": "$500M", "growth_rate": "15%"},
                operational_metrics={"sales_reps": 200, "avg_deal_size": "$250k"},
                market_facts=["AI modernization is top priority for 80% of CIOs."],
            ),
            context=DecisionContext(
                problem_statement="How should Apex accelerate cloud infrastructure market share?",
                primary_objective="Achieve 30% YoY growth across enterprise accounts.",
                timeline="24 months",
                hard_constraints=["Must maintain minimum operating margin of 20%."],
            ),
            candidate_options=[
                StrategicOption(option_id="OPTION_A", name="M&A Consolidation", description="Acquire niche AI startup.", intended_mechanism="Inorganic tech tuck-in."),
                StrategicOption(option_id="OPTION_B", name="Direct Enterprise Sales Expansion", description="Hire 100 enterprise sales reps.", intended_mechanism="Direct field sales."),
                StrategicOption(option_id="OPTION_C", name="Hyperscaler Cloud Marketplace Co-Sell", description="Deep partner integration with AWS/GCP.", intended_mechanism="Marketplace commit drawdowns."),
                StrategicOption(option_id="OPTION_D", name="Product-Led Self-Serve Freemium", description="Open-source lightweight engine.", intended_mechanism="Bottom-up developer adoption."),
                StrategicOption(option_id="OPTION_E", name="Global Systems Integrator Channel", description="Partner with Accenture/Deloitte.", intended_mechanism="Large-scale enterprise transformation bundles."),
            ],
        )

        agent = MarketingAgent()
        prompt = agent._build_analysis_prompt(five_option_case)
        for opt in ["OPTION_A", "OPTION_B", "OPTION_C", "OPTION_D", "OPTION_E"]:
            assert opt in prompt

        analysis = agent._generate_fallback_analysis(five_option_case)
        assert isinstance(analysis, AgentAnalysis)
        assert analysis.agent_id == "marketing"
        assert len(analysis.findings) > 0

    def test_sparse_startup_case_no_crashes(self):
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
                problem_statement="Determine initial GTM path for pre-revenue product.",
                primary_objective="Reach first 50 design partner customers.",
                timeline="6 months",
                hard_constraints=[],
            ),
            candidate_options=[
                StrategicOption(option_id="OPTION_A", name="Developer Community Launch", description="Launch on Product Hunt and GitHub.", intended_mechanism="Organic virality."),
                StrategicOption(option_id="OPTION_B", name="Founder-Led Sales Outreach", description="Direct LinkedIn and angel network outreach.", intended_mechanism="High-touch feedback."),
            ],
        )

        agent = MarketingAgent()
        prompt = agent._build_analysis_prompt(sparse_case)
        assert "None provided" in prompt
        assert "Stealth Labs" in prompt

        analysis = agent.analyze(sparse_case)
        assert isinstance(analysis, AgentAnalysis)
        assert analysis.agent_id == "marketing"

    def test_positive_viral_demand_surprise_adaptation(self):
        """Test runtime surprise where inbound demand explodes unexpectedly."""
        viral_surprise = SurpriseEvent(
            event_id="surprise_viral_001",
            title="Viral Developer Campaign Yields 10x Inbound Pipeline",
            description="A community benchmark blog post went viral, generating 10,000 signups in 72 hours, overwhelming self-serve onboarding.",
            impacted_areas=[Department.MARKETING],
            parameter_deltas={
                "inbound_lead_multiplier": 10.0,
                "inbound_cac": "$45",
                "organic_traffic_spike": "500%",
            },
        )

        agent = MarketingAgent()
        adapted = agent._generate_fallback_adaptation(
            case=SAAS_EXPANSION_CASE,
            surprise=viral_surprise,
        )

        assert isinstance(adapted, AgentAnalysis)
        assert "Viral Developer Campaign" in adapted.findings[0] or "viral" in adapted.findings[0].lower()
        assert 0.0 <= adapted.confidence <= 1.0

    def test_regulatory_ban_surprise_adaptation(self):
        """Test runtime disruption where a major channel is suddenly outlawed."""
        regulatory_surprise = SurpriseEvent(
            event_id="surprise_reg_002",
            title="EU Imposes Immediate Strict Restriction on Cold B2B Outreach",
            description="New privacy directive requires explicit opt-in before direct sales outreach, reducing outbound SDR conversion by 80%.",
            impacted_areas=[Department.MARKETING],
            parameter_deltas={
                "outbound_conversion_drop": "80%",
                "lead_cost_inflation": "300%",
            },
        )

        agent = MarketingAgent()
        prompt = agent._build_adaptation_prompt(SAAS_EXPANSION_CASE, regulatory_surprise)
        assert "Restriction on Cold B2B Outreach" in prompt

        adapted = agent._generate_fallback_adaptation(SAAS_EXPANSION_CASE, regulatory_surprise)
        assert isinstance(adapted, AgentAnalysis)
        assert len(adapted.risks) > 0

    def test_adaptation_when_marketing_not_in_impacted_areas(self):
        """Test surprise event that directly affects other departments (e.g. Finance only)."""
        finance_only_surprise = SurpriseEvent(
            event_id="surprise_fin_003",
            title="Interest Rate Hike Increases Cost of Capital",
            description="Central bank rate hike increases borrowing cost, reducing available expansion CapEx.",
            impacted_areas=[Department.FINANCE],
            parameter_deltas={"cost_of_capital": "12%"},
        )

        agent = MarketingAgent()
        adapted = agent._generate_fallback_adaptation(SAAS_EXPANSION_CASE, finance_only_surprise)
        assert isinstance(adapted, AgentAnalysis)
        assert adapted.agent_id == "marketing"

    def test_graceful_fallback_on_llm_exception(self):
        with patch("agents.marketing.agent.generate_structured", side_effect=Exception("API Timeout")):
            agent = MarketingAgent()
            result = agent.analyze(SAAS_EXPANSION_CASE)
            assert isinstance(result, AgentAnalysis)
            assert result.agent_id == "marketing"
            assert len(result.findings) > 0
