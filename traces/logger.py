"""
Execution Trace & Audit Logger for Fireflies Swarm.

Provides real-time event logging, timestamp generation, and state trace tracking
conforming to the ExecutionTrace and SwarmState schemas in state/schemas.py.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
import uuid

from state.schemas import (
    ExecutionTrace,
    SwarmPhase,
    SwarmState,
    AgentAnalysis,
    DebateMessage,
    StrategyComparison,
    CEODecision,
    SurpriseEvent,
)


class TraceLogger:
    """
    Manages and records the chronological audit trail for all boardroom operations,
    agent communications, strategy formulations, and executive decisions.
    """

    def __init__(self, initial_traces: Optional[List[ExecutionTrace]] = None):
        self.traces: List[ExecutionTrace] = list(initial_traces) if initial_traces else []

    def _generate_event_id(self) -> str:
        return f"evt_{uuid.uuid4().hex[:8]}"

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def log_event(
        self,
        phase: SwarmPhase,
        event_type: str,
        summary: str,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ExecutionTrace:
        """
        Base event logger that creates and appends an ExecutionTrace record.
        """
        trace = ExecutionTrace(
            event_id=self._generate_event_id(),
            timestamp=self._now_iso(),
            phase=phase,
            agent_id=agent_id,
            event_type=event_type,
            summary=summary,
            metadata=metadata or {},
        )
        self.traces.append(trace)
        return trace

    def log_phase(
        self,
        phase: SwarmPhase,
        summary: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ExecutionTrace:
        """Logs the transition into a new swarm lifecycle phase."""
        return self.log_event(
            phase=phase,
            event_type="phase_started",
            summary=summary,
            metadata=metadata,
        )

    def log_agent_started(
        self,
        phase: SwarmPhase,
        agent_id: str,
        summary: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ExecutionTrace:
        """Logs when an individual agent commences analysis."""
        return self.log_event(
            phase=phase,
            event_type="agent_started",
            agent_id=agent_id,
            summary=summary or f"Agent '{agent_id}' started analytical evaluation.",
            metadata=metadata,
        )

    def log_agent_completed(
        self,
        phase: SwarmPhase,
        agent_id: str,
        analysis: AgentAnalysis,
        summary: Optional[str] = None,
    ) -> ExecutionTrace:
        """Logs when an agent completes analysis with structured outputs."""
        meta = {
            "agent_role": analysis.agent_role,
            "recommendation": analysis.recommendation,
            "findings_count": len(analysis.findings),
            "evidence_count": len(analysis.evidence),
            "assumptions_count": len(analysis.assumptions),
            "risks_count": len(analysis.risks),
            "confidence": analysis.confidence,
        }
        return self.log_event(
            phase=phase,
            event_type="agent_completed",
            agent_id=agent_id,
            summary=summary or f"Agent '{agent_id}' completed analysis with confidence {analysis.confidence}.",
            metadata=meta,
        )

    def log_agent_failed(
        self,
        phase: SwarmPhase,
        agent_id: str,
        error: str,
    ) -> ExecutionTrace:
        """Logs an agent failure or exception."""
        return self.log_event(
            phase=phase,
            event_type="agent_failed",
            agent_id=agent_id,
            summary=f"Agent '{agent_id}' encountered an error: {error}",
            metadata={"error": error},
        )

    def log_debate_message(self, message: DebateMessage) -> ExecutionTrace:
        """Logs an inter-agent challenge, response, or critique."""
        return self.log_event(
            phase=SwarmPhase.DEBATE_CHALLENGE,
            event_type="challenge" if message.message_type == "challenge" else "message_sent",
            agent_id=message.from_agent,
            summary=f"[{message.message_type.upper()}] from {message.from_agent} to {message.to_agent or 'all'}: {message.content[:80]}...",
            metadata={
                "message_id": message.message_id,
                "from_agent": message.from_agent,
                "to_agent": message.to_agent,
                "message_type": message.message_type,
                "referenced_agent": message.referenced_agent,
                "referenced_claim": message.referenced_claim,
                "requires_response": message.requires_response,
                "full_content": message.content,
            },
        )

    def log_strategy_comparison(
        self,
        comparison: StrategyComparison,
        phase: SwarmPhase = SwarmPhase.STRATEGY_COMPARISON,
    ) -> ExecutionTrace:
        """Logs the formulation of the strategic comparison matrix."""
        return self.log_event(
            phase=phase,
            event_type="strategy_comparison",
            summary=f"Strategy comparison generated. Leading option: '{comparison.preferred_option}'.",
            metadata={
                "preferred_option": comparison.preferred_option,
                "options_evaluated": [e.option_id for e in comparison.evaluations],
                "trade_offs_count": len(comparison.trade_offs),
                "uncertainties_count": len(comparison.unresolved_uncertainties),
            },
        )

    def log_decision(
        self,
        decision: CEODecision,
        phase: SwarmPhase = SwarmPhase.BASELINE_DECISION,
    ) -> ExecutionTrace:
        """Logs the executive CEO decision."""
        return self.log_event(
            phase=phase,
            event_type="decision",
            agent_id="ceo",
            summary=f"CEO selected '{decision.selected_option_id}': {decision.decision_statement[:90]}...",
            metadata={
                "selected_option_id": decision.selected_option_id,
                "rejected_options": decision.rejected_options,
                "kpis_count": len(decision.kpis),
                "implementation_steps_count": len(decision.implementation_steps),
            },
        )

    def log_surprise(self, surprise: SurpriseEvent) -> ExecutionTrace:
        """Logs a runtime surprise disruption injection."""
        return self.log_event(
            phase=SwarmPhase.SURPRISE_INJECTION,
            event_type="surprise_injected",
            summary=f"Surprise disruption injected: '{surprise.title}'",
            metadata={
                "event_id": surprise.event_id,
                "title": surprise.title,
                "impacted_areas": [
                    d.value if hasattr(d, "value") else str(d) for d in surprise.impacted_areas
                ],
                "parameter_deltas": surprise.parameter_deltas,
            },
        )

    def log_error(
        self,
        phase: SwarmPhase,
        error: str,
        agent_id: Optional[str] = None,
    ) -> ExecutionTrace:
        """Logs system-level errors or exceptions."""
        return self.log_event(
            phase=phase,
            event_type="error",
            agent_id=agent_id,
            summary=f"System error: {error}",
            metadata={"error": error},
        )

    def attach_to_state(self, state: SwarmState) -> None:
        """Synchronizes the collected traces directly into the SwarmState object."""
        state.execution_trace = list(self.traces)

    def get_traces(self) -> List[ExecutionTrace]:
        """Returns a copy of all recorded traces."""
        return list(self.traces)

    def clear(self) -> None:
        """Clears all recorded traces."""
        self.traces.clear()
