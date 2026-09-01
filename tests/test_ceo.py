"""
Unit tests for the CEO Agent.
"""

import pytest
from agents.ceo.agent import CEOAgent
from state.schemas import (
    InitialBusinessCase,
    BusinessFacts,
    DecisionContext,
    StrategicOption,
    AgentAnalysis,
    DebateMessage,
    StrategyComparison,
    StrategyEvaluation,
    CEODecision,
)


def test_ceo_agent_synthesize_baseline_mock(monkeypatch):
    """Verifies that the CEO agent produces a valid CEODecision adhering to schema."""
    case = InitialBusinessCase(
        case_id="test_001",
        facts=BusinessFacts(
            company_name="TestCo",
            industry="Software",
            financial_baseline={"revenue": "$1M"},
            operational_metrics={"team": 10},
            market_facts=["Growing market"],
        ),
        context=DecisionContext(
            problem_statement="Expand or optimize?",
            primary_objective="Maximize profit",
            timeline="1 year",
        ),
        candidate_options=[
            StrategicOption(option_id="OPT_A", name="Option A", description="Expand", intended_mechanism="Scale"),
            StrategicOption(option_id="OPT_B", name="Option B", description="Optimize", intended_mechanism="Cut costs"),
        ],
    )

    dept_analyses = {
        "research": AgentAnalysis(
            agent_id="research",
            agent_role="Research Lead",
            findings=["Market ready for expansion"],
            recommendation="Adopt OPT_A",
            evidence=["High TAM"],
            assumptions=["Stability"],
            risks=["Competition"],
            confidence=0.9,
        ),
        "finance": AgentAnalysis(
            agent_id="finance",
            agent_role="Finance Lead",
            findings=["Runway allows OPT_A"],
            recommendation="Adopt OPT_A",
            evidence=["$2M cash"],
            assumptions=["Stable burn"],
            risks=["CapEx overrun"],
            confidence=0.85,
        ),
    }

    strategy_comp = StrategyComparison(
        evaluations=[
            StrategyEvaluation(option_id="OPT_A", advantages=["Higher upside"], disadvantages=["More cash"]),
            StrategyEvaluation(option_id="OPT_B", advantages=["Low risk"], disadvantages=["Slower growth"]),
        ],
        preferred_option="OPT_A",
        trade_offs=["Cash vs Growth"],
    )

    ceo = CEOAgent()

    # Mock generate_structured to test schema compliance without requiring live LLM call
    def mock_generate_structured(*args, **kwargs):
        return CEODecision(
            selected_option_id="OPT_A",
            decision_statement="Execute Option A to capture market leadership.",
            rationale=["Supported by Research TAM and Finance runway."],
            rejected_options=["OPT_B"],
            rejection_reasons=["Option B yields insufficient ARR growth."],
            trade_offs=["Higher initial burn accepted for market share."],
            risks=["Execution delays"],
            assumptions=["Market demand holds"],
            implementation_steps=["Phase 1: Team ramp", "Phase 2: Product launch"],
            kpis=["ARR > $3M", "CAC < $500", "Payback < 12 months"],
        )

    monkeypatch.setattr("agents.ceo.agent.generate_structured", mock_generate_structured)

    decision = ceo.synthesize_baseline_decision(
        business_case=case,
        department_analyses=dept_analyses,
        debate_messages=[],
        strategy_comparison=strategy_comp,
    )

    assert isinstance(decision, CEODecision)
    assert decision.selected_option_id == "OPT_A"
    assert len(decision.kpis) >= 3
    assert len(decision.rejected_options) >= 1
