"""
Fireflies Swarm CLI Entrypoint.

Executes the multi-agent decision swarm across all testcases (TC1 Baseline + TC2-TC5 Surprises)
for the selected company theme:
- Theme A: FINSWARM (FinNova Capital - Indian Digital Lending)
- Theme B: SAASSWARM (OrbitFlow Software - B2B AI Workflow SaaS)
- Theme C: CHIPSWARM (IndusCompute Hub - GPU Module Assembly)
"""

import sys
import argparse
from typing import List, Tuple, Optional
from orchestrator.engine import SwarmOrchestrator
from state.schemas import InitialBusinessCase, SurpriseEvent
from tests.actual_cases import (
    # Theme A
    FINSWARM_TC1_CASE,
    FINSWARM_TC2_SURPRISE,
    FINSWARM_TC3_SURPRISE,
    FINSWARM_TC4_SURPRISE,
    FINSWARM_TC5_SURPRISE,
    # Theme B
    SAASSWARM_TC1_CASE,
    SAASSWARM_TC2_SURPRISE,
    SAASSWARM_TC3_SURPRISE,
    SAASSWARM_TC4_SURPRISE,
    SAASSWARM_TC5_SURPRISE,
    # Theme C
    CHIPSWARM_TC1_CASE,
    CHIPSWARM_TC2_SURPRISE,
    CHIPSWARM_TC3_SURPRISE,
    CHIPSWARM_TC4_SURPRISE,
    CHIPSWARM_TC5_SURPRISE,
    TEST_CASES_REGISTRY,
)

# Safe console encoding configuration for Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from traces.formatter import TraceFormatter
    HAS_FORMATTER = True
except ImportError:
    HAS_FORMATTER = False


THEMES = {
    "A": {
        "name": "THEME A: FINSWARM -- FinNova Capital (Digital MSME Lending)",
        "base_case": FINSWARM_TC1_CASE,
        "scenarios": [
            ("TC1 -- BASELINE LAUNCH", None),
            ("TC2 -- SURPRISE: CREDIT-RISK SPIKE", FINSWARM_TC2_SURPRISE),
            ("TC3 -- SURPRISE: MARKETING BUDGET CUT", FINSWARM_TC3_SURPRISE),
            ("TC4 -- SURPRISE: STRICTER VERIFICATION REQUIREMENTS", FINSWARM_TC4_SURPRISE),
            ("TC5 -- LIVE TEST: FUNDING-COST & FRAUD SHOCK", FINSWARM_TC5_SURPRISE),
        ],
    },
    "B": {
        "name": "THEME B: SAASSWARM -- OrbitFlow Software (B2B AI SaaS)",
        "base_case": SAASSWARM_TC1_CASE,
        "scenarios": [
            ("TC1 -- BASELINE MVP & MARKET CHOICE", None),
            ("TC2 -- SURPRISE: COMPETITOR PRICE CUT", SAASSWARM_TC2_SURPRISE),
            ("TC3 -- SURPRISE: ENTERPRISE SECURITY REQUIREMENTS", SAASSWARM_TC3_SURPRISE),
            ("TC4 -- SURPRISE: OUTAGES & CUSTOMER CHURN", SAASSWARM_TC4_SURPRISE),
            ("TC5 -- LIVE TEST: STRATEGIC CUSTOMER REQUEST", SAASSWARM_TC5_SURPRISE),
        ],
    },
    "C": {
        "name": "THEME C: CHIPSWARM -- IndusCompute Hub (GPU Module Assembly)",
        "base_case": CHIPSWARM_TC1_CASE,
        "scenarios": [
            ("TC1 -- BASELINE PRODUCTION ALLOCATION", None),
            ("TC2 -- SURPRISE: CRITICAL COMPONENT DELAY", CHIPSWARM_TC2_SURPRISE),
            ("TC3 -- SURPRISE: AI DEMAND & ENERGY-COST SURGE", CHIPSWARM_TC3_SURPRISE),
            ("TC4 -- SURPRISE: PACKAGING-YIELD DECLINE", CHIPSWARM_TC4_SURPRISE),
            ("TC5 -- LIVE TEST: EXPORT-RESTRICTION REALLOCATION", CHIPSWARM_TC5_SURPRISE),
        ],
    },
}


def run_single_scenario(
    orchestrator: SwarmOrchestrator,
    title: str,
    base_case: InitialBusinessCase,
    surprise_event: Optional[SurpriseEvent] = None,
):
    print("\n" + "=" * 80)
    print(f">> SCENARIO: {title}")
    print("=" * 80)
    if surprise_event:
        print(f">> INJECTED DISRUPTION: {surprise_event.title}")
        print(f">> DESCRIPTION: {surprise_event.description}")
    else:
        print(f">> BASELINE OBJECTIVE: {base_case.context.primary_objective}")

    final_state = orchestrator.run_full_swarm(
        business_case=base_case,
        surprise_event=surprise_event,
    )

    if HAS_FORMATTER:
        TraceFormatter.render_terminal(final_state)
    else:
        print(f"\n[Status: {final_state.phase.value}]")
        if final_state.baseline_decision:
            print(f"• Baseline Decision: {final_state.baseline_decision.decision_statement}")
            print(f"  Selected: {final_state.baseline_decision.selected_option_id} | KPIs: {final_state.baseline_decision.kpis}")
        if final_state.adapted_decision:
            print(f"• Adapted Decision: {final_state.adapted_decision.decision_statement}")
            print(f"  Selected: {final_state.adapted_decision.selected_option_id} | Updated KPIs: {final_state.adapted_decision.kpis}")

    return final_state


def main():
    parser = argparse.ArgumentParser(description="Fireflies Multi-Agent Swarm Runner")
    parser.add_argument(
        "--theme",
        type=str,
        default="A",
        choices=["A", "B", "C", "ALL", "a", "b", "c", "all"],
        help="Run all TC1-TC5 scenarios for Theme A (FinSwarm), Theme B (SaaSSwarm), Theme C (ChipSwarm), or ALL",
    )
    parser.add_argument(
        "--case",
        type=str,
        default=None,
        help="Run a specific single case ID (e.g. FINSWARM_TC1, FINSWARM_TC2, SAASSWARM_TC3)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available themes and test cases",
    )
    args = parser.parse_args()

    if args.list:
        print("\n=== AVAILABLE THEMES & TEST CASES ===")
        print("=" * 70)
        for t_key, t_data in THEMES.items():
            print(f"\n[THEME] {t_data['name']}:")
            for title, s_event in t_data["scenarios"]:
                s_str = f" [Surprise: {s_event.title}]" if s_event else " [Baseline Only]"
                print(f"   • {title}{s_str}")
        print("=" * 70)
        return

    orchestrator = SwarmOrchestrator()

    # Single specific case mode
    if args.case:
        case_key = args.case.upper()
        if case_key in TEST_CASES_REGISTRY:
            b_case, s_event = TEST_CASES_REGISTRY[case_key]
            run_single_scenario(orchestrator, case_key, b_case, s_event)
            return
        else:
            print(f"Case '{args.case}' not found in registry. Running default theme.")

    # Default Theme Mode (Runs all TC1 through TC5 for the selected theme)
    theme_choice = args.theme.upper()
    themes_to_run = ["A", "B", "C"] if theme_choice == "ALL" else [theme_choice]

    print("=" * 80)
    print("FIREFLIES AGENTIC SWARM -- COMPLETE BOARDROOM EVALUATION SUITE")
    print("=" * 80)

    for t_key in themes_to_run:
        theme = THEMES[t_key]
        print("\n" + "#" * 80)
        print(f"STARTING {theme['name']}")
        print("Running all 5 Testcases (TC1 Baseline + TC2-TC5 Runtime Disruptions)...")
        print("#" * 80)

        for idx, (tc_title, surprise_event) in enumerate(theme["scenarios"], 1):
            run_single_scenario(
                orchestrator=orchestrator,
                title=f"[{t_key}.{idx}] {tc_title}",
                base_case=theme["base_case"],
                surprise_event=surprise_event,
            )

    print("\n" + "=" * 80)
    print("ALL TEST SCENARIOS EXECUTED SUCCESSFULLY.")
    print("=" * 80)


if __name__ == "__main__":
    main()
