# =============================================================================
# config.py  —  SSPM PPT Generator Settings
# =============================================================================
# This is the ONLY file you need to edit.
#
# IMPORTANT — FIELD NAMES WITH SPACES
# =====================================
# JIRA has TWO completely different things that look like field names:
#
#   1. FIELD KEY  (used in API responses — what you put in config.py)
#      - Always a single word, no spaces
#      - Format: customfield_10042  or  status  or  priority  or  assignee
#      - This is what find_jira_fields.py prints in the LEFT column
#      - This is what you paste into this config file
#      - Example:  "prod_done" : "customfield_10042"   ✅ correct
#
#   2. DISPLAY NAME  (shown in the JIRA UI — do NOT use in config.py)
#      - Can have spaces, e.g. "Prod Instances Done", "Epic Link", "App Tier"
#      - This appears in the RIGHT column of find_jira_fields.py output
#      - NEVER use the display name as a field key — it will break
#      - Example:  "prod_done" : "Prod Instances Done"  ❌ WRONG — will not work
#
#   EXCEPTION — field VALUES (dropdown options, label text, priority names):
#      - These CAN and often DO have spaces
#      - e.g. "In Progress", "Epic Link", "P1 - Critical Apps"
#      - Spaces in VALUES are fine — only spaces in KEYS are the problem
#
# QUICK REFERENCE:
#   "Epic Link" as a JQL field name     → put it in quotes in JQL: "Epic Link" = SSPM-10  ✅
#   "Epic Link" as a Python dict key    → use the field key instead: customfield_10014     ✅
#   "Prod Instances Done" display name  → use the field key: customfield_10042             ✅
#   Priority value "Highest"            → use as-is, spaces fine in values                ✅
#   Label value "Non Prod"              → use as-is, spaces fine in values                ✅
# =============================================================================


# -----------------------------------------------------------------------------
# 1. OUTPUT
# -----------------------------------------------------------------------------

OUTPUT_FILE = "SSPM_Status_Light.pptx"


# -----------------------------------------------------------------------------
# 2. JIRA CONNECTION
# -----------------------------------------------------------------------------
# Set USE_JIRA = False  →  reads data.py (manual, default)
# Set USE_JIRA = True   →  calls JIRA REST API live
#
# API token:  https://id.atlassian.com → Security → API tokens → Create
# -----------------------------------------------------------------------------

USE_JIRA       = False
JIRA_BASE_URL  = "https://yourcompany.atlassian.net"   # no trailing slash
JIRA_EMAIL     = "you@yourcompany.com"
JIRA_API_TOKEN = "YOUR_API_TOKEN_HERE"
JIRA_PROJECT   = "SSPM"                                # your project key, e.g. "SSPM"


# =============================================================================
# HOW TO FIND FIELD KEYS (run this first before filling anything below)
# =============================================================================
#
#   python find_jira_fields.py SSPM-001
#
# This prints every field on that issue.  Output looks like:
#
#   FIELD KEY                           VALUE / DISPLAY NAME
#   -----------------------------------------------------------------------
#   customfield_10042                   3              ◄ CUSTOM
#   customfield_10043                   Prod Instances Done  ◄ CUSTOM
#   customfield_10044                   Yes            ◄ CUSTOM
#   priority                            Highest
#   status                              In Progress
#   assignee                            John Smith
#
#   LEFT column  = field KEY  → paste this into config.py below
#   RIGHT column = field VALUE / display name → for reference only, do not paste
#
# =============================================================================


# =============================================================================
# 2a. HOW JIRA IDENTIFIES TIERS  (P1 / P2 / P3 / P4 / P5)
# =============================================================================
#
# OPTION A — JIRA Priority field  (most common, works out of the box)
# -------------------------------------------------------------------
# Set TIER_SOURCE = "priority"
# The priority field key is simply "priority" — no customfield_ prefix needed.
# The priority NAMES (Highest, High etc.) are VALUES — spaces in them are fine.
#
# OPTION B — Custom dropdown field  (e.g. a field called "SSPM Tier")
# -------------------------------------------------------------------
# Your display name might be "SSPM Tier" or "App Priority" (spaces in name — fine).
# But find_jira_fields.py will show its KEY as e.g. customfield_10055.
# Set TIER_SOURCE = "customfield_10055"   ← the KEY (no spaces), not the display name.
# Then fill TIER_CUSTOM_VALUES with the exact dropdown option texts (spaces OK there).
#
# OPTION C — Epic  (one Epic per tier)
# -------------------------------------------------------------------
# Set TIER_SOURCE = "epic" and fill EPIC_IDS below.
# The tier is determined by which Epic a Story belongs to.
#
# =============================================================================

TIER_SOURCE = "priority"     # "priority"  |  "customfield_XXXXX"  |  "epic"

# Used when TIER_SOURCE = "priority"
# Left side  = exact Priority VALUE shown in JIRA UI (spaces OK — it's a value, not a key)
# Right side = tier label used in the PPT
JIRA_PRIORITY_TO_TIER = {
    "Highest" : "P1",    # ← if your JIRA shows "Critical" instead, write "Critical": "P1"
    "High"    : "P2",
    "Medium"  : "P3",
    "Low"     : "P4",
    "Lowest"  : "P5",
}

# Used when TIER_SOURCE = "customfield_XXXXX"
# TIER_CUSTOM_FIELD = the field KEY from find_jira_fields.py  (no spaces allowed)
# TIER_CUSTOM_VALUES maps the dropdown OPTION TEXT → tier label  (spaces in option text OK)
#
# Example — your JIRA field is called "App Priority" (display name with space).
# find_jira_fields.py shows its key is customfield_10055.
# The dropdown options are "P1 - Critical Apps", "P2 - High" etc.
# You write:
#   TIER_CUSTOM_FIELD  = "customfield_10055"          ← KEY, no spaces
#   TIER_CUSTOM_VALUES = {
#       "P1 - Critical Apps" : "P1",                  ← VALUE, spaces OK
#       "P2 - High"          : "P2",
#   }
TIER_CUSTOM_FIELD  = "customfield_XXXXX"
TIER_CUSTOM_VALUES = {
    "P1 - Critical" : "P1",
    "P2 - High"     : "P2",
    "P3 - Medium"   : "P3",
    "P4 - Low"      : "P4",
    "P5 - Minimal"  : "P5",
}


# =============================================================================
# 2b. HOW JIRA IDENTIFIES PROD vs NON-PROD INSTANCE COUNTS
# =============================================================================
#
# Your custom fields hold instance counts as numbers on each Story.
# Their DISPLAY NAMES probably have spaces, e.g.:
#   "Prod Instances Done"   →  field key: customfield_10042
#   "Prod Instances Total"  →  field key: customfield_10043
#   "NP Instances Done"     →  field key: customfield_10044
#   "NP Instances Total"    →  field key: customfield_10045
#
# You use the FIELD KEY (no spaces) in config — not the display name.
#
# INSTANCE_SOURCE options:
#   "custom_fields"  → counts come from number fields on the Story (recommended)
#   "subtask_label"  → counts derived from sub-tasks labelled Prod / Non-Prod
#   "component"      → counts derived from JIRA Components on the Story
#
# =============================================================================

INSTANCE_SOURCE = "custom_fields"

# Paste the FIELD KEY for each count (left column from find_jira_fields.py output)
# The display name has spaces — that is fine — but use the KEY here, not the name.
#
# HOW TO FIND EACH KEY:
#   1. Run: python find_jira_fields.py SSPM-001
#   2. Find the row whose right column says something like "Prod Instances Done"
#   3. Copy the LEFT column value (e.g. customfield_10042)
#   4. Paste it as the value below
#
INSTANCE_FIELDS = {
    # PPT concept       Field KEY (from find_jira_fields.py)   Display name (for your reference)
    "prod_done"  : "customfield_XXXXX",   # e.g. "Prod Instances Done"    — number field
    "prod_total" : "customfield_XXXXX",   # e.g. "Prod Instances Total"   — number field
    "np_done"    : "customfield_XXXXX",   # e.g. "NP Instances Done"      — number field
    "np_total"   : "customfield_XXXXX",   # e.g. "NP Instances Total"     — number field (0 = no NP)
}

# Used only when INSTANCE_SOURCE = "subtask_label"
# These are label VALUES in JIRA — spaces in the label text are fine here
PROD_LABEL    = "Prod"       # exact label text on Prod sub-tasks     (spaces OK in value)
NONPROD_LABEL = "Non-Prod"   # exact label text on Non-Prod sub-tasks (spaces OK in value)


# =============================================================================
# 2c. HOW JIRA IDENTIFIES WHICH STORIES BELONG TO EACH SLIDE SECTION
# =============================================================================
#
# The generator fetches Stories under each Epic using JQL.
# "Epic Link" is the JQL field name — it has a space.
# In JQL queries, field names with spaces are wrapped in double quotes:
#   "Epic Link" = SSPM-10
#
# This is handled automatically inside jira_loader.py — you just paste
# the Epic issue key below (e.g. "SSPM-10"). No spaces issue for you here.
#
# EPIC_LINK_STYLE:
#   "classic"  → JQL uses  "Epic Link" = KEY   (older JIRA Software projects)
#   "nextgen"  → JQL uses  parent = KEY        (team-managed / next-gen projects)
#
# How to tell which one:
#   Run find_jira_fields.py on a Story.
#   If you see a field called "Epic Link" in the output → use "classic"
#   If you see "parent" pointing to an Epic key        → use "nextgen"
#
# =============================================================================

EPIC_LINK_STYLE = "classic"    # "classic"  |  "nextgen"

EPIC_IDS = {
    # Section in PPT       Epic issue key    Stories it contains
    "p1_apps"    : "SSPM-10",   # one Story per P1 app being onboarded
    "p2_apps"    : "SSPM-11",   # one Story per P2 app being onboarded
    "p1_blockers": "SSPM-12",   # blocker / impediment tickets for P1
    "s3_blockers": "SSPM-13",   # cross-phase blockers (Phase 2 / Phase 3)
    "milestones" : "SSPM-14",   # Phase 2 and Phase 3 task stories
}


# =============================================================================
# 2d. HOW JIRA IDENTIFIES THE REGION OF EACH APP
# =============================================================================
#
# REGION_SOURCE options:
#   "custom_field"  →  a dropdown or text field on each Story holds the region name
#   "label"         →  Stories are tagged with labels like "APAC", "EMEA"
#   "component"     →  JIRA Components are named after regions
#
# For "custom_field":
#   The display name might be "App Region" or "Region" (spaces OK in display name).
#   Use the field KEY from find_jira_fields.py (no spaces).
#
# For "label":
#   The label VALUES can have spaces if yours do — e.g. "North America" is fine.
#   List every region label exactly as it appears in JIRA.
#
# =============================================================================

REGION_SOURCE = "custom_field"    # "custom_field"  |  "label"  |  "component"

# Used when REGION_SOURCE = "custom_field"
# Paste the field KEY (no spaces) — the display name "App Region" is irrelevant here
REGION_FIELD  = "customfield_XXXXX"

# Used when REGION_SOURCE = "label"
# List exact label VALUES from JIRA — spaces in label values are fine
REGION_LABELS = ["APAC", "EMEA", "Global", "Japan", "North America", "TG"]

# Regions shown as rows in Slide 2 (order controls row order top to bottom)
REGIONS = ["APAC", "EMEA", "Global", "Japan", "North America", "TG"]


# =============================================================================
# 2e. OTHER FIELD MAPPINGS  (blockers and phase tags)
# =============================================================================
#
# "status" and "assignee" are built-in JIRA fields — their keys have no spaces.
# Custom fields below: use the field KEY (no spaces), not the display name.
#
# Example — your field is displayed as "Is Blocker?" in JIRA UI.
# find_jira_fields.py shows its key is customfield_10060.
# You write:  "customfield_10060" : "is_blocker"   ← KEY on left, no spaces
#
# =============================================================================

OTHER_FIELDS = {
    # Field KEY (no spaces)    →  PPT concept      Notes
    "status"            : "onboard_status",   # built-in — do not change
    "assignee"          : "owner",            # built-in — do not change
    "customfield_XXXXX" : "is_blocker",       # custom — value: "Yes" / "No"
    "customfield_XXXXX" : "impact",           # custom — value: "High" / "Med" / "Low"
    "customfield_XXXXX" : "phase",            # custom — value: "Phase 1" / "Phase 2" / "Phase 3"
}

# How JIRA status VALUES map to PPT status labels
# Status values can have spaces — that is fine here (they are values, not keys)
JIRA_STATUS_MAP = {
    "Done"        : "Completed",
    "In Progress" : "In Progress",   # ← "In Progress" has a space — fine, it's a value
    "To Do"       : "Not Started",   # ← "To Do" has a space — fine
    "Blocked"     : "Not Started",
    "Open"        : "Not Started",
}


# =============================================================================
# 3. VISUAL THEME
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
