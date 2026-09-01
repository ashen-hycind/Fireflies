"""
Boardroom Trace & Evidence Formatter for Fireflies Swarm.

Provides rich terminal presentation, structured Markdown boardroom reports,
and JSON serialization for human evaluation, debugging, and hackathon judging.
"""

from typing import Optional, Dict, Any, List
import json
from state.schemas import (
    SwarmState,
    AgentAnalysis,
    CEODecision,
    StrategyComparison,
    SurpriseEvent,
    DebateMessage,
    ExecutionTrace,
)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.tree import Tree
    from rich.layout import Layout
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class TraceFormatter:
    """
    Formats end-to-end swarm state and execution traces into auditable
    visual formats: Rich Terminal Output, Markdown Boardroom Report, and JSON.
    """

    @staticmethod
    def render_terminal(state: SwarmState, console: Optional[Any] = None) -> None:
        """
        Renders the entire boardroom session onto the terminal using Rich.
        """
        if not RICH_AVAILABLE:
            print(TraceFormatter.to_markdown(state))
            return

        c = console or Console()
        facts = state.business_case.facts
        context = state.business_case.context

        # 1. Header Banner
        header_text = Text(
            f"FIREFLIES AGENTIC BOARDROOM SWARM\nCase: {state.business_case.case_id} — {facts.company_name}",
            justify="center",
            style="bold white on blue",
        )
        c.print(Panel(header_text, border_style="bright_blue"))

        # 2. Business Baseline Panel
        baseline_table = Table(title="[bold cyan]Business Case & Operating Constraints[/bold cyan]", show_header=True, header_style="bold magenta")
        baseline_table.add_column("Parameter", style="cyan", width=22)
        baseline_table.add_column("Details", style="white")

        baseline_table.add_row("Company / Industry", f"{facts.company_name} ({facts.industry})")
        baseline_table.add_row("Problem Statement", context.problem_statement)
        baseline_table.add_row("Primary Objective", context.primary_objective)
        baseline_table.add_row("Budget & Timeline", f"Budget: {context.budget_limit or 'N/A'} | Timeline: {context.timeline}")
        baseline_table.add_row("Hard Constraints", "\n".join(f"• {hc}" for hc in context.hard_constraints) if context.hard_constraints else "None")
        baseline_table.add_row("Strategic Options", "\n".join(f"• [{opt.option_id}] {opt.name}: {opt.description}" for opt in state.business_case.candidate_options))

        c.print(baseline_table)
        c.print()

        # 3. Department Analyses (Phase: INITIAL_ANALYSIS)
        if state.department_analyses:
            dept_table = Table(title="[bold green]Initial Department Analyses (Research, Finance, Marketing)[/bold green]", show_header=True, header_style="bold green")
            dept_table.add_column("Department", style="bold yellow", width=14)
            dept_table.add_column("Recommendation", style="bold white", width=30)
            dept_table.add_column("Key Findings & Evidence", style="white", width=40)
            dept_table.add_column("Assumptions & Risks", style="dim white", width=30)
            dept_table.add_column("Conf.", justify="center", width=7)

            for dept_name, analysis in state.department_analyses.items():
                findings_ev = "\n".join([f"• [bold]Finding:[/bold] {f}" for f in analysis.findings[:2]] + [f"• [dim]Evidence:[/dim] {e}" for e in analysis.evidence[:2]])
                assump_risk = "\n".join([f"• [italic]Assump:[/italic] {a}" for a in analysis.assumptions[:2]] + [f"• [red]Risk:[/red] {r}" for r in analysis.risks[:2]])
                conf_str = f"{int(analysis.confidence * 100)}%" if analysis.confidence is not None else "N/A"
                dept_table.add_row(
                    f"{dept_name.upper()}\n({analysis.agent_role})",
                    analysis.recommendation,
                    findings_ev,
                    assump_risk,
                    conf_str,
                )

            c.print(dept_table)
            c.print()

        # 4. Inter-Agent Debate Messages
        if state.debate_messages:
            c.print(Panel("[bold yellow]Boardroom Debate & Inter-Agent Challenges[/bold yellow]", border_style="yellow"))
            for msg in state.debate_messages:
                msg_title = f"[{msg.message_type.upper()}] From: {msg.from_agent.upper()} ➔ To: {(msg.to_agent or 'ALL').upper()}"
                c.print(Panel(
                    msg.content,
                    title=f"[bold cyan]{msg_title}[/bold cyan]",
                    border_style="cyan" if msg.message_type == "challenge" else "dim white",
                    padding=(0, 1),
                ))
            c.print()

        # 5. Strategy Comparison Matrix
        if state.strategy_comparison:
            strat_table = Table(title="[bold magenta]Strategy Comparison Matrix[/bold magenta]", show_header=True, header_style="bold magenta")
            strat_table.add_column("Option ID", style="bold cyan", width=12)
            strat_table.add_column("Advantages", style="green", width=30)
            strat_table.add_column("Disadvantages & Risks", style="red", width=30)
            strat_table.add_column("Impacts (Fin / Mkt / Ops)", style="white", width=30)
            strat_table.add_column("Supporters", style="yellow", width=15)

            for eval_item in state.strategy_comparison.evaluations:
                advs = "\n".join(f"✓ {a}" for a in eval_item.advantages)
                disadvs = "\n".join([f"✗ {d}" for d in eval_item.disadvantages] + [f"⚠ {r}" for r in eval_item.risks])
                impacts = f"Fin: {eval_item.financial_impact or 'N/A'}\nMkt: {eval_item.market_impact or 'N/A'}\nOps: {eval_item.operational_impact or 'N/A'}"
                supporters = ", ".join(eval_item.supporting_agents) or "None"

                strat_table.add_row(eval_item.option_id, advs, disadvs, impacts, supporters)

            c.print(strat_table)
            c.print(f"[bold green]Leading Strategy Preferred by Swarm:[/bold green] [bold underline]{state.strategy_comparison.preferred_option}[/bold underline]")
            c.print()

        # 6. Baseline CEO Decision
        if state.baseline_decision:
            ceo = state.baseline_decision
            ceo_body = Text()
            ceo_body.append(f"SELECTED OPTION: {ceo.selected_option_id}\n\n", style="bold green")
            ceo_body.append(f"DECISION STATEMENT:\n{ceo.decision_statement}\n\n", style="bold white")
            ceo_body.append("KEY RATIONALE:\n" + "\n".join(f"• {r}" for r in ceo.rationale) + "\n\n", style="white")
            if ceo.rejected_options:
                ceo_body.append(f"REJECTED OPTIONS: {', '.join(ceo.rejected_options)}\n", style="bold red")
                ceo_body.append("REJECTION REASONS:\n" + "\n".join(f"• {rr}" for rr in ceo.rejection_reasons) + "\n\n", style="red")
            ceo_body.append("IMPLEMENTATION ROADMAP:\n" + "\n".join(f"1. {step}" for step in ceo.implementation_steps) + "\n\n", style="cyan")
            ceo_body.append("MEASURABLE SUCCESS KPIs:\n" + "\n".join(f"📊 {kpi}" for kpi in ceo.kpis), style="bold yellow")

            c.print(Panel(ceo_body, title="[bold white on dark_green] BASELINE CEO EXECUTIVE DECISION [/bold white on dark_green]", border_style="green"))
            c.print()

        # 7. Surprise Disruption
        if state.surprise:
            sur = state.surprise
            sur_text = Text()
            sur_text.append(f"EVENT: {sur.title} (ID: {sur.event_id})\n\n", style="bold red")
            sur_text.append(f"{sur.description}\n\n", style="white")
            sur_text.append(f"Materially Impacted Areas: {', '.join(d.value if hasattr(d, 'value') else str(d) for d in sur.impacted_areas)}\n", style="bold yellow")
            sur_text.append("Parameter Deltas:\n" + json.dumps(sur.parameter_deltas, indent=2), style="yellow")

            c.print(Panel(sur_text, title="[bold white on red] 🚨 RUNTIME SURPRISE INJECTION [/bold white on red]", border_style="red"))
            c.print()

        # 8. Adapted CEO Decision
        if state.adapted_decision:
            ad_ceo = state.adapted_decision
            ad_body = Text()
            ad_body.append(f"ADAPTED STRATEGY: {ad_ceo.selected_option_id}\n\n", style="bold yellow")
            ad_body.append(f"REVISED DECISION STATEMENT:\n{ad_ceo.decision_statement}\n\n", style="bold white")
            ad_body.append("REVISED RATIONALE:\n" + "\n".join(f"• {r}" for r in ad_ceo.rationale) + "\n\n", style="white")
            ad_body.append("ADAPTED IMPLEMENTATION STEPS:\n" + "\n".join(f"1. {step}" for step in ad_ceo.implementation_steps) + "\n\n", style="cyan")
            ad_body.append("REVISED KPIs:\n" + "\n".join(f"📊 {kpi}" for kpi in ad_ceo.kpis), style="bold yellow")

            c.print(Panel(ad_body, title="[bold white on dark_magenta] 🔄 FINAL ADAPTED CEO DECISION [/bold white on dark_magenta]", border_style="magenta"))
            c.print()

        # 9. Execution Trace Audit Trail
        if state.execution_trace:
            trace_table = Table(title="[bold blue]Chronological Audit Trail (Execution Trace)[/bold blue]", show_header=True, header_style="bold blue")
            trace_table.add_column("Timestamp", style="dim white", width=22)
            trace_table.add_column("Phase", style="cyan", width=22)
            trace_table.add_column("Agent", style="yellow", width=12)
            trace_table.add_column("Event Type", style="magenta", width=18)
            trace_table.add_column("Summary", style="white")

            for t in state.execution_trace[-15:]:  # show recent/key traces
                phase_val = t.phase.value if hasattr(t.phase, "value") else str(t.phase)
                trace_table.add_row(
                    t.timestamp[:19].replace("T", " "),
                    phase_val,
                    t.agent_id or "-",
                    t.event_type,
                    t.summary,
                )

            c.print(trace_table)
            c.print()

    @staticmethod
    def to_markdown(state: SwarmState) -> str:
        """
        Generates a comprehensive, auditable GitHub-Flavored Markdown report of the entire boardroom run.
        """
        facts = state.business_case.facts
        context = state.business_case.context

        lines = [
            f"# Fireflies Swarm Boardroom Audit Report",
            f"**Case ID:** `{state.business_case.case_id}` | **Company:** **{facts.company_name}** (`{facts.industry}`)",
            f"**Current Swarm Phase:** `{state.phase.value if hasattr(state.phase, 'value') else state.phase}`",
            "",
            "---",
            "## 1. Executive Problem Context & Operating Constraints",
            f"- **Problem Statement:** {context.problem_statement}",
            f"- **Primary Objective:** {context.primary_objective}",
            f"- **Budget Limit:** {context.budget_limit or 'Not constrained'}",
            f"- **Timeline:** {context.timeline}",
            "",
            "### Candidate Strategic Options Evaluated:",
        ]

        for opt in state.business_case.candidate_options:
            lines.append(f"- **`{opt.option_id}` — {opt.name}**: {opt.description} *(Mechanism: {opt.intended_mechanism})*")

        lines.extend([
            "",
            "---",
            "## 2. Department Analytical Findings (Initial Analysis Phase)",
        ])

        if state.department_analyses:
            lines.append("| Department | Role | Recommendation | Confidence | Key Evidence | Top Risks |")
            lines.append("|---|---|---|---|---|---|")
            for dept, analysis in state.department_analyses.items():
                ev_str = "<br>".join(f"• {e}" for e in analysis.evidence[:2])
                risk_str = "<br>".join(f"• {r}" for r in analysis.risks[:2])
                conf_str = f"{int(analysis.confidence * 100)}%" if analysis.confidence is not None else "N/A"
                lines.append(f"| **{dept.capitalize()}** | {analysis.agent_role} | {analysis.recommendation} | {conf_str} | {ev_str} | {risk_str} |")
        else:
            lines.append("*No initial department analyses recorded.*")

        lines.extend([
            "",
            "---",
            "## 3. Boardroom Debate & Inter-Agent Challenges",
        ])

        if state.debate_messages:
            for idx, msg in enumerate(state.debate_messages, 1):
                lines.append(f"#### {idx}. [{msg.message_type.upper()}] From: `{msg.from_agent}` ➔ To: `{msg.to_agent or 'all'}`")
                lines.append(f"> {msg.content}")
                lines.append("")
        else:
            lines.append("*No debate messages recorded.*")

        lines.extend([
            "",
            "---",
            "## 4. Strategy Comparison Matrix",
        ])

        if state.strategy_comparison:
            lines.append(f"**Swarm Leading Strategy:** `{state.strategy_comparison.preferred_option}`\n")
            lines.append("| Option ID | Advantages | Disadvantages & Risks | Impacts (Fin / Mkt / Ops) | Supporting Agents |")
            lines.append("|---|---|---|---|---|")
            for eval_item in state.strategy_comparison.evaluations:
                adv_str = "<br>".join(f"✓ {a}" for a in eval_item.advantages)
                dis_str = "<br>".join([f"✗ {d}" for d in eval_item.disadvantages] + [f"⚠ {r}" for r in eval_item.risks])
                imp_str = f"Fin: {eval_item.financial_impact or 'N/A'}<br>Mkt: {eval_item.market_impact or 'N/A'}<br>Ops: {eval_item.operational_impact or 'N/A'}"
                sup_str = ", ".join(eval_item.supporting_agents) or "None"
                lines.append(f"| `{eval_item.option_id}` | {adv_str} | {dis_str} | {imp_str} | {sup_str} |")

            if state.strategy_comparison.trade_offs:
                lines.append("\n**Key Trade-offs:**")
                for to in state.strategy_comparison.trade_offs:
                    lines.append(f"- {to}")
        else:
            lines.append("*No strategy comparison recorded.*")

        lines.extend([
            "",
            "---",
            "## 5. Baseline CEO Executive Decision",
        ])

        if state.baseline_decision:
            ceo = state.baseline_decision
            lines.extend([
                f"### Selected Option: `{ceo.selected_option_id}`",
                f"**Decision Statement:** {ceo.decision_statement}",
                "",
                "#### Strategic Rationale:",
            ])
            for r in ceo.rationale:
                lines.append(f"- {r}")

            if ceo.rejected_options:
                lines.append(f"\n#### Rejected Options (`{', '.join(ceo.rejected_options)}`):")
                for rr in ceo.rejection_reasons:
                    lines.append(f"- {rr}")

            lines.append("\n#### Phased Implementation Roadmap:")
            for i, step in enumerate(ceo.implementation_steps, 1):
                lines.append(f"{i}. {step}")

            lines.append("\n#### Measurable Success KPIs:")
            for kpi in ceo.kpis:
                lines.append(f"- 📊 **{kpi}**")
        else:
            lines.append("*No baseline CEO decision recorded.*")

        if state.surprise:
            sur = state.surprise
            lines.extend([
                "",
                "---",
                "## 6. Runtime Surprise Disruption & Impact",
                f"### 🚨 Disruption: {sur.title} (`{sur.event_id}`)",
                f"> {sur.description}",
                "",
                f"- **Materially Impacted Areas:** `{', '.join(d.value if hasattr(d, 'value') else str(d) for d in sur.impacted_areas)}`",
                "- **Parameter / Metric Deltas:**",
                "```json",
                json.dumps(sur.parameter_deltas, indent=2),
                "```",
            ])

        if state.adapted_decision:
            ad_ceo = state.adapted_decision
            lines.extend([
                "",
                "---",
                "## 7. Post-Surprise Adaptation & Final Revised Decision",
                f"### Revised Strategic Choice: `{ad_ceo.selected_option_id}`",
                f"**Revised Decision Statement:** {ad_ceo.decision_statement}",
                "",
                "#### Revised Rationale:",
            ])
            for r in ad_ceo.rationale:
                lines.append(f"- {r}")

            lines.append("\n#### Phased Tactical Implementation:")
            for i, step in enumerate(ad_ceo.implementation_steps, 1):
                lines.append(f"{i}. {step}")

            lines.append("\n#### Revised Tracking KPIs:")
            for kpi in ad_ceo.kpis:
                lines.append(f"- 📊 **{kpi}**")

        lines.extend([
            "",
            "---",
            "## 8. Complete Chronological Execution Trace (Audit Trail)",
            "| Event ID | Timestamp | Phase | Agent | Event Type | Summary |",
            "|---|---|---|---|---|---|",
        ])

        for t in state.execution_trace:
            phase_val = t.phase.value if hasattr(t.phase, "value") else str(t.phase)
            lines.append(
                f"| `{t.event_id}` | `{t.timestamp[:19]}` | `{phase_val}` | `{t.agent_id or '-'}` | `{t.event_type}` | {t.summary} |"
            )

        return "\n".join(lines)

    @staticmethod
    def to_json(state: SwarmState, filepath: Optional[str] = None) -> str:
        """
        Serializes the complete SwarmState (including all traces) to a formatted JSON string
        and optionally writes to a target file.
        """
        json_data = state.model_dump_json(indent=2)
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_data)
        return json_data
