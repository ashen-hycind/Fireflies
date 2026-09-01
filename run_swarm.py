"""
Fireflies Swarm CLI Entrypoint.

Demonstrates running the multi-agent decision swarm end-to-end on a business case.
"""

import sys
import json
from state.schemas import SwarmPhase
from orchestrator.engine import SwarmOrchestrator
from tests.mock_cases import SAAS_EXPANSION_CASE, SAAS_SURPRISE_EVENT


def main():
    print("=" * 70)
    print("🔥 FIREFLIES AGENTIC SWARM — BOARDROOM DECISION SYSTEM 🔥")
    print("=" * 70)

    orchestrator = SwarmOrchestrator()

    print(f"\n📂 Loading Business Case: {SAAS_EXPANSION_CASE.facts.company_name}")
    print(f"🎯 Objective: {SAAS_EXPANSION_CASE.context.primary_objective}")
    print(f"📊 Candidate Options: {[opt.name for opt in SAAS_EXPANSION_CASE.candidate_options]}")

    print("\n🚀 Executing Swarm (Analyse -> Debate -> Compare -> Decide -> Adapt)...")
    final_state = orchestrator.run_full_swarm(
        business_case=SAAS_EXPANSION_CASE,
        surprise_event=SAAS_SURPRISE_EVENT,
    )

    print("\n" + "=" * 70)
    print("📋 BOARDROOM EXECUTION SUMMARY")
    print("=" * 70)
    print(f"Final Phase: {final_state.phase.value}")
    print(f"Total Audit Events: {len(final_state.execution_trace)}")
    print(f"Errors Logged: {len(final_state.errors)}")

    print("\n--- 1. DEPARTMENT ANALYSES ---")
    for dept, analysis in final_state.department_analyses.items():
        print(f"• {dept.upper()}: Recommendation: {analysis.recommendation}")
        print(f"  Confidence: {analysis.confidence}")
        print(f"  Risks: {analysis.risks}")

    print("\n--- 2. BOARDROOM DEBATE ---")
    for msg in final_state.debate_messages:
        print(f"• [{msg.from_agent} -> {msg.to_agent or 'all'} ({msg.message_type})]: {msg.content}")

    if final_state.strategy_comparison:
        print("\n--- 3. STRATEGY COMPARISON ---")
        print(f"• Preferred Strategy: {final_state.strategy_comparison.preferred_option}")
        print(f"• Trade-offs: {final_state.strategy_comparison.trade_offs}")

    if final_state.baseline_decision:
        print("\n--- 4. BASELINE CEO DECISION ---")
        print(f"• Selected Option: {final_state.baseline_decision.selected_option_id}")
        print(f"• Decision: {final_state.baseline_decision.decision_statement}")
        print(f"• Rationale: {final_state.baseline_decision.rationale}")
        print(f"• Target KPIs: {final_state.baseline_decision.kpis}")

    if final_state.adapted_decision:
        print("\n--- 5. ADAPTED CEO DECISION (POST-SURPRISE) ---")
        print(f"• Surprise: {final_state.surprise.title if final_state.surprise else 'N/A'}")
        print(f"• Adapted Option: {final_state.adapted_decision.selected_option_id}")
        print(f"• Decision: {final_state.adapted_decision.decision_statement}")
        print(f"• Updated KPIs: {final_state.adapted_decision.kpis}")

    print("\n" + "=" * 70)
    print("✅ Swarm run completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()
