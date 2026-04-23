# =============================================================================
# data.py  —  Manual / fallback data  (used when USE_JIRA = False)
# =============================================================================
# STATUS values must match one of the keys in config.STATUS_MAPPING:
#   "completed"      → maps from "Completed" JIRA dropdown
#   "de_scoped"      → maps from "De-Scoped"
#   "future_request" → maps from "Future Request"
#   "not_started"    → maps from "Not Started"
#   "in_progress"    → maps from "Onboarding In Progress"
# =============================================================================

# =============================================================================
# APPLICATIONS  (Phase 1 + Phase 2)
# =============================================================================
# Mock data:  18 Phase-1 apps  → 2 detail slides (14 + 4 rows)
#             32 Phase-2 apps  → 3 detail slides (14 + 14 + 4 rows)
# All 5 statuses represented across the dataset.

def _inst(key, summary, phase, status, region, pd, pt, nd, nt,
          app_id="—", instance_name=None):
    # Derive simple subtask rows for the Appendix from prod/np counts
    subtasks = []
    for i in range(pt):
        subtasks.append({"key": f"{key}-P{i+1}", "name": f"{summary} Prod {i+1}",
                         "env": "Prod", "status": "Done" if i < pd else "Not Started",
                         "done": i < pd})
    for i in range(nt):
        subtasks.append({"key": f"{key}-NP{i+1}", "name": f"{summary} Non-Prod {i+1}",
                         "env": "Non-Prod", "status": "Done" if i < nd else "Not Started",
                         "done": i < nd})
    return {"key": key, "summary": summary,
            "instance_name": instance_name or summary,
            "app_id": app_id,
            "phase": phase, "status": status, "region": region,
            "prod_done": pd, "prod_total": pt,
            "non_prod_done": nd, "non_prod_total": nt,
            "subtasks": subtasks}

APPLICATIONS = [

    # ── PHASE 1 ── 18 applications ───────────────────────────────────────────

    {"name": "Salesforce", "instances": [
        _inst("SSPM-101","Salesforce - APAC Prod",   "Phase 1","completed",      "APAC",          1,1,1,1),
        _inst("SSPM-102","Salesforce - APAC DR",     "Phase 1","completed",      "APAC",          1,1,0,1),
        _inst("SSPM-103","Salesforce - EMEA Prod",   "Phase 1","in_progress",    "EMEA",          0,1,0,1),
        _inst("SSPM-104","Salesforce - Japan Prod",  "Phase 1","completed",      "Japan",         1,1,1,1),
        _inst("SSPM-105","Salesforce - NA Prod",     "Phase 1","in_progress",    "North America", 1,1,0,1),
        _inst("SSPM-106","Salesforce - NA Sandbox",  "Phase 1","not_started",    "North America", 0,1,0,1),
        _inst("SSPM-107","Salesforce - Global Prod", "Phase 1","completed",      "Global",        1,1,0,0),
        _inst("SSPM-108","Salesforce - TG Prod",     "Phase 1","de_scoped",      "TG",            0,1,0,0),
    ]},
    {"name": "Workday", "instances": [
        _inst("SSPM-201","Workday - APAC Prod",      "Phase 1","completed",      "APAC",          1,1,1,1),
        _inst("SSPM-202","Workday - EMEA Prod",      "Phase 1","completed",      "EMEA",          1,1,0,1),
        _inst("SSPM-203","Workday - NA Prod",        "Phase 1","in_progress",    "North America", 0,1,0,1),
    ]},
    {"name": "ServiceNow", "instances": [
        _inst("SSPM-301","ServiceNow - APAC Prod",   "Phase 1","completed",      "APAC",          1,1,1,1),
        _inst("SSPM-302","ServiceNow - EMEA Prod",   "Phase 1","in_progress",    "EMEA",          1,1,0,1),
        _inst("SSPM-303","ServiceNow - NA Prod",     "Phase 1","in_progress",    "North America", 0,1,0,1),
        _inst("SSPM-304","ServiceNow - Japan Prod",  "Phase 1","completed",      "Japan",         1,1,0,0),
    ]},
    {"name": "GitHub Enterprise", "instances": [
        _inst("SSPM-401","GitHub Ent - APAC",        "Phase 1","completed",      "APAC",          1,1,1,1),
        _inst("SSPM-402","GitHub Ent - EMEA",        "Phase 1","completed",      "EMEA",          1,1,1,1),
        _inst("SSPM-403","GitHub Ent - NA",          "Phase 1","not_started",    "North America", 0,1,0,1),
    ]},
    {"name": "Microsoft 365", "instances": [
        _inst("SSPM-501","M365 - APAC Prod",         "Phase 1","completed",      "APAC",          1,1,0,0),
        _inst("SSPM-502","M365 - EMEA Prod",         "Phase 1","completed",      "EMEA",          1,1,0,0),
        _inst("SSPM-503","M365 - Japan Prod",        "Phase 1","completed",      "Japan",         1,1,0,0),
        _inst("SSPM-504","M365 - NA Prod",           "Phase 1","in_progress",    "North America", 0,1,0,0),
        _inst("SSPM-505","M365 - Global Prod",       "Phase 1","not_started",    "Global",        0,1,0,0),
    ]},
    {"name": "Okta", "instances": [
        _inst("SSPM-601","Okta - APAC Prod",         "Phase 1","completed",      "APAC",          1,1,1,1),
        _inst("SSPM-602","Okta - NA Prod",           "Phase 1","completed",      "North America", 1,1,1,1),
        _inst("SSPM-603","Okta - EMEA Prod",         "Phase 1","in_progress",    "EMEA",          0,1,0,1),
    ]},
    {"name": "Zoom", "instances": [
        _inst("SSPM-701","Zoom - Global Prod",       "Phase 1","completed",      "Global",        1,1,0,1),
        _inst("SSPM-702","Zoom - Japan Prod",        "Phase 1","not_started",    "Japan",         0,1,0,0),
    ]},
    {"name": "Slack", "instances": [
        _inst("SSPM-801","Slack - Global Prod",      "Phase 1","completed",      "Global",        1,1,0,0),
        _inst("SSPM-802","Slack - APAC Prod",        "Phase 1","in_progress",    "APAC",          0,1,0,1),
    ]},
    {"name": "Palo Alto Prisma", "instances": [
        _inst("SSPM-901","Prisma - APAC Prod",       "Phase 1","completed",      "APAC",          1,1,1,1),
        _inst("SSPM-902","Prisma - NA Prod",         "Phase 1","completed",      "North America", 1,1,0,1),
    ]},
    {"name": "CrowdStrike", "instances": [
        _inst("SSPM-1001","CrowdStrike - Global",    "Phase 1","in_progress",    "Global",        1,1,0,1),
    ]},
    {"name": "Proofpoint", "instances": [
        _inst("SSPM-1101","Proofpoint - APAC",       "Phase 1","completed",      "APAC",          1,1,0,0),
        _inst("SSPM-1102","Proofpoint - EMEA",       "Phase 1","completed",      "EMEA",          1,1,0,0),
        _inst("SSPM-1103","Proofpoint - NA",         "Phase 1","de_scoped",      "North America", 0,1,0,0),
    ]},
    {"name": "Mimecast", "instances": [
        _inst("SSPM-1201","Mimecast - APAC Prod",    "Phase 1","in_progress",    "APAC",          0,1,0,1),
        _inst("SSPM-1202","Mimecast - EMEA Prod",    "Phase 1","not_started",    "EMEA",          0,1,0,1),
    ]},
    {"name": "Qualys", "instances": [
        _inst("SSPM-1301","Qualys - Global Prod",    "Phase 1","completed",      "Global",        1,1,0,0),
    ]},
    {"name": "Rapid7", "instances": [
        _inst("SSPM-1401","Rapid7 - APAC Prod",      "Phase 1","not_started",    "APAC",          0,1,0,0),
        _inst("SSPM-1402","Rapid7 - NA Prod",        "Phase 1","not_started",    "North America", 0,1,0,0),
    ]},
    {"name": "Tenable", "instances": [
        _inst("SSPM-1501","Tenable - APAC",          "Phase 1","future_request", "APAC",          0,1,0,0),
    ]},
    {"name": "Varonis", "instances": [
        _inst("SSPM-1601","Varonis - NA Prod",       "Phase 1","de_scoped",      "North America", 0,1,0,0),
    ]},
    {"name": "SailPoint", "instances": [
        _inst("SSPM-1701","SailPoint - APAC",        "Phase 1","future_request", "APAC",          0,1,0,1),
        _inst("SSPM-1702","SailPoint - EMEA",        "Phase 1","not_started",    "EMEA",          0,1,0,1),
    ]},
    {"name": "BeyondTrust", "instances": [
        _inst("SSPM-1801","BeyondTrust - Global",    "Phase 1","not_started",    "Global",        0,1,0,0),
    ]},

    # ── PHASE 2 ── 32 applications ───────────────────────────────────────────

    {"name": "Box", "instances": [
        _inst("SSPM-2001","Box - APAC Prod",         "Phase 2","in_progress",    "APAC",          1,1,0,1),
        _inst("SSPM-2002","Box - EMEA Prod",         "Phase 2","not_started",    "EMEA",          0,1,0,1),
        _inst("SSPM-2003","Box - NA Prod",           "Phase 2","not_started",    "North America", 0,1,0,1),
    ]},
    {"name": "Dropbox", "instances": [
        _inst("SSPM-2101","Dropbox - APAC Prod",     "Phase 2","not_started",    "APAC",          0,1,0,0),
        _inst("SSPM-2102","Dropbox - NA Prod",       "Phase 2","not_started",    "North America", 0,1,0,0),
    ]},
    {"name": "Atlassian (Jira/Confluence)", "instances": [
        _inst("SSPM-2201","Atlassian - APAC Prod",   "Phase 2","in_progress",    "APAC",          1,1,0,1),
        _inst("SSPM-2202","Atlassian - EMEA Prod",   "Phase 2","not_started",    "EMEA",          0,1,0,1),
        _inst("SSPM-2203","Atlassian - NA Prod",     "Phase 2","not_started",    "North America", 0,1,0,1),
    ]},
    {"name": "Zendesk", "instances": [
        _inst("SSPM-2301","Zendesk - APAC Prod",     "Phase 2","not_started",    "APAC",          0,1,0,1),
        _inst("SSPM-2302","Zendesk - Global Prod",   "Phase 2","not_started",    "Global",        0,1,0,0),
    ]},
    {"name": "DocuSign", "instances": [
        _inst("SSPM-2401","DocuSign - APAC Prod",    "Phase 2","in_progress",    "APAC",          1,1,0,1),
        _inst("SSPM-2402","DocuSign - NA Prod",      "Phase 2","not_started",    "North America", 0,1,0,1),
    ]},
    {"name": "HubSpot", "instances": [
        _inst("SSPM-2501","HubSpot - APAC Prod",     "Phase 2","not_started",    "APAC",          0,1,0,1),
        _inst("SSPM-2502","HubSpot - NA Prod",       "Phase 2","not_started",    "North America", 0,1,0,0),
    ]},
    {"name": "Tableau / Salesforce Analytics", "instances": [
        _inst("SSPM-2601","Tableau - APAC Prod",     "Phase 2","in_progress",    "APAC",          1,1,0,1),
        _inst("SSPM-2602","Tableau - EMEA Prod",     "Phase 2","not_started",    "EMEA",          0,1,0,1),
        _inst("SSPM-2603","Tableau - NA Prod",       "Phase 2","not_started",    "North America", 0,1,0,0),
    ]},
    {"name": "Coupa", "instances": [
        _inst("SSPM-2701","Coupa - APAC Prod",       "Phase 2","not_started",    "APAC",          0,1,0,1),
        _inst("SSPM-2702","Coupa - NA Prod",         "Phase 2","de_scoped",      "North America", 0,1,0,0),
    ]},
    {"name": "Snowflake", "instances": [
        _inst("SSPM-2801","Snowflake - APAC Prod",   "Phase 2","not_started",    "APAC",          0,1,0,1),
        _inst("SSPM-2802","Snowflake - NA Prod",     "Phase 2","not_started",    "North America", 0,1,0,1),
    ]},
    {"name": "Splunk", "instances": [
        _inst("SSPM-2901","Splunk - Global Prod",    "Phase 2","in_progress",    "Global",        1,1,0,1),
    ]},
    {"name": "Ariba / SAP", "instances": [
        _inst("SSPM-3001","Ariba - APAC Prod",       "Phase 2","not_started",    "APAC",          0,1,0,1),
        _inst("SSPM-3002","Ariba - EMEA Prod",       "Phase 2","not_started",    "EMEA",          0,1,0,1),
    ]},
    {"name": "Veeva Vault", "instances": [
        _inst("SSPM-3101","Veeva - APAC Prod",       "Phase 2","future_request", "APAC",          0,1,0,0),
        _inst("SSPM-3102","Veeva - NA Prod",         "Phase 2","future_request", "North America", 0,1,0,0),
    ]},
    {"name": "Workiva", "instances": [
        _inst("SSPM-3201","Workiva - Global Prod",   "Phase 2","not_started",    "Global",        0,1,0,0),
    ]},
    {"name": "NetSuite", "instances": [
        _inst("SSPM-3301","NetSuite - APAC Prod",    "Phase 2","not_started",    "APAC",          0,1,0,0),
        _inst("SSPM-3302","NetSuite - NA Prod",      "Phase 2","not_started",    "North America", 0,1,0,0),
    ]},
    {"name": "Anaplan", "instances": [
        _inst("SSPM-3401","Anaplan - APAC Prod",     "Phase 2","future_request", "APAC",          0,1,0,0),
    ]},
    {"name": "Concur (SAP)", "instances": [
        _inst("SSPM-3501","Concur - Global Prod",    "Phase 2","not_started",    "Global",        0,1,0,0),
    ]},
    {"name": "Adobe Sign", "instances": [
        _inst("SSPM-3601","Adobe Sign - APAC",       "Phase 2","not_started",    "APAC",          0,1,0,1),
        _inst("SSPM-3602","Adobe Sign - NA",         "Phase 2","not_started",    "North America", 0,1,0,1),
    ]},
    {"name": "SuccessFactors", "instances": [
        _inst("SSPM-3701","SuccessFactors - APAC",   "Phase 2","not_started",    "APAC",          0,1,0,0),
        _inst("SSPM-3702","SuccessFactors - EMEA",   "Phase 2","not_started",    "EMEA",          0,1,0,0),
    ]},
    {"name": "Darktrace", "instances": [
        _inst("SSPM-3801","Darktrace - APAC Prod",   "Phase 2","in_progress",    "APAC",          1,1,0,1),
    ]},
    {"name": "Elastic (ELK)", "instances": [
        _inst("SSPM-3901","Elastic - Global Prod",   "Phase 2","not_started",    "Global",        0,1,0,1),
    ]},
    {"name": "PagerDuty", "instances": [
        _inst("SSPM-4001","PagerDuty - Global",      "Phase 2","future_request", "Global",        0,1,0,0),
    ]},
    {"name": "Dynatrace", "instances": [
        _inst("SSPM-4101","Dynatrace - APAC Prod",   "Phase 2","not_started",    "APAC",          0,1,0,1),
        _inst("SSPM-4102","Dynatrace - NA Prod",     "Phase 2","not_started",    "North America", 0,1,0,1),
    ]},
    {"name": "Miro", "instances": [
        _inst("SSPM-4201","Miro - Global Prod",      "Phase 2","de_scoped",      "Global",        0,1,0,0),
    ]},
    {"name": "Figma", "instances": [
        _inst("SSPM-4301","Figma - Global Prod",     "Phase 2","not_started",    "Global",        0,1,0,0),
    ]},
    {"name": "Notion", "instances": [
        _inst("SSPM-4401","Notion - Global Prod",    "Phase 2","future_request", "Global",        0,1,0,0),
    ]},
    {"name": "monday.com", "instances": [
        _inst("SSPM-4501","monday.com - APAC",       "Phase 2","not_started",    "APAC",          0,1,0,0),
    ]},
    {"name": "Asana", "instances": [
        _inst("SSPM-4601","Asana - Global Prod",     "Phase 2","not_started",    "Global",        0,1,0,0),
    ]},
    {"name": "Jira Service Mgmt", "instances": [
        _inst("SSPM-4701","JSM - APAC Prod",         "Phase 2","in_progress",    "APAC",          1,1,0,1),
        _inst("SSPM-4702","JSM - NA Prod",           "Phase 2","not_started",    "North America", 0,1,0,1),
    ]},
    {"name": "Freshdesk", "instances": [
        _inst("SSPM-4801","Freshdesk - APAC Prod",   "Phase 2","not_started",    "APAC",          0,1,0,0),
    ]},
    {"name": "Intercom", "instances": [
        _inst("SSPM-4901","Intercom - Global",       "Phase 2","future_request", "Global",        0,1,0,0),
    ]},
    {"name": "Twilio", "instances": [
        _inst("SSPM-5001","Twilio - APAC Prod",      "Phase 2","not_started",    "APAC",          0,1,0,0),
        _inst("SSPM-5002","Twilio - NA Prod",        "Phase 2","not_started",    "North America", 0,1,0,0),
    ]},
    {"name": "SendGrid", "instances": [
        _inst("SSPM-5101","SendGrid - Global",       "Phase 2","de_scoped",      "Global",        0,1,0,0),
    ]},
]


# =============================================================================
# =============================================================================
# SLIDE3_APPLICATIONS  (sub-task based — used for Slide 3 detail rows)
# In manual mode this mirrors APPLICATIONS. In JIRA mode it is built
# separately from JQL_SUBTASKS using SLIDE3_APP_FIELD.
# =============================================================================

SLIDE3_APPLICATIONS = APPLICATIONS   # same mock data; JIRA mode uses a separate build


# =============================================================================
# APPENDIX_ROWS  (flat list from sub-tasks — one row per sub-task)
# Derived here from the subtasks list embedded in each instance.
# In JIRA mode these come directly from JQL_SUBTASKS via APPENDIX_APP_FIELD.
# =============================================================================

def _build_appendix_rows():
    rows = []
    for app in APPLICATIONS:
        for inst in app["instances"]:
            for st in inst.get("subtasks", []):
                rows.append({
                    "app_name" : app["name"],
                    "inst_name": inst.get("instance_name") or inst.get("summary", ""),
                    "app_id"   : inst.get("app_id", "—"),
                    "phase"    : inst.get("phase", ""),
                    "env"      : st["env"],
                    "sub_key"  : st["key"],
                    "sub_name" : st["name"],
                    "status"   : "completed" if st["done"] else "not_started",
                })
    return rows

APPENDIX_ROWS = _build_appendix_rows()


# =============================================================================
# PHASE SUMMARY  (out-of-scope phases — summary row only, no detail slides)
# =============================================================================

PHASE_SUMMARY = {
    "Phase 3": {"total_apps": 143, "prod_done": 12, "prod_total": 143, "np_done": 0, "np_total": 0, "in_scope": False},
    "Phase 4": {"total_apps": 198, "prod_done":  4, "prod_total": 198, "np_done": 0, "np_total": 0, "in_scope": False},
    "Phase 5": {"total_apps": 182, "prod_done":  0, "prod_total": 182, "np_done": 0, "np_total": 0, "in_scope": False},
}


# =============================================================================
# BLOCKERS
# =============================================================================

BLOCKERS = [
    {"id": "B1", "key": "SSPM-9001", "text": "Salesforce EMEA — Prod tenant access pending IT Ops approval",       "owner": "IT Ops",    "impact": "High", "phase": "Phase 1"},
    {"id": "B2", "key": "SSPM-9002", "text": "ServiceNow NA — API endpoint unreachable, firewall change raised",    "owner": "Network",   "impact": "High", "phase": "Phase 1"},
    {"id": "B3", "key": "SSPM-9003", "text": "Workday NA — Non-Prod tenant config not shared by app owner",         "owner": "App Owner", "impact": "Med",  "phase": "Phase 1"},
    {"id": "B4", "key": "SSPM-9004", "text": "Box EMEA — Licence procurement approval pending Finance sign-off",    "owner": "Finance",   "impact": "Med",  "phase": "Phase 2"},
    {"id": "B5", "key": "SSPM-9005", "text": "Atlassian — Prod API key rotation blocking SSPM connector config",    "owner": "Platform",  "impact": "High", "phase": "Phase 2"},
]


# =============================================================================
# MILESTONES
# =============================================================================

MILESTONES = [
    {
        "name"  : "Phase 2 · Auto-Ticketing Integration",
        "status": "in_progress",
        "phase" : "Phase 2",
        "tasks" : [
            {"task": "SSPM → ServiceNow connector: requirements & design",  "status": "completed"},
            {"task": "Connector build — Phase 1 apps (P1 scope)",            "status": "completed"},
            {"task": "Connector build — Phase 2 apps (P2 scope)",            "status": "in_progress"},
            {"task": "Ticket template design (fields, SLA, priority rules)", "status": "in_progress"},
            {"task": "Assignment routing rules & escalation matrix",          "status": "not_started"},
            {"task": "UAT — internal SSPM team validation",                  "status": "not_started"},
            {"task": "UAT — app owner pilot (10 apps)",                      "status": "not_started"},
            {"task": "Runbook: auto-ticket lifecycle SOP",                   "status": "not_started"},
            {"task": "Load & performance testing",                           "status": "not_started"},
            {"task": "Go-live & hypercare (2-week window)",                  "status": "not_started"},
        ],
    },
    {
        "name"  : "Phase 3 · Scorecard & Operationalisation",
        "status": "not_started",
        "phase" : "Phase 3",
        "tasks" : [
            {"task": "Define KPIs and scoring framework",                    "status": "not_started"},
            {"task": "Build SSPM health dashboard (Power BI / Tableau)",     "status": "not_started"},
            {"task": "App owner reporting template & cadence",               "status": "not_started"},
            {"task": "Runbook & SOP documentation",                         "status": "not_started"},
            {"task": "SSPM operating model (BAU) sign-off",                 "status": "not_started"},
            {"task": "BAU handover to operations team",                     "status": "not_started"},
            {"task": "Post-go-live review & lessons learned",               "status": "not_started"},
            {"task": "Hypercare exit criteria & sign-off",                  "status": "not_started"},
        ],
    },
    {
        "name"  : "Phase 4 · Continuous Improvement & Expansion",
        "status": "not_started",
        "phase" : "Phase 4",
        "tasks" : [
            {"task": "Review Phase 3/4 app onboarding backlog",             "status": "not_started"},
            {"task": "Automated risk-scoring model v2",                     "status": "not_started"},
            {"task": "Integration with PAM / IAM tooling",                  "status": "not_started"},
            {"task": "Expanded SSPM coverage: Phase 4 apps (198 apps)",     "status": "not_started"},
            {"task": "Quarterly review cadence with steering committee",    "status": "not_started"},
            {"task": "Audit & compliance reporting package",                "status": "not_started"},
        ],
    },
]
