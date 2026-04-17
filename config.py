# =============================================================================
# config.py  —  SSPM PPT Generator Settings
# =============================================================================
# This is the ONLY file you need to edit.
# It controls three things:
#   1. Output settings (filename)
#   2. JIRA connection + how JIRA identifies each piece of data
#   3. Visual theme colours
#
# Read every section carefully before enabling JIRA mode.
# Run  python find_jira_fields.py SSPM-001  first to discover field names.
# =============================================================================


# -----------------------------------------------------------------------------
# 1. OUTPUT
# -----------------------------------------------------------------------------

OUTPUT_FILE = "SSPM_Status_Light.pptx"


# -----------------------------------------------------------------------------
# 2. JIRA CONNECTION
# -----------------------------------------------------------------------------
# Set USE_JIRA = False  to read data.py (manual mode, default)
# Set USE_JIRA = True   to call JIRA REST API live
#
# How to get an API token:
#   1. Go to https://id.atlassian.com
#   2. Click Security → API tokens → Create API token
#   3. Give it a name (e.g. "SSPM PPT") and copy the token
#      (you will not see it again after closing the dialog)
# -----------------------------------------------------------------------------

USE_JIRA       = False
JIRA_BASE_URL  = "https://yourcompany.atlassian.net"   # No trailing slash
JIRA_EMAIL     = "you@yourcompany.com"
JIRA_API_TOKEN = "YOUR_API_TOKEN_HERE"
JIRA_PROJECT   = "SSPM"                                # Your JIRA project key


# =============================================================================
# HOW JIRA IDENTIFIES EACH DATA CONCEPT
# =============================================================================
# The sections below tell the generator WHERE to find each piece of data
# in JIRA.  Read each section, then fill in your actual values.
# Run  python find_jira_fields.py SSPM-001  to see all fields on a real issue.
# =============================================================================


# -----------------------------------------------------------------------------
# 2a. HOW JIRA IDENTIFIES TIERS (P1 / P2 / P3 / P4 / P5)
# -----------------------------------------------------------------------------
# OPTION A — Use JIRA Priority (most common, works out of the box)
#   Each story is assigned a JIRA Priority. Map priority names to tier labels.
#   Example: if your JIRA uses "Critical" for P1, change "Highest" to "Critical"
#
# OPTION B — Use a Custom Dropdown Field (e.g. a field called "SSPM Tier")
#   If your team created a custom field for tiers, set TIER_SOURCE to its
#   field ID (e.g. "customfield_10055"), then fill in TIER_CUSTOM_VALUES.
#
# OPTION C — Use Epic (recommended for larger teams)
#   Each Epic covers one tier. Stories under that Epic inherit the tier.
#   Set TIER_SOURCE = "epic" and define your Epic IDs in section 2c below.
#   The generator fetches stories under each Epic and assigns the tier
#   automatically based on which Epic the story belongs to.
# -----------------------------------------------------------------------------

TIER_SOURCE = "priority"     # "priority"  |  "customfield_XXXXX"  |  "epic"

# Used when TIER_SOURCE = "priority"
# Left side = exact Priority name in JIRA.  Right side = tier label in PPT.
JIRA_PRIORITY_TO_TIER = {
    "Highest"  : "P1",
    "High"     : "P2",
    "Medium"   : "P3",
    "Low"      : "P4",
    "Lowest"   : "P5",
}

# Used when TIER_SOURCE = "customfield_XXXXX"
# Replace "customfield_XXXXX" with the real field ID from find_jira_fields.py
TIER_CUSTOM_FIELD  = "customfield_XXXXX"
TIER_CUSTOM_VALUES = {
    "P1 - Critical" : "P1",   # Left = exact dropdown option in JIRA
    "P2 - High"     : "P2",   # Right = tier label used in the PPT
    "P3 - Medium"   : "P3",
    "P4 - Low"      : "P4",
    "P5 - Minimal"  : "P5",
}


# -----------------------------------------------------------------------------
# 2b. HOW JIRA IDENTIFIES PROD vs NON-PROD INSTANCES
# -----------------------------------------------------------------------------
# OPTION A — Custom number fields on each story (recommended)
#   One field holds Prod instances completed, another holds the total.
#   Same for Non-Prod.  Fill in the field IDs after running find_jira_fields.py.
#
# OPTION B — Environment label on each sub-task
#   Sub-tasks are labelled "Prod" or "Non-Prod".
#   The generator counts Done sub-tasks per label.
#   Set INSTANCE_SOURCE = "subtask_label".
#
# OPTION C — Component names
#   JIRA Components are named "Prod-Instance-1", "NP-Instance-1" etc.
#   Set INSTANCE_SOURCE = "component".
# -----------------------------------------------------------------------------

INSTANCE_SOURCE = "custom_fields"    # "custom_fields"  |  "subtask_label"  |  "component"

# Used when INSTANCE_SOURCE = "custom_fields"
# Replace each value with the real field ID from find_jira_fields.py
INSTANCE_FIELDS = {
    "prod_done"  : "customfield_XXXXX",   # Integer: Prod instances onboarded
    "prod_total" : "customfield_XXXXX",   # Integer: Total Prod instances for this app
    "np_done"    : "customfield_XXXXX",   # Integer: Non-Prod instances onboarded
    "np_total"   : "customfield_XXXXX",   # Integer: Total Non-Prod instances (0 = no NP env)
}

# Used when INSTANCE_SOURCE = "subtask_label"
PROD_LABEL    = "Prod"
NONPROD_LABEL = "Non-Prod"


# -----------------------------------------------------------------------------
# 2c. HOW JIRA IDENTIFIES WHICH STORIES BELONG TO EACH SLIDE SECTION
# -----------------------------------------------------------------------------
# The generator uses Epic IDs to scope which stories go into each section.
#
# HOW IT WORKS:
#   You create one Epic per slide section in your JIRA project.
#   The generator fetches all stories under each Epic using JQL:
#     Classic boards:   "Epic Link" = SSPM-10
#     Next-gen boards:  parent = SSPM-10
#
# HOW TO FIND YOUR EPIC KEYS:
#   1. Open your JIRA project Backlog or Board
#   2. Find the Epic that groups P1 app onboarding stories
#   3. Click it — the URL or detail panel shows the issue key (e.g. SSPM-10)
#   4. Repeat for P2, blockers, milestones etc.
#   5. Paste the keys below
#
# EPIC_LINK_STYLE:
#   "classic"  → uses  "Epic Link" = KEY   (older JIRA Software projects)
#   "nextgen"  → uses  parent = KEY        (team-managed / next-gen projects)
#   Not sure? Run find_jira_fields.py. If you see a field called "Epic Link",
#   use "classic". If you see "parent" pointing to an Epic, use "nextgen".
# -----------------------------------------------------------------------------

EPIC_LINK_STYLE = "classic"    # "classic"  |  "nextgen"

EPIC_IDS = {
    # Slide section        Epic key      Stories it should contain
    "p1_apps"     : "SSPM-10",   # One story per P1 app being onboarded
    "p2_apps"     : "SSPM-11",   # One story per P2 app being onboarded
    "p1_blockers" : "SSPM-12",   # Blocker / impediment tickets for P1
    "s3_blockers" : "SSPM-13",   # Cross-phase blockers (Phase 2 / Phase 3)
    "milestones"  : "SSPM-14",   # Phase 2 and Phase 3 task stories
    # Note: P3/P4/P5 summary and Regions are built from the same p1+p2 stories
    #       using the region field below — no separate Epic needed
}


# -----------------------------------------------------------------------------
# 2d. HOW JIRA IDENTIFIES THE REGION OF EACH APP
# -----------------------------------------------------------------------------
# The Region Summary slide (Slide 1) groups apps by region.
#
# OPTION A — Custom field on each story (recommended)
#   A dropdown or text field holding the region name (e.g. "APAC").
#
# OPTION B — Label on each story
#   Stories are tagged with labels like "APAC", "EMEA", "AMER".
#
# OPTION C — Component
#   JIRA Components are named after regions.
# -----------------------------------------------------------------------------

REGION_SOURCE = "custom_field"    # "custom_field"  |  "label"  |  "component"

# Used when REGION_SOURCE = "custom_field"
REGION_FIELD  = "customfield_XXXXX"   # Field ID from find_jira_fields.py

# Used when REGION_SOURCE = "label"
REGION_LABELS = ["APAC", "EMEA", "AMER", "GLOBAL"]

# Regions to show as columns in Slide 1 (order = column order left to right)
REGIONS = ["APAC", "EMEA", "AMER", "GLOBAL"]


# -----------------------------------------------------------------------------
# 2e. OTHER JIRA FIELD MAPPINGS
# -----------------------------------------------------------------------------
# Used for blocker stories and milestone task stories.
# Replace "customfield_XXXXX" with real IDs from find_jira_fields.py
# "status" and "assignee" are built-in JIRA fields — do not change those keys.
# -----------------------------------------------------------------------------

OTHER_FIELDS = {
    "status"            : "onboard_status",  # Built-in JIRA field
    "assignee"          : "owner",           # Built-in — assignee shown as blocker owner
    "customfield_XXXXX" : "is_blocker",      # "Yes" / "No"
    "customfield_XXXXX" : "impact",          # "High" / "Med" / "Low"
    "customfield_XXXXX" : "phase",           # "Phase 1" / "Phase 2" / "Phase 3"
}

# How JIRA status names map to PPT labels
JIRA_STATUS_MAP = {
    "Done"        : "Completed",
    "In Progress" : "In Progress",
    "To Do"       : "Not Started",
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
