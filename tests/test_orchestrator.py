"""
Unit and integration tests for the SwarmOrchestrator.
"""

import pytest
from state.schemas import (
    SwarmPhase,
    AgentAnalysis,
    DebateMessage,
    StrategyComparison,
    StrategyEvaluation,
    CEODecision,
)
from orchestrator.engine import SwarmOrchestrator
from tests.mock_cases import SAAS_EXPANSION_CASE, SAAS_SURPRISE_EVENT


def test_orchestrator_lifecycle(monkeypatch):
    """Tests the full SwarmOrchestrator state machine transitions and fallback mechanics."""

    orchestrator = SwarmOrchestrator()

    # Mock DebateEngine
    def mock_run_debate(case, analyses):
        return [
            DebateMessage(
                message_id="deb_001",
                from_agent="finance",
                to_agent="marketing",
                message_type="challenge",
                content="CAC assumption of $28k appears risky.",
            ),
            DebateMessage(
                message_id="deb_002",
                from_agent="marketing",
                to_agent="finance",
                message_type="response",
                content="Channel mix is diversified to protect CAC.",
            ),
        ]

    # Mock StrategyComparator
    def mock_compare_strategies(business_case, department_analyses, debate_messages):
        return StrategyComparison(
            evaluations=[
                StrategyEvaluation(option_id="OPTION_A", advantages=["EU expansion"], disadvantages=["GDPR"]),
                StrategyEvaluation(option_id="OPTION_B", advantages=["Upmarket AI"], disadvantages=["High competition"]),
            ],
            preferred_option="OPTION_A",
            trade_offs=["EU localization overhead vs US competition"],
        )

    # Mock CEOAgent
    def mock_baseline_decision(business_case, department_analyses, debate_messages, strategy_comparison):
        return CEODecision(
            selected_option_id="OPTION_A",
            decision_statement="Proceed with European expansion.",
            rationale=["Lower CAC and strong mid-market opportunity."],
            rejected_options=["OPTION_B"],
            rejection_reasons=["High US competition."],
            trade_offs=["Resource focus on EU over US"],
            risks=["GDPR compliance timeline"],
            assumptions=["EU demand remains stable"],
            implementation_steps=["Hire UK GM", "Localize billing"],
            kpis=["EU ARR > $2M", "Payback < 10 months", "Churn < 1.5%"],
        )

    def mock_adapted_decision(business_case, baseline_decision, surprise_event, adapted_analyses, adapted_strategy_comparison):
        return CEODecision(
            selected_option_id="OPTION_A",
            decision_statement="Reaffirm European expansion; accelerate EU timeline to bypass US price war.",
            rationale=["US pricing slashed 40%, making EU even more strategically attractive."],
            rejected_options=["OPTION_B"],
            rejection_reasons=["US price war further damages unit economics."],
            trade_offs=["Deprioritize US enterprise marketing"],
            risks=["Need faster localization"],
            assumptions=["EU competitors do not slash prices"],
            implementation_steps=["Reallocate 40% US ad spend to EU", "Accelerate Berlin office launch"],
            kpis=["EU ARR > $3.5M", "EU Sales Cycle < 60 days", "Net Margin > 15%"],
        )

    monkeypatch.setattr(orchestrator.debate_engine, "run_debate", mock_run_debate)
    monkeypatch.setattr(orchestrator.strategy_comparator, "compare_strategies", mock_compare_strategies)
    monkeypatch.setattr(orchestrator.ceo_agent, "synthesize_baseline_decision", mock_baseline_decision)
    monkeypatch.setattr(orchestrator.ceo_agent, "synthesize_adapted_decision", mock_adapted_decision)

    # Execute
    state = orchestrator.run_full_swarm(
        business_case=SAAS_EXPANSION_CASE,
        surprise_event=SAAS_SURPRISE_EVENT,
    )

    # Verifications
    assert state.phase == SwarmPhase.COMPLETED
    assert len(state.department_analyses) == 3
    assert "research" in state.department_analyses
    assert "finance" in state.department_analyses
    assert "marketing" in state.department_analyses
    assert len(state.debate_messages) == 2
    assert state.strategy_comparison is not None
    assert state.baseline_decision.selected_option_id == "OPTION_A"
    assert len(state.baseline_decision.kpis) >= 3
    assert state.surprise is not None
    assert len(state.adapted_analyses) >= 1
    assert state.adapted_decision is not None
    assert len(state.execution_trace) > 5
