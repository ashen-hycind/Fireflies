"""
Core Swarm Orchestrator Engine for Fireflies.

Manages state transitions, task dispatching, inter-agent debate coordination,
strategy comparison, executive CEO synthesis, surprise-event injection, and audit tracing.
"""

from datetime import datetime, timezone
import uuid
from typing import Callable, Dict, List, Optional
from state.schemas import (
    Department,
    SwarmPhase,
    InitialBusinessCase,
    AgentTask,
    AgentAnalysis,
    DebateMessage,
    StrategyComparison,
    CEODecision,
    SurpriseEvent,
    ExecutionTrace,
    SwarmState,
)
from agents.ceo.agent import CEOAgent
from orchestrator.debate import DebateEngine
from orchestrator.strategy import StrategyComparator


# Type signature for a department agent runner function
AgentRunnerFunc = Callable[[InitialBusinessCase, Optional[SurpriseEvent]], AgentAnalysis]


class SwarmOrchestrator:
    """End-to-end multi-agent orchestration engine."""

    def __init__(
        self,
        ceo_agent: Optional[CEOAgent] = None,
        debate_engine: Optional[DebateEngine] = None,
        strategy_comparator: Optional[StrategyComparator] = None,
    ):
        self.ceo_agent = ceo_agent or CEOAgent()
        self.debate_engine = debate_engine or DebateEngine()
        self.strategy_comparator = strategy_comparator or StrategyComparator()
        self.registered_agents: Dict[str, AgentRunnerFunc] = {}

    def register_agent(self, department: str, runner: AgentRunnerFunc):
        """Registers a custom department runner (e.g. from Person B or Person C)."""
        self.registered_agents[department.lower()] = runner

    def _create_trace(
        self,
        phase: SwarmPhase,
        event_type: str,
        summary: str,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> ExecutionTrace:
        """Helper to create a structured ExecutionTrace event."""
        return ExecutionTrace(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            phase=phase,
            agent_id=agent_id,
            event_type=event_type,
            summary=summary,
            metadata=metadata or {},
        )

    def _fallback_mock_analysis(self, department: str, business_case: InitialBusinessCase) -> AgentAnalysis:
        """Fallback mock analyzer used for development or if an agent fails."""
        opt_names = [opt.name for opt in business_case.candidate_options]
        return AgentAnalysis(
            agent_id=f"mock_{department}",
            agent_role=f"{department.capitalize()} Analyst",
            findings=[
                f"Evaluated {business_case.facts.company_name} baseline metrics for {department}.",
                f"Core opportunity aligns with {opt_names[0] if opt_names else 'Option A'}.",
            ],
            recommendation=f"Support {business_case.candidate_options[0].option_id} with strict milestone gating.",
            evidence=[
                f"Current revenue: {business_case.facts.financial_baseline.get('annual_recurring_revenue', 'N/A')}",
            ],
            assumptions=[
                f"Standard market growth remains stable over the {business_case.context.timeline} horizon.",
            ],
            risks=[
                f"Execution risk regarding {department} resource allocation.",
            ],
            confidence=0.85,
        )

    def run_full_swarm(
        self,
        business_case: InitialBusinessCase,
        surprise_event: Optional[SurpriseEvent] = None,
    ) -> SwarmState:
        """
        Executes the complete boardroom decision workflow:
        Analyse -> Share & Challenge (Debate) -> Compare Strategies -> Decide (CEO) -> Surprise Adaptation.
        """
        state = SwarmState(
            phase=SwarmPhase.INITIAL_ANALYSIS,
            business_case=business_case,
        )

        state.execution_trace.append(
            self._create_trace(
                phase=SwarmPhase.INITIAL_ANALYSIS,
                event_type="agent_started",
                summary=f"Swarm initiated for case: {business_case.facts.company_name}",
            )
        )

        # -------------------------------------------------------------
        # 1. Phase 1: Department Analysis Dispatch (Research, Finance, Marketing)
        # -------------------------------------------------------------
        required_departments = [Department.RESEARCH.value, Department.FINANCE.value, Department.MARKETING.value]
        
        for dept in required_departments:
            task_id = f"task_{dept}_{uuid.uuid4().hex[:6]}"
            task = AgentTask(
                task_id=task_id,
                agent_id=dept,
                objective=f"Analyze {business_case.facts.company_name} from {dept} perspective.",
                status="running",
            )
            state.tasks.append(task)
            
            try:
                if dept in self.registered_agents:
                    analysis = self.registered_agents[dept](business_case, None)
                else:
                    analysis = self._fallback_mock_analysis(dept, business_case)
                
                state.department_analyses[dept] = analysis
                task.status = "completed"
                state.execution_trace.append(
                    self._create_trace(
                        phase=SwarmPhase.INITIAL_ANALYSIS,
                        event_type="agent_completed",
                        agent_id=dept,
                        summary=f"{dept.capitalize()} completed initial analysis with recommendation: {analysis.recommendation}",
                    )
                )
            except Exception as e:
                task.status = "failed"
                task.error = str(e)
                state.errors.append(f"Department agent '{dept}' failed: {e}. Applying fallback.")
                # Fallback to keep swarm resilient
                state.department_analyses[dept] = self._fallback_mock_analysis(dept, business_case)

        # -------------------------------------------------------------
        # 2. Phase 2: Boardroom Debate & Cross-Challenge
        # -------------------------------------------------------------
        state.phase = SwarmPhase.DEBATE_CHALLENGE
        state.execution_trace.append(
            self._create_trace(
                phase=SwarmPhase.DEBATE_CHALLENGE,
                event_type="agent_started",
                summary="Initiating inter-department cross-examination and challenge round.",
            )
        )
        try:
            debate_msgs = self.debate_engine.run_debate(business_case, state.department_analyses)
            state.debate_messages = debate_msgs
            for msg in debate_msgs:
                state.execution_trace.append(
                    self._create_trace(
                        phase=SwarmPhase.DEBATE_CHALLENGE,
                        event_type="challenge" if msg.message_type == "challenge" else "message_sent",
                        agent_id=msg.from_agent,
                        summary=f"[{msg.from_agent} -> {msg.to_agent or 'all'} ({msg.message_type})]: {msg.content[:100]}...",
                    )
                )
        except Exception as e:
            state.errors.append(f"Debate phase error: {e}")

        # -------------------------------------------------------------
        # 3. Phase 3: Strategy Matrix Comparison
        # -------------------------------------------------------------
        state.phase = SwarmPhase.STRATEGY_COMPARISON
        try:
            strat_comp = self.strategy_comparator.compare_strategies(
                business_case=business_case,
                department_analyses=state.department_analyses,
                debate_messages=state.debate_messages,
            )
            state.strategy_comparison = strat_comp
            state.execution_trace.append(
                self._create_trace(
                    phase=SwarmPhase.STRATEGY_COMPARISON,
                    event_type="strategy_comparison",
                    summary=f"Strategy comparison generated. Leading option: {strat_comp.preferred_option}",
                )
            )
        except Exception as e:
            state.errors.append(f"Strategy comparison error: {e}")

        # -------------------------------------------------------------
        # 4. Phase 4: Baseline CEO Decision
        # -------------------------------------------------------------
        state.phase = SwarmPhase.BASELINE_DECISION
        try:
            baseline_dec = self.ceo_agent.synthesize_baseline_decision(
                business_case=business_case,
                department_analyses=state.department_analyses,
                debate_messages=state.debate_messages,
                strategy_comparison=state.strategy_comparison or StrategyComparison(
                    evaluations=[], preferred_option=business_case.candidate_options[0].option_id
                ),
            )
            state.baseline_decision = baseline_dec
            state.execution_trace.append(
                self._create_trace(
                    phase=SwarmPhase.BASELINE_DECISION,
                    event_type="decision",
                    agent_id="ceo",
                    summary=f"CEO formulated baseline decision: '{baseline_dec.decision_statement}' (Option: {baseline_dec.selected_option_id})",
                )
            )
        except Exception as e:
            state.errors.append(f"CEO baseline decision error: {e}")

        # -------------------------------------------------------------
        # 5. Phase 5: Surprise Injection & Adaptation (if provided)
        # -------------------------------------------------------------
        if surprise_event:
            state.phase = SwarmPhase.SURPRISE_INJECTION
            state.surprise = surprise_event
            state.execution_trace.append(
                self._create_trace(
                    phase=SwarmPhase.SURPRISE_INJECTION,
                    event_type="surprise_injected",
                    summary=f"Surprise injected: '{surprise_event.title}'. Impacted: {[d.value for d in surprise_event.impacted_areas]}",
                )
            )

            state.phase = SwarmPhase.ADAPTATION_RERUN
            # Rerun only impacted departments
            for dept_enum in surprise_event.impacted_areas:
                dept = dept_enum.value
                if dept == Department.CEO.value:
                    continue  # CEO runs in the final synthesis
                
                try:
                    if dept in self.registered_agents:
                        adapted_analysis = self.registered_agents[dept](business_case, surprise_event)
                    else:
                        adapted_analysis = self._fallback_mock_analysis(dept, business_case)
                        adapted_analysis.findings.append(f"Adapted for surprise: {surprise_event.title}")
                    
                    state.adapted_analyses[dept] = adapted_analysis
                    state.execution_trace.append(
                        self._create_trace(
                            phase=SwarmPhase.ADAPTATION_RERUN,
                            event_type="agent_completed",
                            agent_id=dept,
                            summary=f"{dept.capitalize()} completed adapted analysis after surprise event.",
                        )
                    )
                except Exception as e:
                    state.errors.append(f"Adapted rerun for '{dept}' failed: {e}")

            # Re-evaluate strategy matrix under adapted conditions
            all_current_analyses = {**state.department_analyses, **state.adapted_analyses}
            adapted_strategy = self.strategy_comparator.compare_strategies(
                business_case=business_case,
                department_analyses=all_current_analyses,
                debate_messages=state.debate_messages,
            )
            state.adapted_strategy_comparison = adapted_strategy

            # CEO Adapted Decision
            state.phase = SwarmPhase.FINAL_ADAPTED_DECISION
            try:
                adapted_dec = self.ceo_agent.synthesize_adapted_decision(
                    business_case=business_case,
                    baseline_decision=state.baseline_decision or CEODecision(
                        selected_option_id=business_case.candidate_options[0].option_id,
                        decision_statement="Initial fallback",
                        kpis=["KPI1", "KPI2", "KPI3"]
                    ),
                    surprise_event=surprise_event,
                    adapted_analyses=state.adapted_analyses,
                    adapted_strategy_comparison=adapted_strategy,
                )
                state.adapted_decision = adapted_dec
                state.execution_trace.append(
                    self._create_trace(
                        phase=SwarmPhase.FINAL_ADAPTED_DECISION,
                        event_type="decision",
                        agent_id="ceo",
                        summary=f"CEO formulated adapted decision: '{adapted_dec.decision_statement}'",
                    )
                )
            except Exception as e:
                state.errors.append(f"Adapted CEO decision error: {e}")

        state.phase = SwarmPhase.COMPLETED
        return state
