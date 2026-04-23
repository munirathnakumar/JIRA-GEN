# =============================================================================
# config.py  —  SSPM PPT Generator Settings  (re-wired architecture)
# =============================================================================
# THE ONLY FILE YOU NEED TO EDIT.
#
# FIELD KEYS vs. DISPLAY NAMES — THE GOLDEN RULE
# ================================================
# JIRA API uses FIELD KEYS (no spaces):  customfield_10042, status, priority
# JIRA UI shows DISPLAY NAMES (may have spaces): "Prod Done", "Epic Link"
# → Always use the FIELD KEY here, never the display name.
# → Run: python find_jira_fields.py <ISSUE-KEY>  to discover field keys.
#
# FIELD VALUES (dropdown text, label text) CAN have spaces — that's fine.
# e.g. "In Progress", "North America", "Phase 1" are all valid values.
#
# JQL FIELD NAMES with spaces must be double-quoted inside the JQL string:
# e.g.  "Epic Link" = SSPM-10    (quoted inside the JQL)
# =============================================================================


# -----------------------------------------------------------------------------
# 1. OUTPUT
# -----------------------------------------------------------------------------

OUTPUT_FILE = "SSPM_Status.pptx"


# -----------------------------------------------------------------------------
# 2. JIRA CONNECTION
# -----------------------------------------------------------------------------
# USE_JIRA = False  →  use data.py (manual, offline)
# USE_JIRA = True   →  call JIRA REST API live
#
# API token: https://id.atlassian.com → Security → API tokens → Create
# -----------------------------------------------------------------------------

USE_JIRA       = False
JIRA_BASE_URL  = "https://yourcompany.atlassian.net"   # no trailing slash
JIRA_EMAIL     = "you@yourcompany.com"
JIRA_API_TOKEN = "YOUR_API_TOKEN_HERE"


# =============================================================================
# 3. TWO PRIMARY JQL QUERIES
# =============================================================================
#
# JQL MAY CONTAIN SPACES — that is intentional.
# JIRA field names with spaces must be wrapped in double quotes inside the JQL:
#   "Epic Link" = SSPM-10        → ✅ field name "Epic Link" quoted
#   project = "MY PROJECT"       → ✅ project name with space quoted
#   issuetype = "Story"          → ✅ value quotes are optional but safe
#
# JQL 1 — APPLICATION STORIES
# ----------------------------
# One Story = one SaaS instance of an application.
# All stories for the same application (same Epic / same label / same field)
# represent that application's full instance footprint.
#
# Example — Salesforce has 8 stories → Salesforce has 8 instances.
#
# You can use any valid JQL here. Examples:
#   'project = "SSPM" AND issuetype = Story ORDER BY created ASC'
#   '"Epic Link" in (SSPM-10, SSPM-11) ORDER BY key ASC'
#   'project = SSPM AND labels = "Phase1" ORDER BY priority ASC'
#
JQL_STORIES = 'project = "SSPM" AND issuetype = Story ORDER BY created ASC'

# JQL 2 — SUB-TASKS (PROD vs NON-PROD INSTANCES)
# -----------------------------------------------
# Each Sub-task under a Story identifies one Prod or Non-Prod environment.
# The sub-task's parent field links it back to its Story (= instance).
#
# Examples:
#   'project = "SSPM" AND issuetype = Sub-task ORDER BY created ASC'
#   'project = SSPM AND issuetype in subTaskIssueTypes() ORDER BY key ASC'
#
# If your project does NOT use sub-tasks for Prod/Non-Prod, set this to ""
# and configure INSTANCE_COUNT_FIELDS below instead.
#
JQL_SUBTASKS = 'project = "SSPM" AND issuetype = Sub-task ORDER BY created ASC'


# =============================================================================
# 4. APPLICATION GROUPING
# =============================================================================
# How to determine which "application" a Story belongs to.
# All stories that resolve to the same application name are grouped together.
#
# Options:
#   "epic_name"      → use the Story's Epic name (recommended for epic-organised boards)
#   "custom_field"   → use a custom field value on the Story
#   "label"          → use the first label on the Story that matches an application name
#   "component"      → use the first JIRA Component on the Story
#   "summary_prefix" → extract app name from Story summary using a separator
#                      (e.g. "Salesforce - APAC Prod" → "Salesforce")
#
APPLICATION_GROUPING = "epic_name"

# Used only when APPLICATION_GROUPING = "custom_field"
# Paste the FIELD KEY (no spaces) from find_jira_fields.py
APPLICATION_FIELD = "customfield_XXXXX"

# Used only when APPLICATION_GROUPING = "summary_prefix"
# The separator that splits app name from instance detail in the summary
# e.g. "Salesforce - APAC Prod" uses separator " - "
APPLICATION_SUMMARY_SEPARATOR = " - "


# =============================================================================
# 5. PHASE IDENTIFICATION  (5 phases)
# =============================================================================
# A JIRA field on each Story identifies which of the 5 phases it belongs to.
# Use find_jira_fields.py to locate the field key.
#
PHASE_FIELD = "customfield_XXXXX"   # field KEY, no spaces

# Exact dropdown values in JIRA for each phase (spaces in values are fine)
PHASE_VALUES = ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5"]


# =============================================================================
# 6. PROJECT STATUS  (completed / in-progress / backlog / de-scoped)
# =============================================================================
# The JIRA field that holds the integration project status for each Story.
# Use "status" for the built-in JIRA status field, or a custom field key.
#
STATUS_FIELD = "status"    # "status"  OR  "customfield_XXXXX"

# Map JIRA field values → one of the 4 standard statuses used in the PPT.
# Add or edit the JIRA values to match your project's exact status names.
# The mapping is case-insensitive.
STATUS_MAPPING = {
    "completed":  ["Done", "Completed", "Complete", "Closed", "Resolved"],
    "in_progress": ["In Progress", "In Development", "In Review", "Active", "In-Progress"],
    "backlog":    ["To Do", "Backlog", "Not Started", "Open", "New", "Pending"],
    "de_scoped":  ["De-scoped", "De-Scoped", "Won't Do", "Cancelled", "Rejected", "Invalid", "Withdrawn"],
}


# =============================================================================
# 7. REGION IDENTIFICATION
# =============================================================================
# The JIRA field that holds the region for each Story.
# Paste the FIELD KEY (no spaces) from find_jira_fields.py.
#
REGION_FIELD = "customfield_XXXXX"  # field KEY

# Canonical region names shown as rows in the Region slide (order = row order)
REGIONS = ["APAC", "EMEA", "Global", "Japan", "North America", "TG"]


# =============================================================================
# 8. INSTANCE TYPE — PROD vs NON-PROD  (identified from Sub-tasks)
# =============================================================================
# Each Sub-task has a field that says whether it is a Prod or Non-Prod instance.
# Paste the FIELD KEY for that field.
#
INSTANCE_TYPE_FIELD = "customfield_XXXXX"   # field KEY on the Sub-task

# Map JIRA field values on Sub-tasks → "prod" or "non_prod"
INSTANCE_TYPE_MAPPING = {
    "prod":     ["Production", "Prod", "PRD", "prod"],
    "non_prod": ["Non-Production", "Non-Prod", "NP", "UAT", "Staging", "Dev", "Test", "non-prod"],
}

# Set True if INSTANCE_TYPE_FIELD is not available and type should be inferred
# from keywords in the Sub-task summary line instead.
INSTANCE_TYPE_FROM_SUMMARY = False

# Sub-task statuses that count as "done / complete"
SUBTASK_DONE_STATUSES = ["Done", "Completed", "Closed", "Resolved"]

# ── Alternative: instance counts as custom fields on the Story ───────────────
# If JQL_SUBTASKS = "" (no sub-tasks), the loader reads these number fields
# directly from each Story to get Prod/Non-Prod counts.
# Leave as "customfield_XXXXX" (placeholder) when using sub-tasks.
INSTANCE_COUNT_FIELDS = {
    "prod_done"      : "customfield_XXXXX",  # display name e.g. "Prod Instances Done"
    "prod_total"     : "customfield_XXXXX",  # display name e.g. "Prod Instances Total"
    "non_prod_done"  : "customfield_XXXXX",  # display name e.g. "NP Instances Done"
    "non_prod_total" : "customfield_XXXXX",  # display name e.g. "NP Instances Total"
}


# =============================================================================
# 9. EXTRA SLIDE SECTIONS  (Blockers slide + Milestones slide)
# =============================================================================
#
# BLOCKERS SLIDE
# ──────────────
# Provide a JQL that returns all blocker/impediment issues.
# Common approaches:
#   - Issues with a specific label:   'project = SSPM AND labels = "blocker"'
#   - Issues in a specific Epic:      '"Epic Link" = SSPM-99 ORDER BY priority DESC'
#   - Issues with a custom flag:      'project = SSPM AND "Blocker Flag" = Yes'
#   - Issues of a specific type:      'project = SSPM AND issuetype = "Impediment"'
# Set jql = "" to skip this slide entirely.
#
# MILESTONES SLIDE
# ────────────────
# Provide a JQL that returns milestone/roadmap issues.
# Each issue becomes one milestone section; its sub-tasks become the task rows.
# Common approaches:
#   - Epic query:     '"Epic Link" = SSPM-20 ORDER BY key ASC'
#   - Label query:    'project = SSPM AND labels = "milestone" ORDER BY duedate ASC'
#   - Issuetype:      'project = SSPM AND issuetype = Epic ORDER BY created ASC'
# Task count is DYNAMIC — any number of sub-tasks per milestone auto-paginate.
# Set jql = "" to skip this slide entirely.
#
# FIELD KEY REMINDER: use find_jira_fields.py to get the correct key for each field.
#
EXTRA_SECTIONS = {
    "blockers": {
        # ← EDIT THIS: JQL that returns your blocker issues
        "jql":         "",
        # e.g.  'project = SSPM AND labels = "blocker" ORDER BY priority DESC'
        # e.g.  '"Epic Link" = SSPM-99 ORDER BY created ASC'
        "slide_title": "Blockers & Impediments",
        "fields": {
            "owner_field":  "assignee",           # built-in JIRA field — keep as-is
            "impact_field": "customfield_XXXXX",  # field KEY for High/Med/Low impact
            "phase_field":  "customfield_XXXXX",  # same field KEY as PHASE_FIELD
        },
    },
    "milestones": {
        # ← EDIT THIS: JQL that returns your milestone/roadmap issues
        "jql":         "",
        # e.g.  '"Epic Link" = SSPM-20 ORDER BY key ASC'
        # e.g.  'project = SSPM AND issuetype = Epic ORDER BY created ASC'
        "slide_title": "Milestones & Roadmap",
        "fields": {
            "phase_field":  "customfield_XXXXX",  # field KEY for phase
            "target_field": "customfield_XXXXX",  # field KEY for target date/sprint
            "status_field": "status",             # "status" or a custom field KEY
        },
    },
}


# =============================================================================
# 10. VISUAL THEME
# =============================================================================

THEME = {
    "bg"        : (0xF8, 0xF9, 0xFB),
    "header"    : (0x1A, 0x3A, 0x6B),
    "card"      : (0xFF, 0xFF, 0xFF),
    "card_alt"  : (0xF1, 0xF5, 0xF9),
    "border"    : (0xCB, 0xD5, 0xE1),
    "accent"    : (0x00, 0x7A, 0xCC),
    "green"     : (0x05, 0x96, 0x69),
    "amber"     : (0xD9, 0x77, 0x06),
    "red"       : (0xDC, 0x26, 0x26),
    "purple"    : (0x6D, 0x28, 0xD9),
    "teal"      : (0x04, 0x7A, 0x57),
    "gray"      : (0x64, 0x74, 0x8B),
    "white"     : (0xFF, 0xFF, 0xFF),
    "txt_dark"  : (0x0F, 0x17, 0x2A),
    "txt_mid"   : (0x33, 0x41, 0x55),
    "txt_muted" : (0x64, 0x74, 0x8B),
}

# =============================================================================
# 10b. STATUS SYSTEM — 5 canonical statuses
# =============================================================================
#
# HOW THE STATUS PIPELINE WORKS
# ──────────────────────────────
# Step 1 — JIRA RAW VALUE  (what the JIRA dropdown field actually contains)
#           e.g. "Onboarding In Progress", "Future Request - Integration Not
#                currently Supported", "De-Scoped", etc.
#
# Step 2 — STATUS_MAPPING  (map raw JIRA value → one of 5 internal keys)
#           Add every synonym/variant your JIRA instance uses.
#           Matching is case-insensitive. The 5 internal keys are fixed:
#             completed | de_scoped | future_request | not_started | in_progress
#
# Step 3 — STATUS_LABELS  (what appears in PPT pills and slide cells)
#           Edit these to control the exact wording shown in the deck.
#           Keep them SHORT — pills are narrow.
#
# Step 4 — STATUS_SHORT  (tiny label for the KPI colour bar below phase cards)
#           Must be ≤ 8 characters to avoid overlap in the compact chip row.
#
# =============================================================================

# ── Step 2: Map raw JIRA dropdown text → internal key ────────────────────────
# Add every variant your JIRA project uses as extra list entries.
STATUS_MAPPING = {
    "completed":      ["Completed", "Done", "Complete", "Closed"],
    "de_scoped":      ["De-Scoped", "De-scoped", "Descoped", "Won't Do", "Cancelled"],
    "future_request": [
        "Future Request",
        "Future Request - Integration Not currently Supported",
        "Future-Request", "Future", "Planned",
    ],
    "not_started":    ["Not Started", "To Do", "Open", "Backlog", "New", "Pending"],
    "in_progress":    [
        "Onboarding In Progress",
        "In Progress", "In Development", "In Review", "Active", "In-Progress",
    ],
}

# ── Step 3: PPT display labels (shown in pills on slides 3+) ─────────────────
# Edit the RIGHT-hand values only. Keep them concise (≤ 20 chars recommended).
STATUS_LABELS = {
    "completed":      "Completed",
    "de_scoped":      "De-Scoped",
    "future_request": "Future Request",
    "not_started":    "Not Started",
    "in_progress":    "In Progress",
}

# ── Step 4: Compact chip labels for KPI colour bar (≤ 8 chars) ───────────────
STATUS_SHORT = {
    "completed":      "Done",
    "de_scoped":      "D-Scoped",
    "future_request": "Future",
    "not_started":    "Not Strt",
    "in_progress":    "In Prog",
}

# Status → theme colour key (defined in THEME section above)
STATUS_COLORS = {
    "completed":      "green",
    "de_scoped":      "purple",
    "future_request": "teal",
    "not_started":    "gray",
    "in_progress":    "amber",
}

# For detail slides (slide 3/4): statuses that roll up to "Completed" (green)
# Everything else is shown as its own status pill.
COMPLETED_STATUSES = ["completed", "de_scoped"]

# =============================================================================
# 11. DETAIL SLIDES — PHASE SCOPE
# =============================================================================
# Phases listed here get full per-application detail slides (dynamic, multi-page).
# All other phases appear only in the summary table row (aggregated counts).
# Typically Phase 1 + Phase 2 = the active in-scope phases.
#
IN_SCOPE_PHASES = ["Phase 1", "Phase 2"]

# Max application rows per detail slide (increase to pack more rows in)
ROWS_PER_DETAIL_SLIDE = 6
