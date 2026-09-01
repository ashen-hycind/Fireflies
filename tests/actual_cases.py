"""
Official Competition Test Cases for Fireflies Multi-Agent Swarm.

Contains:
- Theme A: FINSWARM (FinNova Capital - Indian Digital Lending) - TC1 to TC5
- Theme B: SAASSWARM (OrbitFlow Software - B2B AI SaaS) - TC1 to TC5
- Theme C: CHIPSWARM (IndusCompute Hub - GPU Module Assembly) - TC1 to TC5
"""

from state.schemas import (
    InitialBusinessCase,
    BusinessFacts,
    DecisionContext,
    StrategicOption,
    SurpriseEvent,
    Department,
)

# ==============================================================================
# THEME A — FINSWARM (FinNova Capital)
# ==============================================================================

# TC1 — Baseline: Launch the Small-Business Loan
FINSWARM_TC1_CASE = InitialBusinessCase(
    case_id="FINSWARM_TC1",
    facts=BusinessFacts(
        company_name="FinNova Capital",
        industry="Indian Digital Lending (Registered MSME Lending)",
        financial_baseline={
            "available_pilot_capital": "INR 30 crore",
            "acquisition_budget": "INR 60 lakh",
            "product_setup_cost": "INR 18 lakh (deducted from acquisition budget, leaving INR 42 lakh for marketing)",
            "cost_of_funds": "10% per year",
            "servicing_and_collections_cost": "1.5% of principal per year",
            "liquidity_reserve_required": "At least INR 3 crore must remain undeployed",
        },
        operational_metrics={
            "max_initial_approved_loans": 700,
            "retail_shops_avg_loan": "INR 4 lakh",
            "retail_shops_expected_default": "5.0%",
            "retail_shops_available_demand": 1500,
            "retail_shops_cac": "INR 2,000 per customer",
            "service_smes_avg_loan": "INR 6 lakh",
            "service_smes_expected_default": "3.5%",
            "service_smes_available_demand": 900,
            "service_smes_cac": "INR 3,500 per customer",
            "small_manufacturers_avg_loan": "INR 9 lakh",
            "small_manufacturers_expected_default": "4.5%",
            "small_manufacturers_available_demand": 450,
            "small_manufacturers_cac": "INR 5,500 per customer",
        },
        market_facts=[
            "FinNova serves registered Indian small businesses.",
            "All values in Indian Rupees (INR).",
            "Product setup cost of INR 18 lakh is deducted upfront from the INR 60 lakh customer acquisition budget.",
        ],
    ),
    context=DecisionContext(
        problem_statement="Which customer segment mix, interest pricing, approval policy, and launch plan creates the strongest risk-adjusted business outcome?",
        primary_objective="Deploy capital within INR 27 crore deployed limit across high-quality MSME borrowers while maintaining expected default <= 5.0% and strong contribution margins.",
        budget_limit="INR 30 crore total capital (INR 27 crore max deployment, INR 3 crore liquidity reserve); INR 60 lakh acquisition budget (INR 42 lakh net marketing).",
        timeline="1 year pilot",
        hard_constraints=[
            "Expected portfolio default must remain at or below 5.0%.",
            "Average annual customer interest rate must not exceed 19.0%.",
            "No single segment may receive more than 70% of deployed capital.",
            "At least INR 3 crore must remain undeployed as a liquidity reserve.",
            "Total approved loans cannot exceed 700.",
        ],
    ),
    candidate_options=[
        StrategicOption(
            option_id="OPTION_A",
            name="Balanced Diversified Portfolio Mix",
            description="Allocate across Retail Shops (40%), Service SMEs (40%), and Small Manufacturers (20%) at 17.5% average interest.",
            intended_mechanism="Balances volume and lower CAC from Retail with the higher ticket size and lower default rate of Service SMEs.",
        ),
        StrategicOption(
            option_id="OPTION_B",
            name="Service-SME Focused Quality Portfolio",
            description="Allocate 65% capital to Service SMEs and 35% to Small Manufacturers/Retail at 16.5% interest with tighter underwriting.",
            intended_mechanism="Minimizes portfolio default (3.5%-4.5%) and maximizes risk-adjusted capital preservation.",
        ),
        StrategicOption(
            option_id="OPTION_C",
            name="High-Velocity Retail Aggressive Rollout",
            description="Allocate 60% to Retail Shops, 30% to Service SMEs, 10% to Small Manufacturers at 18.5% interest.",
            intended_mechanism="Maximizes interest spread and loan count volume (up to 700 loans) leveraging low INR 2,000 CAC.",
        ),
    ],
)

# TC2 — Surprise: Credit-Risk Spike
FINSWARM_TC2_SURPRISE = SurpriseEvent(
    event_id="FINSWARM_TC2_SURPRISE",
    title="Macro Credit-Risk Spike Across Small Business Segments",
    description="Retail-shop default increases to 8.0%, Service-SME default to 5.0%, and Small-manufacturer default to 7.0%. The risk committee strictly mandates portfolio default remain at or below 5.5%. Tighter approval rules reduce eligible demand by 25%. Pausing creates INR 12 lakh in sunk costs.",
    impacted_areas=[Department.FINANCE, Department.RESEARCH, Department.MARKETING],
    parameter_deltas={
        "retail_default_rate": "8.0%",
        "service_sme_default_rate": "5.0%",
        "small_mfg_default_rate": "7.0%",
        "mandated_portfolio_default_cap": "5.5%",
        "demand_reduction_from_tighter_rules": "25%",
        "sunk_cost_if_paused": "INR 12 lakh",
        "implementation_deadline": "30 days",
    },
)

# TC3 — Surprise: Marketing Budget Cut
FINSWARM_TC3_SURPRISE = SurpriseEvent(
    event_id="FINSWARM_TC3_SURPRISE",
    title="Customer Acquisition Budget Slashed from INR 60L to INR 36L",
    description="Customer acquisition budget reduced to INR 36 lakh (INR 18 lakh setup leaves only INR 18 lakh for marketing). Targets remain at least 400 qualified applications and 160 funded loans. Channel performance: Partner Accountants (INR 3,000/app, 45% conv), Digital Ads (INR 1,800/app, 25% conv), Trade Associations (INR 4,000/app, 60% conv), Referrals (INR 1,200/app, 40% conv, max 120 apps). Max 65% spend per channel.",
    impacted_areas=[Department.MARKETING, Department.FINANCE],
    parameter_deltas={
        "net_marketing_budget": "INR 18 lakh",
        "min_qualified_applications": 400,
        "min_funded_loans": 160,
        "max_single_channel_spend_pct": "65%",
        "max_launch_delay_allowed": "2 weeks",
    },
)

# TC4 — Surprise: Stricter Verification Requirements
FINSWARM_TC4_SURPRISE = SurpriseEvent(
    event_id="FINSWARM_TC4_SURPRISE",
    title="Regulatory Mandate: Enhanced Ownership and Bank-Statement Verification",
    description="Automated checks clear 60% of applications; 40% require manual review. Current review capacity is 8 reviewers x 4 reviews/day x 5 days/wk = 160 manual reviews/wk for 500 apps/wk (needs 200/wk). Three-month response budget: INR 15 lakh. Options: hire temporary reviewers (INR 45k/mo), integrate automated service (INR 8 lakh, 2 weeks), or appointment-based intake.",
    impacted_areas=[Department.RESEARCH, Department.FINANCE],
    parameter_deltas={
        "manual_review_share": "40%",
        "response_budget": "INR 15 lakh",
        "max_approval_time_hours": 48,
        "max_complaint_rate": "2.0%",
        "automated_integration_cost": "INR 8 lakh (2 weeks)",
    },
)

# TC5 — Live Test: Funding-Cost and Fraud Shock
FINSWARM_TC5_SURPRISE = SurpriseEvent(
    event_id="FINSWARM_TC5_SURPRISE",
    title="Funding Cost Surges to 13% and Retail Application Fraud Climbs to 7%",
    description="Cost of funds increases from 10% to 13%. Suspected retail application fraud jumps from 2% to 7%. Available control: fraud-screening service at INR 1,200/retail app reducing fraud by 60%. Price cap remains 19%. At least INR 3 crore must remain liquid and expected default <= 5.5%.",
    impacted_areas=[Department.FINANCE, Department.RESEARCH, Department.MARKETING],
    parameter_deltas={
        "cost_of_funds": "13.0%",
        "retail_fraud_rate": "7.0%",
        "fraud_screening_cost_per_app": "INR 1,200",
        "fraud_reduction_pct": "60%",
        "max_customer_pricing": "19.0%",
        "min_liquidity": "INR 3 crore",
        "max_portfolio_default": "5.5%",
    },
)


# ==============================================================================
# THEME B — SAASSWARM (OrbitFlow Software)
# ==============================================================================

# TC1 — Baseline: Choose the Product Market and MVP
SAASSWARM_TC1_CASE = InitialBusinessCase(
    case_id="SAASSWARM_TC1",
    facts=BusinessFacts(
        company_name="OrbitFlow Software",
        industry="B2B AI-Assisted Workflow Platform (Indian Enterprise SaaS)",
        financial_baseline={
            "available_capital": "INR 2.4 crore",
            "marketing_and_sales_budget": "INR 70 lakh",
            "arr_target_12m": "At least INR 60 lakh ARR within 12 months",
        },
        operational_metrics={
            "engineers_count": 12,
            "launch_timeline_months": 9,
            "total_pre_launch_capacity": "72 engineer-months",
            "core_platform_effort": "30 engineer-months",
            "remaining_segment_capacity": "42 engineer-months (allocated to ONE segment)",
            "small_retailers_effort": "18 engineer-months",
            "small_retailers_acv": "INR 1.2 lakh",
            "small_retailers_prospects": 220,
            "small_retailers_conversion": "12%",
            "mid_market_effort": "28 engineer-months",
            "mid_market_acv": "INR 4.5 lakh",
            "mid_market_prospects": 70,
            "mid_market_conversion": "20%",
            "large_enterprise_effort": "42 engineer-months",
            "large_enterprise_acv": "INR 15 lakh",
            "large_enterprise_prospects": 18,
            "large_enterprise_conversion": "28%",
        },
        market_facts=[
            "OrbitFlow Software builds an AI-assisted workflow platform.",
            "Core platform and admin system require 30 engineer-months.",
            "Remaining 42 engineer-months must be allocated to one customer segment for MVP.",
        ],
    ),
    context=DecisionContext(
        problem_statement="Which customer segment, MVP feature scope, pricing model, and go-to-market strategy should OrbitFlow select?",
        primary_objective="Achieve at least INR 60 lakh in annual recurring revenue (ARR) within 12 months with customer churn < 15%.",
        budget_limit="INR 2.4 crore total capital; INR 70 lakh for sales & marketing.",
        timeline="9 months to launch + 12 months ARR realization",
        hard_constraints=[
            "At least INR 60 lakh in ARR within 12 months.",
            "Annual customer churn below 15%.",
            "Discounts cannot exceed 20% of list price.",
            "Total segment feature development cannot exceed 42 engineer-months.",
        ],
    ),
    candidate_options=[
        StrategicOption(
            option_id="OPTION_A",
            name="Mid-Market Service Companies Focus (28 EM, INR 4.5L ACV)",
            description="Allocate 28 engineer-months to build workflow automation for 70 mid-market prospects at INR 4.5L ACV with 20% conversion (14 customers = INR 63L ARR).",
            intended_mechanism="Surpasses the INR 60L ARR target with 14 engineer-months of spare capacity for reliability and onboarding support.",
        ),
        StrategicOption(
            option_id="OPTION_B",
            name="Large Enterprise High-ACV Focus (42 EM, INR 15L ACV)",
            description="Use all 42 engineer-months to build deep enterprise controls targeting 18 large enterprises with 28% conversion (5 customers = INR 75L ARR).",
            intended_mechanism="Generates maximum revenue per contract, but utilizes 100% of engineering bandwidth leaving zero buffer for delays.",
        ),
        StrategicOption(
            option_id="OPTION_C",
            name="Small Retailers Volume Play (18 EM, INR 1.2L ACV)",
            description="Use 18 engineer-months for rapid retail workflow deployment targeting 220 prospects at 12% conversion (26 customers = INR 31.2L ARR + expansion).",
            intended_mechanism="Fastest to deploy and easiest to sell, but requires aggressive volume to hit the INR 60L threshold.",
        ),
    ],
)

# TC2 — Surprise: Competitor Price Cut
SAASSWARM_TC2_SURPRISE = SurpriseEvent(
    event_id="SAASSWARM_TC2_SURPRISE",
    title="Well-Funded Competitor Launches at INR 2.4L/yr (Price War)",
    description="A well-funded competitor launches at INR 2.4L/yr against OrbitFlow's planned INR 4.5L/yr price. Customer research reveals: 45% highly price-sensitive, 35% value implementation support, 20% prioritize data controls. OrbitFlow can fund either 6 engineer-months of new features OR 4 implementation specialists for 6 months.",
    impacted_areas=[Department.MARKETING, Department.FINANCE, Department.RESEARCH],
    parameter_deltas={
        "competitor_price": "INR 2.4 lakh/yr",
        "orbitflow_planned_price": "INR 4.5 lakh/yr",
        "price_sensitive_share": "45%",
        "implementation_support_share": "35%",
        "data_control_share": "20%",
        "max_launch_delay_allowed": "6 weeks (beyond reduces prospects by 20%)",
    },
)

# TC3 — Surprise: Enterprise Security Requirements
SAASSWARM_TC3_SURPRISE = SurpriseEvent(
    event_id="SAASSWARM_TC3_SURPRISE",
    title="Enterprise Pipeline Demands Stricter Security Controls (INR 54L ARR at stake)",
    description="Three enterprise prospects (INR 54L ARR) require: SSO (8 EM), RBAC (6 EM), Audit logs (5 EM), CMEK (10 EM), Security testing (INR 12 lakh, 4 wks). Available resources: 18 engineer-months, INR 15 lakh, max 6 weeks delay. Mid-market needs RBAC, enterprise needs audit logs.",
    impacted_areas=[Department.RESEARCH, Department.FINANCE],
    parameter_deltas={
        "pipeline_at_stake": "INR 54 lakh ARR",
        "available_engineering_months": 18,
        "available_budget": "INR 15 lakh",
        "max_launch_delay_weeks": 6,
    },
)

# TC4 — Surprise: Outages and Customer Churn
SAASSWARM_TC4_SURPRISE = SurpriseEvent(
    event_id="SAASSWARM_TC4_SURPRISE",
    title="Outages Spike Monthly Churn from 1% to 3% (40 Customers, INR 1.5Cr ARR)",
    description="Three incidents caused 6 hours downtime last month. Cancellation signals: 50% reliability, 30% slow support, 20% missing features. Available: 20 engineer-months next quarter, INR 12 lakh budget. Must reserve at least 4 EM for maintenance. Churn must fall below 1.5%.",
    impacted_areas=[Department.RESEARCH, Department.FINANCE, Department.MARKETING],
    parameter_deltas={
        "monthly_churn_rate": "3.0%",
        "target_churn_rate": "< 1.5%",
        "available_em": 20,
        "critical_maintenance_reserve_em": 4,
        "budget": "INR 12 lakh",
    },
)

# TC5 — Live Test: Strategic Customer Request
SAASSWARM_TC5_SURPRISE = SurpriseEvent(
    event_id="SAASSWARM_TC5_SURPRISE",
    title="Major Prospect Offers 2-Year Contract at INR 60L/yr for Private Deployment",
    description="Prospect offers INR 60L/yr 2-year deal for private deployment in 12 weeks. Delivery needs: 24 EM, INR 8 lakh infra, INR 6 lakh support specialist (6 mos), delays shared cloud roadmap by 8 weeks. Delayed roadmap puts 3 opportunities at risk (INR 45L value, 40% probability). 6 months runway, 8 engineers, INR 30 lakh budget.",
    impacted_areas=[Department.FINANCE, Department.RESEARCH, Department.MARKETING],
    parameter_deltas={
        "deal_value_annual": "INR 60 lakh/yr (2-year contract)",
        "delivery_window_weeks": 12,
        "engineering_effort_required": "24 engineer-months",
        "infrastructure_cost": "INR 8 lakh",
        "support_cost": "INR 6 lakh",
        "cloud_roadmap_delay_weeks": 8,
        "pipeline_at_risk": "INR 45 lakh (40% win rate)",
    },
)


# ==============================================================================
# THEME C — CHIPSWARM (IndusCompute Hub)
# ==============================================================================

# TC1 — Baseline: Allocate Production Capacity
CHIPSWARM_TC1_CASE = InitialBusinessCase(
    case_id="CHIPSWARM_TC1",
    facts=BusinessFacts(
        company_name="IndusCompute Hub",
        industry="Indian GPU Module Assembly, Advanced Packaging & Testing",
        financial_baseline={
            "ai_accelerator_margin": "INR 45,000 per unit",
            "gaming_gpu_margin": "INR 10,000 per unit",
            "edge_gpu_margin": "INR 18,000 per unit",
        },
        operational_metrics={
            "total_machine_hours_available": 24000,
            "ai_accelerator_hours_per_unit": 6,
            "ai_accelerator_max_demand": 2500,
            "ai_accelerator_fixed_commitment": 800,
            "gaming_gpu_hours_per_unit": 2,
            "gaming_gpu_max_demand": 6000,
            "gaming_gpu_fixed_commitment": 2000,
            "edge_gpu_hours_per_unit": 3,
            "edge_gpu_max_demand": 3500,
            "edge_gpu_fixed_commitment": 1000,
            "disruption_buffer_required_hours": 1200,
        },
        market_facts=[
            "IndusCompute Hub performs final assembly, advanced packaging, and testing for GPU modules.",
            "AI Accelerator: Rapidly growing data-centre demand.",
            "Gaming GPU: Stable repeat customer base.",
            "Edge GPU: Two long-term industrial contracts.",
        ],
    ),
    context=DecisionContext(
        problem_statement="How many units of each product should IndusCompute Hub manufacture next month to maximize contribution margin while honoring commitments and resilience buffers?",
        primary_objective="Maximize total contribution margin from the 24,000 machine-hour capacity while honoring all fixed commitments and maintaining buffer.",
        budget_limit="24,000 total machine-hours available",
        timeline="1 month production cycle",
        hard_constraints=[
            "No single product line may use more than 65% of total machine-hours (max 15,600 hours).",
            "At least 1,200 machine-hours must remain as a disruption buffer unless explicitly justified.",
            "Must meet minimum fixed commitments: >= 800 AI, >= 2,000 Gaming, >= 1,000 Edge.",
            "Production cannot exceed maximum demand for any product line.",
        ],
    ),
    candidate_options=[
        StrategicOption(
            option_id="OPTION_A",
            name="Max AI High-Margin Allocation (2,400 AI, 2,000 Gaming, 1,466 Edge)",
            description="Produce 2,400 AI modules (14,400 hrs), 2,000 Gaming GPUs (4,000 hrs), and 1,466 Edge GPUs (4,400 hrs), retaining 1,200 hrs buffer.",
            intended_mechanism="Prioritizes highest margin AI accelerators (INR 45k/unit = INR 7,500/hr) within the 65% line cap (14,400 < 15,600 hrs) to yield INR 15.4 crore contribution margin.",
        ),
        StrategicOption(
            option_id="OPTION_B",
            name="Balanced Commitment & Buffer Preservation Mix",
            description="Produce 1,800 AI modules (10,800 hrs), 3,500 Gaming GPUs (7,000 hrs), and 2,000 Edge GPUs (6,000 hrs), zero buffer reduction.",
            intended_mechanism="Maintains extensive relationships across gaming and industrial sectors while protecting delivery SLA reliability.",
        ),
    ],
)

# TC2 — Surprise: Critical Component Delay
CHIPSWARM_TC2_SURPRISE = SurpriseEvent(
    event_id="CHIPSWARM_TC2_SURPRISE",
    title="HBM Memory Supplier Delay Limits AI Production to 1,100 Units",
    description="HBM supplier delay caps AI modules at 1,100 units. Backup supplier offers 500 modules (INR 9,000 lower margin, INR 15 lakh qualification cost). Customer commitment is 1,500 AI units; shortfall costs INR 6,000/unit service credit. Unused machine-hours can be shifted to gaming (max 6k) or edge (max 3.5k). Buffer: 800 hrs.",
    impacted_areas=[Department.FINANCE, Department.RESEARCH, Department.MARKETING],
    parameter_deltas={
        "primary_ai_capacity_limit": 1100,
        "backup_supplier_ai_units": 500,
        "backup_margin_reduction": "INR 9,000/unit",
        "backup_qualification_cost": "INR 15 lakh",
        "customer_commitment_ai": 1500,
        "service_credit_per_shortfall_unit": "INR 6,000",
        "disruption_buffer_hours": 800,
    },
)

# TC3 — Surprise: AI Demand & Energy-Cost Surge
CHIPSWARM_TC3_SURPRISE = SurpriseEvent(
    event_id="CHIPSWARM_TC3_SURPRISE",
    title="AI Demand Jumps to 3,200 Units and Electricity Rates Rise 35%",
    description="Electricity costs rise 35%, cutting AI margins by INR 4,000, gaming by INR 1,000, edge by INR 1,500. Weekend shift adds up to 3,000 hours at INR 28 lakh fixed cost, but increases inspection workload by 20% and requires 600 regular hours for rework. No line > 70% total capacity.",
    impacted_areas=[Department.FINANCE, Department.RESEARCH],
    parameter_deltas={
        "ai_demand": 3200,
        "ai_margin_reduction": "INR 4,000/unit",
        "gaming_margin_reduction": "INR 1,000/unit",
        "edge_margin_reduction": "INR 1,500/unit",
        "weekend_shift_hours": 3000,
        "weekend_shift_fixed_cost": "INR 28 lakh",
        "rework_reservation_hours": 600,
    },
)

# TC4 — Surprise: Packaging-Yield Decline
CHIPSWARM_TC4_SURPRISE = SurpriseEvent(
    event_id="CHIPSWARM_TC4_SURPRISE",
    title="Packaging Line Yield Falls from 94% to 82% (Must Deliver >= 1,700 Units)",
    description="Final yield falls to 82%. Must deliver at least 1,700 saleable AI modules. Shortfall penalty: INR 8,000/unit. Options: Calibration shutdown (3 days, starts drop to 1,850, yield improves to 92%), Enhanced inspection (INR 3,000/started unit, yield 86%), Outsourcing (max 300 units, loses INR 12,000/unit margin).",
    impacted_areas=[Department.RESEARCH, Department.FINANCE],
    parameter_deltas={
        "current_yield": "82%",
        "min_required_saleable_units": 1700,
        "shortfall_penalty_per_unit": "INR 8,000",
        "calibration_yield": "92% (1,850 starts)",
        "inspection_cost_per_unit": "INR 3,000 (86% yield)",
        "outsourcing_max_units": 300,
        "outsourcing_margin_loss": "INR 12,000/unit",
    },
)

# TC5 — Live Test: Export-Restriction Reallocation
CHIPSWARM_TC5_SURPRISE = SurpriseEvent(
    event_id="CHIPSWARM_TC5_SURPRISE",
    title="Export Restriction Blocks 25% AI Modules and 30% Gaming Boards",
    description="Export restriction blocks 25% of AI modules (400 units) and 30% of gaming boards (1,200 units). Domestic market absorbs: 250 AI modules at full margin, 700 gaming boards at 80% margin. Storage costs: INR 2,000/AI unit/mo, INR 500/gaming unit/mo. Cash reserve covers max INR 18 lakh in storage/working-capital costs.",
    impacted_areas=[Department.FINANCE, Department.MARKETING, Department.RESEARCH],
    parameter_deltas={
        "blocked_ai_export_units": 400,
        "blocked_gaming_export_units": 1200,
        "domestic_ai_absorption": 250,
        "domestic_gaming_absorption": 700,
        "domestic_gaming_discount": "20%",
        "ai_storage_cost_per_month": "INR 2,000/unit",
        "gaming_storage_cost_per_month": "INR 500/unit",
        "max_storage_cash_reserve": "INR 18 lakh",
    },
)


# ==============================================================================
# Master Registry of Test Cases
# ==============================================================================

TEST_CASES_REGISTRY = {
    # Theme A: FinSwarm
    "FINSWARM_TC1": (FINSWARM_TC1_CASE, None),
    "FINSWARM_TC2": (FINSWARM_TC1_CASE, FINSWARM_TC2_SURPRISE),
    "FINSWARM_TC3": (FINSWARM_TC1_CASE, FINSWARM_TC3_SURPRISE),
    "FINSWARM_TC4": (FINSWARM_TC1_CASE, FINSWARM_TC4_SURPRISE),
    "FINSWARM_TC5": (FINSWARM_TC1_CASE, FINSWARM_TC5_SURPRISE),
    # Theme B: SaaS Swarm
    "SAASSWARM_TC1": (SAASSWARM_TC1_CASE, None),
    "SAASSWARM_TC2": (SAASSWARM_TC1_CASE, SAASSWARM_TC2_SURPRISE),
    "SAASSWARM_TC3": (SAASSWARM_TC1_CASE, SAASSWARM_TC3_SURPRISE),
    "SAASSWARM_TC4": (SAASSWARM_TC1_CASE, SAASSWARM_TC4_SURPRISE),
    "SAASSWARM_TC5": (SAASSWARM_TC1_CASE, SAASSWARM_TC5_SURPRISE),
    # Theme C: ChipSwarm
    "CHIPSWARM_TC1": (CHIPSWARM_TC1_CASE, None),
    "CHIPSWARM_TC2": (CHIPSWARM_TC1_CASE, CHIPSWARM_TC2_SURPRISE),
    "CHIPSWARM_TC3": (CHIPSWARM_TC1_CASE, CHIPSWARM_TC3_SURPRISE),
    "CHIPSWARM_TC4": (CHIPSWARM_TC1_CASE, CHIPSWARM_TC4_SURPRISE),
    "CHIPSWARM_TC5": (CHIPSWARM_TC1_CASE, CHIPSWARM_TC5_SURPRISE),
}
