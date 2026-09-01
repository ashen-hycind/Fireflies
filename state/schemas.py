"""
Fireflies Agentic Swarm - Core Pydantic Schemas & State Management.

Defines the complete data contract for the multi-agent decision swarm:
- InitialBusinessCase (Facts, Decision Context, Candidate Options)
- AgentTask (Orchestration & Failure Tracking)
- AgentAnalysis (Department Outputs: Research, Finance, Marketing)
- DebateMessage (Inter-Agent Challenges & Responses)
- StrategyComparison (Comparative Matrix: Option A vs Option B)
- CEODecision (Executive Decision, KPIs, Implementation Steps)
- SurpriseEvent (Runtime Disruption & Impact Vector)
- ExecutionTrace (Audit Trail for Real-Time & Historical Evaluation)
- SwarmState (End-to-End Orchestrator State)
"""

from __future__ import annotations
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


# ==========================================
# 1. Enums
# ==========================================

class Department(str, Enum):
    RESEARCH = "research"
    FINANCE = "finance"
    MARKETING = "marketing"
    CEO = "ceo"


class SwarmPhase(str, Enum):
    INITIAL_ANALYSIS = "initial_analysis"
    DEBATE_CHALLENGE = "debate_challenge"
    STRATEGY_COMPARISON = "strategy_comparison"
    BASELINE_DECISION = "baseline_decision"
    SURPRISE_INJECTION = "surprise_injection"
    ADAPTATION_RERUN = "adaptation_rerun"
    FINAL_ADAPTED_DECISION = "final_adapted_decision"
    COMPLETED = "completed"
    FAILED = "failed"


# ==========================================
# 2. Initial Business Case Schemas (Immutable Baseline)
# ==========================================

class BusinessFacts(BaseModel):
    """Ground truth baseline facts about the business and its environment."""
    company_name: str = Field(description="Name and overview of the company")
    industry: str = Field(description="Industry / market sector")
    financial_baseline: Dict[str, Any] = Field(
        default_factory=dict,
        description="Factual financial metrics (e.g. revenue, burn rate, runway, margins)"
    )
    operational_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Factual operational metrics (e.g. team size, customer count, unit costs)"
    )
    market_facts: List[str] = Field(
        default_factory=list,
        description="Verified market data, competitor baseline, regulatory conditions"
    )


class DecisionContext(BaseModel):
    """Decision goals, horizons, and hard operating constraints."""
    problem_statement: str = Field(description="The core strategic question or dilemma")
    primary_objective: str = Field(description="Primary goal or target outcome")
    budget_limit: Optional[str] = Field(default=None, description="Hard budget constraint if applicable")
    timeline: str = Field(description="Decision and execution timeframe (e.g. '6 months')")
    hard_constraints: List[str] = Field(
        default_factory=list,
        description="Non-negotiable legal, operational, or resource constraints"
    )


class StrategicOption(BaseModel):
    """Candidate strategic option provided or formulated for evaluation."""
    option_id: str = Field(description="Unique option ID, e.g. 'OPTION_A', 'OPTION_B'")
    name: str = Field(description="Clear title of the strategic option")
    description: str = Field(description="Summary of the proposed approach")
    intended_mechanism: str = Field(description="How this strategic option achieves the primary objective")


class InitialBusinessCase(BaseModel):
    """Clean initial input payload without any surprise event data leakage."""
    case_id: str = Field(description="Unique identifier for the testcase")
    facts: BusinessFacts = Field(description="Verified baseline facts")
    context: DecisionContext = Field(description="Decision parameters, goals, and constraints")
    candidate_options: List[StrategicOption] = Field(
        description="Strategic paths to evaluate (minimum 2)"
    )


# ==========================================
# 3. Agent Task & Department Analysis Schemas
# ==========================================

class AgentTask(BaseModel):
    """Task assigned by the orchestrator to an agent (for routing & retry/failure handling)."""
    task_id: str
    agent_id: str
    objective: str
    input_context: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="pending", description="pending | running | completed | failed")
    retry_count: int = 0
    error: Optional[str] = None


class AgentAnalysis(BaseModel):
    """Structured analytical output produced by a department agent."""
    agent_id: str
    agent_role: str
    findings: List[str] = Field(
        default_factory=list,
        description="Key analytical findings derived from the business case"
    )
    recommendation: str = Field(
        description="The agent's recommended course of action"
    )
    evidence: List[str] = Field(
        default_factory=list,
        description="Facts or provided data directly supporting the recommendation"
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Explicit assumptions used during reasoning"
    )
    risks: List[str] = Field(
        default_factory=list,
        description="Domain-specific risks identified by the agent"
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Agent confidence score in its recommendation (0.0 to 1.0)"
    )


# ==========================================
# 4. Debate & Challenge Schemas
# ==========================================

class DebateMessage(BaseModel):
    """Inter-agent communication message during boardroom debate & challenge."""
    message_id: str
    from_agent: str
    to_agent: Optional[str] = None
    message_type: str = Field(
        description="challenge | response | clarification | agreement | objection"
    )
    content: str = Field(description="The body of the message / critique / defense")
    referenced_agent: Optional[str] = None
    referenced_claim: Optional[str] = None
    requires_response: bool = False


# ==========================================
# 5. Strategy Comparison Schemas
# ==========================================

class StrategyEvaluation(BaseModel):
    """Multi-dimensional evaluation of a single strategic option."""
    option_id: str
    advantages: List[str] = Field(default_factory=list)
    disadvantages: List[str] = Field(default_factory=list)
    financial_impact: Optional[str] = None
    market_impact: Optional[str] = None
    operational_impact: Optional[str] = None
    risks: List[str] = Field(default_factory=list)
    supporting_agents: List[str] = Field(default_factory=list)


class StrategyComparison(BaseModel):
    """Comprehensive comparison matrix across all candidate options."""
    evaluations: List[StrategyEvaluation] = Field(
        description="Evaluations for each candidate strategic option"
    )
    preferred_option: str = Field(
        description="Option ID of the leading strategy following debate"
    )
    trade_offs: List[str] = Field(
        default_factory=list,
        description="Explicit trade-offs between compared strategies"
    )
    unresolved_uncertainties: List[str] = Field(
        default_factory=list,
        description="Remaining uncertainties or assumptions to monitor"
    )


# ==========================================
# 6. Executive CEO Decision Schema
# ==========================================

class CEODecision(BaseModel):
    """Final, explainable executive decision with action plan and measurable KPIs."""
    selected_option_id: str = Field(description="The chosen strategic option ID")
    decision_statement: str = Field(description="Clear, authoritative executive decision summary")
    rationale: List[str] = Field(
        default_factory=list,
        description="Department evidence and strategic justifications supporting the decision"
    )
    rejected_options: List[str] = Field(
        default_factory=list,
        description="List of rejected option IDs"
    )
    rejection_reasons: List[str] = Field(
        default_factory=list,
        description="Specific reasons why alternatives were rejected"
    )
    trade_offs: List[str] = Field(
        default_factory=list,
        description="Key compromises and prioritized trade-offs"
    )
    risks: List[str] = Field(
        default_factory=list,
        description="Identified risks associated with the selected strategy"
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Underlying assumptions that must hold true"
    )
    implementation_steps: List[str] = Field(
        default_factory=list,
        description="Concrete, phased tactical implementation steps"
    )
    kpis: List[str] = Field(
        min_length=3,
        description="At least three measurable business KPIs for tracking success"
    )
    quantitative_adjustments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Explicit Before -> After quantitative deltas, allocation shifts, and financial metrics"
    )
    constraint_checks: List[str] = Field(
        default_factory=list,
        description="Verification audit of hard constraints (e.g. ['Portfolio Default 5.2% <= 5.5% (PASS)'])"
    )


# ==========================================
# 7. Surprise Event & Runtime Adaptation Schemas
# ==========================================

class SurpriseEvent(BaseModel):
    """Runtime disruption injected during the adaptation phase."""
    event_id: str = Field(description="Unique identifier for the surprise event")
    title: str = Field(description="Headline of the unexpected market shift or disruption")
    description: str = Field(description="Detailed narrative of what changed at runtime")
    impacted_areas: List[Department] = Field(
        description="List of departments materially affected that require reruns"
    )
    parameter_deltas: Dict[str, Any] = Field(
        default_factory=dict,
        description="Changed metrics, updated constraints, or new parameters"
    )


# ==========================================
# 8. Execution Trace & Audit Trail Schema
# ==========================================

class ExecutionTrace(BaseModel):
    """Timestamped audit record for real-time visualization and judge evaluation."""
    event_id: str
    timestamp: str
    phase: SwarmPhase
    agent_id: Optional[str] = None
    event_type: str = Field(
        description="agent_started | agent_completed | agent_failed | message_sent | challenge | strategy_comparison | decision | surprise_injected"
    )
    summary: str = Field(description="Human-readable log summary")
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ==========================================
# 9. Full Swarm State (End-to-End Orchestration)
# ==========================================

class SwarmState(BaseModel):
    """Comprehensive runtime state for the Fireflies multi-agent swarm."""
    phase: SwarmPhase = SwarmPhase.INITIAL_ANALYSIS
    business_case: InitialBusinessCase

    # Orchestration & task management
    tasks: List[AgentTask] = Field(default_factory=list)

    # Initial Department Outputs
    department_analyses: Dict[str, AgentAnalysis] = Field(
        default_factory=dict,
        description="Keyed by department name, e.g. {'research': AgentAnalysis, ...}"
    )

    # Debate & Challenge Phase
    debate_messages: List[DebateMessage] = Field(default_factory=list)

    # Strategy Comparison Matrix
    strategy_comparison: Optional[StrategyComparison] = None

    # Baseline CEO Output
    baseline_decision: Optional[CEODecision] = None

    # Runtime Surprise Event
    surprise: Optional[SurpriseEvent] = None

    # Adapted Analyses (post-surprise reruns)
    adapted_analyses: Dict[str, AgentAnalysis] = Field(default_factory=dict)

    # Adapted Strategy Comparison
    adapted_strategy_comparison: Optional[StrategyComparison] = None

    # Final Adapted CEO Decision
    adapted_decision: Optional[CEODecision] = None

    # Complete Audit Trail
    execution_trace: List[ExecutionTrace] = Field(default_factory=list)

    # System-level error log & fallbacks
    errors: List[str] = Field(default_factory=list)
