"""
Mock business test cases and surprise events for testing the Fireflies Swarm.
"""

from state.schemas import (
    InitialBusinessCase,
    BusinessFacts,
    DecisionContext,
    StrategicOption,
    SurpriseEvent,
    Department,
)

# ==========================================
# Case 1: SaaS Growth Strategy Dilemma
# ==========================================

SAAS_EXPANSION_CASE = InitialBusinessCase(
    case_id="case_saas_001",
    facts=BusinessFacts(
        company_name="CloudMetrics AI",
        industry="B2B Enterprise SaaS / Observability",
        financial_baseline={
            "annual_recurring_revenue": "$8.5M",
            "monthly_burn_rate": "$220,000",
            "cash_runway_months": 16,
            "gross_margin": "78%",
            "net_revenue_retention": "112%",
        },
        operational_metrics={
            "total_headcount": 55,
            "sales_team_size": 12,
            "engineering_team_size": 28,
            "average_contract_value": "$45,000/yr",
            "customer_acquisition_cost": "$28,000",
            "sales_cycle_days": 75,
        },
        market_facts=[
            "Enterprise demand for AI-assisted observability grew 34% YoY.",
            "Two established competitors (DataWatch, AppPulse) hold 60% of the North American market.",
            "European market has stricter GDPR compliance requirements but lower competition for mid-market tier.",
        ],
    ),
    context=DecisionContext(
        problem_statement="How should CloudMetrics allocate its $3.5M growth budget over the next 12 months to accelerate towards $15M ARR while maintaining unit economics?",
        primary_objective="Maximize ARR growth over 12 months with sustainable CAC payback (< 14 months).",
        budget_limit="$3.5M",
        timeline="12 months (4 quarters)",
        hard_constraints=[
            "Cannot decrease cash runway below 10 months without new funding.",
            "All product features must remain SOC2 and GDPR compliant.",
        ],
    ),
    candidate_options=[
        StrategicOption(
            option_id="OPTION_A",
            name="Aggressive European Mid-Market Expansion",
            description="Establish an EU sales hub in London/Berlin, localize product for GDPR, and target 150 mid-market EU enterprise accounts.",
            intended_mechanism="Capture underserved EU mid-market with lower CAC and less aggressive competitor resistance.",
        ),
        StrategicOption(
            option_id="OPTION_B",
            name="US Upmarket Enterprise Push with AI Copilot Tier",
            description="Double down on US Fortune 500 accounts by launching a premium AI Observability Copilot module at $90k/yr ACV.",
            intended_mechanism="Expand expansion revenue from existing top-tier accounts and increase contract size to offset high US CAC.",
        ),
    ],
)

SAAS_SURPRISE_EVENT = SurpriseEvent(
    event_id="surprise_saas_001",
    title="Key Competitor DataWatch Slashes Enterprise Pricing by 40%",
    description="DataWatch announced an aggressive bundle slashing prices by 40% for multi-year enterprise contracts, directly impacting US sales conversion and lengthening pipeline cycles.",
    impacted_areas=[Department.FINANCE, Department.MARKETING],
    parameter_deltas={
        "us_sales_cycle_days": 110,
        "us_expected_cac": "$42,000",
        "eu_competitor_activity": "unchanged",
    },
)


# ==========================================
# Case 2: Direct-to-Consumer Logistics Dilemma
# ==========================================

D2C_LOGISTICS_CASE = InitialBusinessCase(
    case_id="case_d2c_002",
    facts=BusinessFacts(
        company_name="Lumina Health",
        industry="D2C Wellness & Smart Nutrition",
        financial_baseline={
            "annual_revenue": "$14.0M",
            "monthly_burn_rate": "$80,000",
            "cash_runway_months": 22,
            "product_gross_margin": "62%",
        },
        operational_metrics={
            "monthly_orders": 35000,
            "average_order_value": "$65",
            "fulfillment_cost_per_order": "$11.50 (via outsourced 3PL)",
            "average_delivery_days": 4.8,
            "order_return_rate": "4.2%",
        },
        market_facts=[
            "Customer reviews indicate 28% of negative feedback stems from delayed delivery (> 5 days).",
            "Next-day delivery expectation has risen from 15% to 45% of shoppers in the category.",
        ],
    ),
    context=DecisionContext(
        problem_statement="Should Lumina Health build its own automated regional fulfillment center or negotiate an upgraded SLA with a global 3PL partner?",
        primary_objective="Reduce per-order fulfillment cost to < $8.00 and delivery times to < 2.5 days.",
        budget_limit="$2.0M CapEx",
        timeline="9 months",
        hard_constraints=[
            "Fulfillment operations cannot be interrupted during peak holiday season (Q4).",
        ],
    ),
    candidate_options=[
        StrategicOption(
            option_id="OPTION_A",
            name="Build Dedicated Automated Micro-Fulfillment Center",
            description="Invest $1.8M CapEx into a leased regional automated facility in Ohio to control end-to-end packing and ship 80% of orders within 2 days at $6.80/order.",
            intended_mechanism="Direct ownership cuts variable cost per unit and improves brand experience.",
        ),
        StrategicOption(
            option_id="OPTION_B",
            name="Multi-Node Tier-1 3PL Network Transition",
            description="Migrate to a distributed 3-warehouse 3PL network with guaranteed 2-day ground shipping and $8.50/order cost with zero upfront CapEx.",
            intended_mechanism="Eliminate CapEx risk and operational overhead while immediately achieving multi-region 2-day delivery.",
        ),
    ],
)

D2C_SURPRISE_EVENT = SurpriseEvent(
    event_id="surprise_d2c_002",
    title="Commercial Warehouse Lease Rates Spike 35% in Target Region",
    description="Due to regional industrial zoning restrictions, lease costs for the proposed Ohio facility rose 35%, pushing upfront setup costs to $2.4M (exceeding CapEx limit).",
    impacted_areas=[Department.FINANCE],
    parameter_deltas={
        "facility_capex": "$2.4M",
        "capex_budget_breached": True,
    },
)
