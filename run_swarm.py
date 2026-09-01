"""
Fireflies Swarm CLI Entrypoint.

Executes the multi-agent decision swarm on official competition test cases:
- Theme A: FINSWARM (FinNova Capital - Indian Digital Lending)
- Theme B: SAASSWARM (OrbitFlow Software - B2B AI Workflow SaaS)
- Theme C: CHIPSWARM (IndusCompute Hub - GPU Module Assembly)
"""

import sys
import argparse
from orchestrator.engine import SwarmOrchestrator
from tests.actual_cases import (
    TEST_CASES_REGISTRY,
    FINSWARM_TC1_CASE,
    FINSWARM_TC2_SURPRISE,
)

try:
    from traces.formatter import TraceFormatter
    HAS_FORMATTER = True
except ImportError:
    HAS_FORMATTER = False


def main():
    parser = argparse.ArgumentParser(description="Fireflies Multi-Agent Swarm Decision Runner")
    parser.add_argument(
        "--case",
        type=str,
        default="FINSWARM_TC2",
        help="Case ID to run (e.g. FINSWARM_TC1, FINSWARM_TC2, SAASSWARM_TC2, CHIPSWARM_TC2)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available competition test cases",
    )
    args = parser.parse_args()

    if args.list:
        print("\n📋 AVAILABLE COMPETITION TEST CASES:")
        print("=" * 60)
        for case_id, (b_case, surprise) in TEST_CASES_REGISTRY.items():
            surprise_str = f" | Surprise: {surprise.title}" if surprise else " | Baseline Only"
            print(f"• {case_id:<16}: {b_case.facts.company_name} ({b_case.facts.industry}){surprise_str}")
        print("=" * 60)
        return

    case_key = args.case.upper()
    if case_key not in TEST_CASES_REGISTRY:
        print(f"⚠️ Case '{args.case}' not found in registry. Defaulting to 'FINSWARM_TC2'.")
        case_key = "FINSWARM_TC2"

    business_case, surprise_event = TEST_CASES_REGISTRY[case_key]

    print("=" * 75)
    print("🔥 FIREFLIES AGENTIC SWARM — BOARDROOM DECISION SYSTEM 🔥")
    print("=" * 75)
    print(f"\n📂 Active Case: [{case_key}] — {business_case.facts.company_name}")
    print(f"🏢 Industry: {business_case.facts.industry}")
    print(f"🎯 Objective: {business_case.context.primary_objective}")
    print(f"📊 Candidate Options: {[opt.name for opt in business_case.candidate_options]}")
    if surprise_event:
        print(f"⚡ Disruption Event: {surprise_event.title}")

    print("\n🚀 Executing Multi-Agent Boardroom Decision Swarm...")
    orchestrator = SwarmOrchestrator()
    final_state = orchestrator.run_full_swarm(
        business_case=business_case,
        surprise_event=surprise_event,
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
    print(f"✅ Swarm run completed for case: {case_key}")
    print("=" * 75)


if __name__ == "__main__":
    main()
