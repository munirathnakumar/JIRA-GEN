# =============================================================================
# data.py  —  SSPM Slide Data  (manual mode)
# =============================================================================
# Edit this file when USE_JIRA = False in config.py.
# When USE_JIRA = True this file is IGNORED except for TIER_SUMMARY and MILESTONES.
#
# Slide map:
#   SUMMARY_STATS  → Slide 1  stat bar at top
#   TIER_TABLE     → Slide 1  top table    (by Priority tier:  P1–P5)
#   REGION_TABLE   → Slide 1  bottom table (by Region)
#   P1_APPS        → Slide 2  (P1 detailed rows, no blockers)
#   P2_APPS        → Slide 3  (P2 grid, no blockers)
#   TIER_SUMMARY   → Slide 4  (P3/P4/P5 out-of-scope + milestones)
#   MILESTONES     → Slide 4
#   P1_BLOCKERS    → Slide 5  (dedicated blockers slide)
#   S3_BLOCKERS    → Slide 5
#   P1_APPS        → Slide 6  (8-pane score improvement layout)
# =============================================================================


# =============================================================================
# SLIDE 1 — Summary Dashboard Data
# =============================================================================

# ── APP_SUMMARY: Unique application counts per tier ───────────────────────────
# One entry per tier.  "total_apps" = count of unique applications (= Stories).
# "done"    = apps where all instances are fully onboarded
# "pending" = apps still in progress or not started

APP_SUMMARY = [
    {"tier": "P1", "total_apps":  8, "done":  5, "pending": 3},
    {"tier": "P2", "total_apps": 14, "done":  8, "pending": 6},
    {"tier": "P3", "total_apps": 30, "done":  0, "pending": 30},
    {"tier": "P4", "total_apps": 20, "done":  0, "pending": 20},
    {"tier": "P5", "total_apps": 16, "done":  0, "pending": 16},
]

# ── INST_SUMMARY: Instance counts per tier ────────────────────────────────────
# One entry per tier.  Each instance = one Sub-task in the app's Story.
# "prod_done"  / "prod_pend"  / "prod_total"  : Production instances
# "np_done"    / "np_pend"    / "np_total"    : Non-Prod instances
#   Set np_total = 0 if no Non-Prod visibility yet (P3/P4/P5) → shows N/A

INST_SUMMARY = [
    {"tier": "P1", "prod_done": 8, "prod_pend": 3, "prod_total": 11,
                   "np_done":   3, "np_pend":   2, "np_total":    5},
    {"tier": "P2", "prod_done":12, "prod_pend": 8, "prod_total": 20,
                   "np_done":   4, "np_pend":   6, "np_total":   10},
    {"tier": "P3", "prod_done": 8, "prod_pend":22, "prod_total": 30,
                   "np_done":   0, "np_pend":   0, "np_total":    0},
    {"tier": "P4", "prod_done": 4, "prod_pend":16, "prod_total": 20,
                   "np_done":   0, "np_pend":   0, "np_total":    0},
    {"tier": "P5", "prod_done": 0, "prod_pend":15, "prod_total": 15,
                   "np_done":   0, "np_pend":   0, "np_total":    0},
]

# =============================================================================
# SLIDE 2 — Region-wise Summary
# =============================================================================
# Same instance structure as INST_SUMMARY but grouped by region.
# "prod_done" / "prod_pend" / "prod_total" : Prod instances in this region
# "np_done"   / "np_pend"  / "np_total"   : Non-Prod instances (0 = N/A)

REGION_TABLE = [
    {"region": "APAC",          "prod_done":10, "prod_pend": 8, "prod_total":18,
                                 "np_done":  3, "np_pend":  4,  "np_total":  7},
    {"region": "EMEA",          "prod_done": 7, "prod_pend": 6, "prod_total":13,
                                 "np_done":  2, "np_pend":  3,  "np_total":  5},
    {"region": "Global",        "prod_done": 5, "prod_pend": 3, "prod_total": 8,
                                 "np_done":  0, "np_pend":  0,  "np_total":  0},
    {"region": "Japan",         "prod_done": 3, "prod_pend": 2, "prod_total": 5,
                                 "np_done":  1, "np_pend":  1,  "np_total":  2},
    {"region": "North America", "prod_done": 4, "prod_pend": 5, "prod_total": 9,
                                 "np_done":  0, "np_pend":  3,  "np_total":  3},
    {"region": "TG",            "prod_done": 2, "prod_pend": 3, "prod_total": 5,
                                 "np_done":  0, "np_pend":  1,  "np_total":  1},
]

# =============================================================================
# Both tables share the SAME column structure:
#
#   Status columns (each with Prod + Non-Prod sub-columns):
#     Completed | Descoped | Future-Request | Not Started | In-Progress | Total
#
# Each cell is [Prod_count, NonProd_count].
# Use 0 where the count is zero. Use None where N/A (no NP environment).
#
# "Descoped"       = App was originally in scope, later removed
# "Future-Request" = App requested for future inclusion, not yet committed
# =============================================================================


# =============================================================================
# SLIDE 3  —  P1 Applications (detailed, per instance)
# =============================================================================
# One entry per app. Each instance: "env" = "Prod"|"Non-Prod", "done" = True|False

P1_APPS = [
    {"name": "A1", "instances": [
        {"env": "Prod",     "done": True },
        {"env": "Prod",     "done": True },
        {"env": "Prod",     "done": False},
        {"env": "Non-Prod", "done": True },
        {"env": "Non-Prod", "done": False},
    ]},
    {"name": "A2", "instances": [
        {"env": "Prod",     "done": True },
        {"env": "Non-Prod", "done": True },
    ]},
    {"name": "A3", "instances": [{"env": "Prod", "done": True }]},
    {"name": "A4", "instances": [
        {"env": "Prod",     "done": True },
        {"env": "Non-Prod", "done": False},
    ]},
    {"name": "A5", "instances": [{"env": "Prod", "done": True }]},
    {"name": "A6", "instances": [
        {"env": "Prod",     "done": True },
        {"env": "Non-Prod", "done": True },
    ]},
    {"name": "A7", "instances": [
        {"env": "Prod", "done": True },
        {"env": "Prod", "done": False},
    ]},
    {"name": "A8", "instances": [{"env": "Prod", "done": False}]},
]

P1_BLOCKERS = [
    {"id": "B1", "text": "A1 — Prod instance access provisioning pending IT approval",  "owner": "IT Ops",    "impact": "High"},
    {"id": "B2", "text": "A7 — Prod instance API unreachable, firewall change raised",  "owner": "Network",   "impact": "High"},
    {"id": "B3", "text": "A4 — Non-Prod tenant config not shared by app owner",         "owner": "App Owner", "impact": "Med" },
]


# =============================================================================
# SLIDE 3  —  P2 Applications (summary counts)
# =============================================================================

P2_APPS = [
    {"name": "A1",  "prod_done": 1, "prod_total": 1, "np_done": 0, "np_total": 1},
    {"name": "A2",  "prod_done": 1, "prod_total": 1, "np_done": 0, "np_total": 2},
    {"name": "A3",  "prod_done": 1, "prod_total": 1, "np_done": 1, "np_total": 1},
    {"name": "A4",  "prod_done": 1, "prod_total": 1, "np_done": 0, "np_total": 1},
    {"name": "A5",  "prod_done": 0, "prod_total": 1, "np_done": 0, "np_total": 1},
    {"name": "A6",  "prod_done": 0, "prod_total": 1, "np_done": 0, "np_total": 0},
    {"name": "A7",  "prod_done": 0, "prod_total": 1, "np_done": 0, "np_total": 1},
    {"name": "A8",  "prod_done": 0, "prod_total": 1, "np_done": 0, "np_total": 1},
    {"name": "A9",  "prod_done": 1, "prod_total": 1, "np_done": 0, "np_total": 1},
    {"name": "A10", "prod_done": 0, "prod_total": 1, "np_done": 0, "np_total": 0},
    {"name": "A11", "prod_done": 1, "prod_total": 1, "np_done": 0, "np_total": 1},
    {"name": "A12", "prod_done": 0, "prod_total": 1, "np_done": 0, "np_total": 0},
    {"name": "A13", "prod_done": 0, "prod_total": 1, "np_done": 0, "np_total": 0},
    {"name": "A14", "prod_done": 0, "prod_total": 1, "np_done": 0, "np_total": 0},
]


# =============================================================================
# SLIDE 4  —  Out-of-Scope Tiers, Milestones & Blockers
# =============================================================================

TIER_SUMMARY = [
    {"tier": "P3", "total": "~30", "prod_done": "8",  "prod_pending": "~22", "color": "purple"},
    {"tier": "P4", "total": "~20", "prod_done": "4",  "prod_pending": "~16", "color": "teal"  },
    {"tier": "P5", "total": "~15", "prod_done": "0",  "prod_pending": "~15", "color": "gray"  },
]

MILESTONES = [
    {
        "name": "Phase 2 · Auto-Ticketing Integration", "status": "In Progress", "color": "amber",
        "tasks": [
            {"task": "SSPM → ServiceNow connector design & build", "status": "In Progress"},
            {"task": "Ticket template, SLA & assignment routing",  "status": "Not Started"},
            {"task": "UAT, pilot & go-live",                       "status": "Not Started"},
        ],
    },
    {
        "name": "Phase 3 · Scorecard & Operationalisation", "status": "Not Started", "color": "purple",
        "tasks": [
            {"task": "Define KPIs, scoring framework & dashboard", "status": "Not Started"},
            {"task": "Runbook, SOP & SSPM operating model (BAU)",  "status": "Not Started"},
            {"task": "App owner reporting cadence & BAU handover", "status": "Not Started"},
        ],
    },
]

S3_BLOCKERS = [
    {"id": "B1", "text": "A1 (P1) — Prod instance access provisioning pending IT Ops approval", "owner": "IT Ops",    "impact": "High", "phase": "Phase 1"},
    {"id": "B2", "text": "A7 (P1) — Prod instance API unreachable, firewall change raised",     "owner": "Network",   "impact": "High", "phase": "Phase 1"},
    {"id": "B3", "text": "ServiceNow connector design blocked — ITSM team bandwidth",            "owner": "ITSM Team", "impact": "High", "phase": "Phase 2"},
    {"id": "B4", "text": "Scorecard KPI framework pending Security Architecture approval",       "owner": "Sec Arch",  "impact": "Med",  "phase": "Phase 3"},
]
