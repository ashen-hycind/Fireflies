"""
Unit & Integration tests for Boardroom Traces & Evidence System (Person C).
Covers end-to-end logging, rich formatting, Markdown/JSON export, and rubric verification.
"""

import pytest
import json
from datetime import datetime

from state.schemas import (
    SwarmState,
    SwarmPhase,
    AgentAnalysis,
    DebateMessage,
    StrategyComparison,
    StrategyEvaluation,
    CEODecision,
    ExecutionTrace,
)
from traces.logger import TraceLogger
from traces.formatter import TraceFormatter
from traces.evidence_verifier import EvidenceVerifier
from tests.mock_cases import (
    SAAS_EXPANSION_CASE,
    SAAS_SURPRISE_EVENT,
    D2C_LOGISTICS_CASE,
    D2C_SURPRISE_EVENT,
)


@pytest.fixture
def sample_swarm_state() -> SwarmState:
    """Fixture providing a fully populated SwarmState across all phases."""
    research_analysis = AgentAnalysis(
        agent_id="research",
        agent_role="Lead Market Researcher",
        findings=["EU mid-market represents an uncrowded TAM with strong growth."],
        recommendation="Option A: Expand to EU mid-market.",
        evidence=["European market has lower competitor resistance."],
        assumptions=["GDPR compliance timeline is achievable."],
        risks=["Regulatory divergence across EU nations."],
        confidence=0.85,
    )
    finance_analysis = AgentAnalysis(
        agent_id="finance",
        agent_role="Chief Financial Officer",
        findings=["Option A maintains cash runway within the 10-month safety limit."],
        recommendation="Option A: EU expansion offers superior unit economics.",
        evidence=["$3.5M budget covers EU sales hub ramp."],
        assumptions=["CAC payback remains under 14 months."],
        risks=["FX currency volatility against GBP/EUR."],
        confidence=0.90,
    )
    marketing_analysis = AgentAnalysis(
        agent_id="marketing",
        agent_role="Chief Marketing Officer",
        findings=["Lower competitive friction in EU mid-market enables fast pipeline velocity."],
        recommendation="Option A: Target 150 mid-market EU enterprise accounts.",
        evidence=["DataWatch holds 60% of US, creating high US CAC."],
        assumptions=["Target accounts respond to direct SDR outreach in London/Berlin."],
        risks=["Channel partner development delays."],
        confidence=0.88,
    )

    debate_msgs = [
        DebateMessage(
            message_id="msg_001",
            from_agent="finance",
            to_agent="marketing",
            message_type="challenge",
            content="Can marketing achieve < 14 month CAC payback in the EU given localization costs?",
            referenced_agent="marketing",
            requires_response=True,
        ),
        DebateMessage(
            message_id="msg_002",
            from_agent="marketing",
            to_agent="finance",
            message_type="response",
            content="Yes, because inbound search CPC and SDR compensation in London/Berlin are 30% lower than in SF/NY.",
            referenced_agent="finance",
            requires_response=False,
        ),
    ]

    strat_comp = StrategyComparison(
        evaluations=[
            StrategyEvaluation(
                option_id="OPTION_A",
                advantages=["Lower CAC", "Uncontested mid-market TAM"],
                disadvantages=["GDPR localization overhead"],
                financial_impact="High ROI, payback in 11 months",
                market_impact="First-mover advantage in mid-market",
                operational_impact="Requires London/Berlin hub setup",
                risks=["Regulatory delays"],
                supporting_agents=["research", "finance", "marketing"],
            ),
            StrategyEvaluation(
                option_id="OPTION_B",
                advantages=["High ACV expansion from US enterprise"],
                disadvantages=["High US CAC", "DataWatch entrenched"],
                financial_impact="Moderate ROI with high upfront sales cost",
                market_impact="High competitor friction",
                operational_impact="Requires enterprise sales reps",
                risks=["Price war with DataWatch"],
                supporting_agents=[],
            ),
        ],
        preferred_option="OPTION_A",
        trade_offs=["Short-term setup friction vs long-term margin sustainability"],
        unresolved_uncertainties=["EU enterprise decision velocity"],
    )

    ceo_decision = CEODecision(
        selected_option_id="OPTION_A",
        decision_statement="CloudMetrics will execute Option A (Aggressive European Mid-Market Expansion) to capture underserved EU mid-market accounts.",
        rationale=[
            "Unanimous agreement across Research, Finance, and Marketing on superior unit economics.",
            "Avoids direct head-to-head price compression with DataWatch in US enterprise.",
        ],
        rejected_options=["OPTION_B"],
        rejection_reasons=[
            "Option B exposes the company to excessive CAC in a crowded US enterprise tier.",
        ],
        trade_offs=[
            "Prioritizing international geographic footprint over domestic upmarket expansion.",
        ],
        risks=[
            "GDPR compliance timeline slippage.",
            "Exchange rate volatility.",
        ],
        assumptions=[
            "European mid-market decision-makers are receptive to US SaaS observability.",
        ],
        implementation_steps=[
            "Establish London/Berlin sales entity and hire regional lead.",
            "Complete EU GDPR localization and data sovereignty audit.",
            "Launch outbound SDR campaign targeting top 150 accounts.",
        ],
        kpis=[
            "Add $3.5M in EU ARR within 12 months",
            "Maintain CAC payback period under 12 months",
            "Achieve Net Revenue Retention > 110% in EU cohort",
        ],
    )

    adapted_decision = CEODecision(
        selected_option_id="OPTION_A",
        decision_statement="Reaffirming Option A with accelerated timeline following DataWatch US price cut.",
        rationale=[
            "DataWatch's 40% price cut severely damages Option B viability, reinforcing Option A as the only sustainable path.",
        ],
        rejected_options=["OPTION_B"],
        rejection_reasons=["US enterprise margin compression renders Option B unprofitable."],
        trade_offs=["Reallocating 100% of growth budget to EU."],
        risks=["DataWatch expanding into Europe next fiscal year."],
        assumptions=["EU pricing remains shielded from US price wars."],
        implementation_steps=[
            "Shift 2 US SDRs to EU outbound pipeline.",
            "Fast-track localized enterprise pricing packages.",
        ],
        kpis=[
            "Acquire first 40 EU customers within 6 months",
            "Keep US customer logo churn under 3%",
            "Reach $4.0M ARR in EU by Q4",
        ],
    )

    state = SwarmState(
        phase=SwarmPhase.COMPLETED,
        business_case=SAAS_EXPANSION_CASE,
        department_analyses={
            "research": research_analysis,
            "finance": finance_analysis,
            "marketing": marketing_analysis,
        },
        debate_messages=debate_msgs,
        strategy_comparison=strat_comp,
        baseline_decision=ceo_decision,
        surprise=SAAS_SURPRISE_EVENT,
        adapted_analyses={
            "marketing": marketing_analysis,
            "finance": finance_analysis,
        },
        adapted_decision=adapted_decision,
    )

    return state


class TestTraceLogger:
    """Test suite for TraceLogger operations."""

    def test_logger_event_creation(self):
        logger = TraceLogger()
        trace = logger.log_phase(SwarmPhase.INITIAL_ANALYSIS, "Starting initial analysis phase")

        assert trace.phase == SwarmPhase.INITIAL_ANALYSIS
        assert trace.event_type == "phase_started"
        assert trace.summary == "Starting initial analysis phase"
        assert trace.timestamp is not None
        dt = datetime.fromisoformat(trace.timestamp)
        assert dt is not None
        assert len(logger.get_traces()) == 1

    def test_logger_log_agent_lifecycle(self):
        logger = TraceLogger()
        logger.log_agent_started(SwarmPhase.INITIAL_ANALYSIS, "marketing")

        analysis = AgentAnalysis(
            agent_id="marketing",
            agent_role="Chief Marketing Officer",
            findings=["Strong ICP fit in EU"],
            recommendation="Option A",
            evidence=["Verified market fact"],
            assumptions=["CAC stable"],
            risks=["Hiring delay"],
            confidence=0.9,
        )
        logger.log_agent_completed(SwarmPhase.INITIAL_ANALYSIS, "marketing", analysis)

        traces = logger.get_traces()
        assert len(traces) == 2
        assert traces[0].event_type == "agent_started"
        assert traces[1].event_type == "agent_completed"
        assert traces[1].metadata["confidence"] == 0.9

    def test_logger_log_agent_failed(self):
        logger = TraceLogger()
        logger.log_agent_failed(SwarmPhase.INITIAL_ANALYSIS, "marketing", "LLM rate limit")
        traces = logger.get_traces()
        assert len(traces) == 1
        assert traces[0].event_type == "agent_failed"
        assert "LLM rate limit" in traces[0].summary

    def test_logger_log_debate_and_decision(self):
        logger = TraceLogger()
        msg = DebateMessage(
            message_id="m1",
            from_agent="finance",
            to_agent="marketing",
            message_type="challenge",
            content="Critique on CAC",
        )
        logger.log_debate_message(msg)

        traces = logger.get_traces()
        assert len(traces) == 1
        assert traces[0].event_type == "challenge"
        assert traces[0].agent_id == "finance"

    def test_logger_high_volume_batch_logging(self):
        """Test logging 100+ events sequentially."""
        logger = TraceLogger()
        for i in range(100):
            logger.log_event(
                phase=SwarmPhase.INITIAL_ANALYSIS,
                event_type="heartbeat",
                summary=f"Batch trace event #{i}",
                metadata={"index": i},
            )
        assert len(logger.get_traces()) == 100
        logger.clear()
        assert len(logger.get_traces()) == 0

    def test_logger_system_error_logging(self):
        logger = TraceLogger()
        trace = logger.log_error(SwarmPhase.SURPRISE_INJECTION, "Kafka disruption event lost", agent_id="orchestrator")
        assert trace.event_type == "error"
        assert "Kafka disruption event lost" in trace.summary

    def test_attach_to_state(self, sample_swarm_state):
        logger = TraceLogger()
        logger.log_phase(SwarmPhase.INITIAL_ANALYSIS, "Init")
        logger.log_phase(SwarmPhase.COMPLETED, "Done")

        logger.attach_to_state(sample_swarm_state)
        assert len(sample_swarm_state.execution_trace) == 2
        assert sample_swarm_state.execution_trace[0].summary == "Init"


class TestTraceFormatter:
    """Test suite for TraceFormatter rendering and export functions."""

    def test_to_markdown_contains_all_core_sections(self, sample_swarm_state):
        logger = TraceLogger()
        logger.log_phase(SwarmPhase.INITIAL_ANALYSIS, "Init analysis")
        logger.attach_to_state(sample_swarm_state)

        md = TraceFormatter.to_markdown(sample_swarm_state)

        assert "# Fireflies Swarm Boardroom Audit Report" in md
        assert "CloudMetrics AI" in md
        assert "Executive Problem Context" in md
        assert "Department Analytical Findings" in md
        assert "Chief Marketing Officer" in md
        assert "Boardroom Debate & Inter-Agent Challenges" in md
        assert "Strategy Comparison Matrix" in md
        assert "Baseline CEO Executive Decision" in md
        assert "OPTION_A" in md
        assert "Runtime Surprise Disruption" in md
        assert "Final Revised Decision" in md
        assert "Complete Chronological Execution Trace" in md

    def test_to_markdown_partial_state(self):
        """Verify markdown formatter handles early in-progress swarm states gracefully."""
        partial_state = SwarmState(
            phase=SwarmPhase.INITIAL_ANALYSIS,
            business_case=D2C_LOGISTICS_CASE,
        )
        md = TraceFormatter.to_markdown(partial_state)
        assert "Lumina Health" in md
        assert "No initial department analyses recorded" in md
        assert "No baseline CEO decision recorded" in md

    def test_to_markdown_with_d2c_surprise(self, sample_swarm_state):
        """Test markdown formatting with D2C logistics surprise event."""
        sample_swarm_state.surprise = D2C_SURPRISE_EVENT
        md = TraceFormatter.to_markdown(sample_swarm_state)
        assert "Warehouse Lease Rates Spike" in md

    def test_to_json_validity(self, sample_swarm_state, tmp_path):
        json_file = tmp_path / "trace_test.json"
        json_str = TraceFormatter.to_json(sample_swarm_state, filepath=str(json_file))

        parsed = json.loads(json_str)
        assert parsed["business_case"]["case_id"] == "case_saas_001"
        assert "marketing" in parsed["department_analyses"]
        assert json_file.exists()

    def test_render_terminal_does_not_throw(self, sample_swarm_state):
        # Ensure render_terminal runs smoothly without raising exceptions
        TraceFormatter.render_terminal(sample_swarm_state)

    def test_render_terminal_partial_state(self):
        partial_state = SwarmState(
            phase=SwarmPhase.INITIAL_ANALYSIS,
            business_case=D2C_LOGISTICS_CASE,
        )
        TraceFormatter.render_terminal(partial_state)


class TestEvidenceVerifier:
    """Test suite for hackathon rubric & evidence checklist verifier."""

    def test_verifier_on_compliant_state(self, sample_swarm_state):
        logger = TraceLogger()
        for i in range(6):
            logger.log_phase(SwarmPhase.INITIAL_ANALYSIS, f"Step {i}")
        logger.attach_to_state(sample_swarm_state)

        result = EvidenceVerifier.verify_state(sample_swarm_state)

        assert result["is_fully_compliant"] is True
        assert result["score_percent"] == 100.0
        assert result["passed_checks"] == result["total_checks"]

    def test_verifier_detects_missing_department(self, sample_swarm_state):
        del sample_swarm_state.department_analyses["marketing"]

        result = EvidenceVerifier.verify_state(sample_swarm_state)
        assert result["is_fully_compliant"] is False
        check1 = result["checks"][0]
        assert check1["passed"] is False

    def test_verifier_detects_insufficient_kpis(self, sample_swarm_state):
        sample_swarm_state.baseline_decision.kpis = ["Single KPI"]

        result = EvidenceVerifier.verify_state(sample_swarm_state)
        assert result["is_fully_compliant"] is False
        kpi_check = next(c for c in result["checks"] if "KPIs" in c["criteria"])
        assert kpi_check["passed"] is False

    def test_verifier_detects_missing_debate(self, sample_swarm_state):
        sample_swarm_state.debate_messages = []
        result = EvidenceVerifier.verify_state(sample_swarm_state)
        assert result["is_fully_compliant"] is False
        debate_check = next(c for c in result["checks"] if "Debate" in c["criteria"])
        assert debate_check["passed"] is False
