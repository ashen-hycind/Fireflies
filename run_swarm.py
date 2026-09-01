"""
Fireflies Swarm CLI Entrypoint.

Demonstrates running the integrated multi-agent decision swarm end-to-end on a business case.
"""

import sys
from orchestrator.engine import SwarmOrchestrator
from tests.mock_cases import SAAS_EXPANSION_CASE, SAAS_SURPRISE_EVENT

try:
    from traces.formatter import TraceFormatter
    HAS_FORMATTER = True
except ImportError:
    HAS_FORMATTER = False


def main():
    print("=" * 75)
    print("🔥 FIREFLIES AGENTIC SWARM — BOARDROOM DECISION SYSTEM 🔥")
    print("=" * 75)

    orchestrator = SwarmOrchestrator()

    print(f"\n📂 Loading Business Case: {SAAS_EXPANSION_CASE.facts.company_name}")
    print(f"🎯 Objective: {SAAS_EXPANSION_CASE.context.primary_objective}")
    print(f"📊 Candidate Options: {[opt.name for opt in SAAS_EXPANSION_CASE.candidate_options]}")

    print("\n🚀 Executing Multi-Agent Boardroom Decision Swarm...")
    final_state = orchestrator.run_full_swarm(
        business_case=SAAS_EXPANSION_CASE,
        surprise_event=SAAS_SURPRISE_EVENT,
    )

    if HAS_FORMATTER:
        TraceFormatter.render_terminal(final_state)
    else:
        print("\n" + "=" * 75)
        print("📋 BOARDROOM EXECUTION SUMMARY")
        print("=" * 75)
        print(f"Final Phase: {final_state.phase.value}")
        print(f"Total Audit Events: {len(final_state.execution_trace)}")
        print(f"Errors Logged: {len(final_state.errors)}")

        print("\n--- 1. DEPARTMENT ANALYSES ---")
        for dept, analysis in final_state.department_analyses.items():
            print(f"• {dept.upper()}: {analysis.recommendation}")
            print(f"  Confidence: {analysis.confidence}")

        print("\n--- 2. BOARDROOM DEBATE ---")
        for msg in final_state.debate_messages:
            print(f"• [{msg.from_agent} -> {msg.to_agent or 'all'} ({msg.message_type})]: {msg.content}")

        if final_state.baseline_decision:
            print("\n--- 3. BASELINE CEO DECISION ---")
            print(f"• Selected Option: {final_state.baseline_decision.selected_option_id}")
            print(f"• Decision: {final_state.baseline_decision.decision_statement}")
            print(f"• KPIs: {final_state.baseline_decision.kpis}")

        if final_state.adapted_decision:
            print("\n--- 4. ADAPTED CEO DECISION (POST-SURPRISE) ---")
            print(f"• Adapted Option: {final_state.adapted_decision.selected_option_id}")
            print(f"• Decision: {final_state.adapted_decision.decision_statement}")
            print(f"• Updated KPIs: {final_state.adapted_decision.kpis}")

    print("\n" + "=" * 75)
    print("✅ Swarm run completed successfully.")
    print("=" * 75)


if __name__ == "__main__":
    main()
