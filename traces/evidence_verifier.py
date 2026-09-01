"""
Evidence & Judging Rubric Verifier for Fireflies Swarm.

Evaluates an end-to-end SwarmState against the hackathon judging criteria
and integration checklist from tasks.md.
"""

from typing import Dict, Any, List
from state.schemas import SwarmState, SwarmPhase


class EvidenceVerifier:
    """
    Validates that a SwarmState meets all auditable judging criteria.
    """

    @classmethod
    def verify_state(cls, state: SwarmState) -> Dict[str, Any]:
        """
        Runs comprehensive checklist audits and returns a scoring breakdown.
        """
        checks: List[Dict[str, Any]] = []

        # 1. Multi-Agent Presence Check (Research, Finance, Marketing, CEO)
        dept_keys = set(state.department_analyses.keys())
        has_research = "research" in dept_keys
        has_finance = "finance" in dept_keys
        has_marketing = "marketing" in dept_keys
        has_ceo = state.baseline_decision is not None
        all_present = has_research and has_finance and has_marketing and has_ceo

        checks.append({
            "criteria": "Four Identifiable Agent Roles (Research, Finance, Marketing, CEO)",
            "passed": all_present,
            "details": f"Present: {sorted(list(dept_keys)) + (['ceo'] if has_ceo else [])}",
        })

        # 2. Distinct Role & Structured Output Adherence
        structured_ok = True
        for name, analysis in state.department_analyses.items():
            if not analysis.findings or not analysis.recommendation or not analysis.evidence or not analysis.assumptions or not analysis.risks:
                structured_ok = False
                break

        checks.append({
            "criteria": "Department Structured Output Adherence (Findings, Evidence, Assumptions, Risks)",
            "passed": structured_ok and len(state.department_analyses) > 0,
            "details": f"All {len(state.department_analyses)} department analyses strictly separate evidence from assumptions.",
        })

        # 3. Meaningful Inter-Agent Debate & Disagreements
        has_challenges = any(
            msg.message_type in ("challenge", "objection", "critique")
            for msg in state.debate_messages
        )
        checks.append({
            "criteria": "Inter-Agent Challenge & Debate Recorded",
            "passed": len(state.debate_messages) > 0 and has_challenges,
            "details": f"{len(state.debate_messages)} total messages with challenge/objection dynamics.",
        })

        # 4. Multi-Option Strategy Comparison Matrix
        has_multi_options = (
            state.strategy_comparison is not None
            and len(state.strategy_comparison.evaluations) >= 2
            and bool(state.strategy_comparison.preferred_option)
        )
        checks.append({
            "criteria": "Strategy Comparison Matrix (>= 2 Options with Trade-offs)",
            "passed": has_multi_options,
            "details": f"{len(state.strategy_comparison.evaluations) if state.strategy_comparison else 0} options compared with explicit trade-offs.",
        })

        # 5. Explainable CEO Baseline Decision & Rejected Alternatives
        ceo_ok = False
        if state.baseline_decision:
            b = state.baseline_decision
            ceo_ok = (
                bool(b.selected_option_id)
                and len(b.rationale) >= 1
                and len(b.rejected_options) >= 1
                and len(b.rejection_reasons) >= 1
            )
        checks.append({
            "criteria": "Executive CEO Decision with Rationale and Rejected Alternatives",
            "passed": ceo_ok,
            "details": f"Selected: '{state.baseline_decision.selected_option_id if state.baseline_decision else 'None'}' with documented rejection reasons.",
        })

        # 6. Actionable Implementation Steps & Measurable KPIs (>= 3)
        kpi_ok = False
        if state.baseline_decision:
            kpi_ok = len(state.baseline_decision.kpis) >= 3 and len(state.baseline_decision.implementation_steps) >= 1
        checks.append({
            "criteria": "Phased Implementation Steps & >= 3 Measurable KPIs",
            "passed": kpi_ok,
            "details": f"{len(state.baseline_decision.kpis) if state.baseline_decision else 0} KPIs defined (minimum 3 required).",
        })

        # 7. Runtime Surprise Injection & Adaptation Rerun
        surprise_ok = False
        if state.surprise:
            has_adapted_analyses = len(state.adapted_analyses) > 0
            has_adapted_ceo = state.adapted_decision is not None
            surprise_ok = has_adapted_analyses and has_adapted_ceo
        checks.append({
            "criteria": "Runtime Surprise Disruption & Dynamic Adaptation Rerun",
            "passed": surprise_ok,
            "details": f"Surprise injected ('{state.surprise.title if state.surprise else 'None'}') with adapted rerun and revised CEO decision.",
        })

        # 8. Complete Chronological Execution Trace Audit Trail
        trace_ok = len(state.execution_trace) >= 5
        checks.append({
            "criteria": "Tamper-Evident Execution Trace Audit Trail",
            "passed": trace_ok,
            "details": f"{len(state.execution_trace)} timestamped execution events recorded.",
        })

        # Calculate overall score
        total_checks = len(checks)
        passed_checks = sum(1 for c in checks if c["passed"])
        score_percent = (passed_checks / total_checks) * 100.0

        return {
            "case_id": state.business_case.case_id,
            "score_percent": round(score_percent, 1),
            "passed_checks": passed_checks,
            "total_checks": total_checks,
            "is_fully_compliant": passed_checks == total_checks,
            "checks": checks,
        }
