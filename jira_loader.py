# =============================================================================
# jira_loader.py  —  JIRA Data Fetcher
# =============================================================================
# Called automatically by generator.py when USE_JIRA = True in config.py.
# Fetches issues from JIRA and transforms them into the same data shape
# that data.py uses — so the slide builder never needs to change.
#
# You should NOT need to edit this file unless your JIRA custom field
# names differ from what is set in config.py → JIRA_FIELDS.
# =============================================================================

import requests
from requests.auth import HTTPBasicAuth
from config import (
    JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN,
    JIRA_PROJECT, JIRA_FIELDS,
    JIRA_PRIORITY_TO_TIER, JIRA_STATUS_MAP
)


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _auth():
    return HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

def _headers():
    return {"Accept": "application/json"}

def _get(url, params=None):
    """Make a JIRA REST API GET request and return parsed JSON."""
    resp = requests.get(url, headers=_headers(), auth=_auth(), params=params)
    resp.raise_for_status()
    return resp.json()

def _field(issue, field_key):
    """Safely read a field from a JIRA issue dict."""
    return issue.get("fields", {}).get(field_key)

def _map_status(jira_status_name):
    return JIRA_STATUS_MAP.get(jira_status_name, "Not Started")

def _map_tier(jira_priority_name):
    return JIRA_PRIORITY_TO_TIER.get(jira_priority_name, "P5")


# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Discover custom field IDs (run find_jira_fields.py for this)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_all_issues(tier_filter=None):
    """
    Fetch all SSPM issues from JIRA.
    tier_filter: "P1" | "P2" | None (fetch all)

    Returns a list of raw JIRA issue dicts.
    """
    # Build JQL query
    priority_map = {v: k for k, v in JIRA_PRIORITY_TO_TIER.items()}
    if tier_filter and tier_filter in priority_map:
        jql = f'project = {JIRA_PROJECT} AND priority = "{priority_map[tier_filter]}" ORDER BY key ASC'
    else:
        jql = f'project = {JIRA_PROJECT} ORDER BY priority ASC, key ASC'

    url    = f"{JIRA_BASE_URL}/rest/api/3/search"
    issues = []
    start  = 0

    # JIRA paginates at 100 per page — loop until all are fetched
    while True:
        data = _get(url, params={
            "jql"        : jql,
            "startAt"    : start,
            "maxResults" : 100,
            "fields"     : "summary,status,priority," + ",".join(JIRA_FIELDS.keys()),
        })
        issues.extend(data["issues"])
        start += len(data["issues"])
        if start >= data["total"]:
            break

    print(f"  Fetched {len(issues)} issues from JIRA project '{JIRA_PROJECT}'")
    return issues


# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Transform raw JIRA issues → P1_APPS format (Slide 1)
# ─────────────────────────────────────────────────────────────────────────────

def build_p1_apps(issues):
    """
    Build the P1_APPS list from JIRA issues.
    Each issue = one app.  Prod/NP counts come from custom fields.
    """
    p1_apps = []
    for idx, issue in enumerate(issues, start=1):
        priority_name = (_field(issue, "priority") or {}).get("name", "")
        if _map_tier(priority_name) != "P1":
            continue

        prod_done  = int(_field(issue, JIRA_FIELDS["customfield_prod_done"])  or 0)
        prod_total = int(_field(issue, JIRA_FIELDS["customfield_prod_total"]) or 0)
        np_done    = int(_field(issue, JIRA_FIELDS["customfield_np_done"])    or 0)
        np_total   = int(_field(issue, JIRA_FIELDS["customfield_np_total"])   or 0)

        # Build one instance entry per Prod slot and per NP slot
        instances = []
        for n in range(prod_total):
            instances.append({"env": "Prod",     "done": n < prod_done})
        for n in range(np_total):
            instances.append({"env": "Non-Prod", "done": n < np_done})

        p1_apps.append({
            "name"     : f"A{idx}",          # Replace with issue["key"] if you want real keys
            "instances": instances,
        })

    return p1_apps


def build_p1_blockers(issues):
    """
    Build the P1_BLOCKERS list.
    Issues are treated as blockers if the blocker custom field = "Yes".
    """
    blockers = []
    idx = 1
    for issue in issues:
        is_blocker = _field(issue, JIRA_FIELDS["customfield_blocker"])
        if str(is_blocker).lower() not in ("yes", "true", "1"):
            continue

        priority_name = (_field(issue, "priority") or {}).get("name", "")
        if _map_tier(priority_name) != "P1":
            continue

        impact = _field(issue, JIRA_FIELDS["customfield_impact"]) or "Med"
        owner  = _field(issue, JIRA_FIELDS["customfield_owner"])  or "TBD"
        summary = (issue.get("fields") or {}).get("summary", "No description")

        blockers.append({
            "id"    : f"B{idx}",
            "text"  : summary,
            "owner" : owner,
            "impact": impact,
        })
        idx += 1

    return blockers


# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Transform → P2_APPS format (Slide 2)
# ─────────────────────────────────────────────────────────────────────────────

def build_p2_apps(issues):
    """Build the P2_APPS list from JIRA issues."""
    p2_apps = []
    idx = 1
    for issue in issues:
        priority_name = (_field(issue, "priority") or {}).get("name", "")
        if _map_tier(priority_name) != "P2":
            continue

        prod_done  = int(_field(issue, JIRA_FIELDS["customfield_prod_done"])  or 0)
        prod_total = int(_field(issue, JIRA_FIELDS["customfield_prod_total"]) or 1)
        np_done    = int(_field(issue, JIRA_FIELDS["customfield_np_done"])    or 0)
        np_total   = int(_field(issue, JIRA_FIELDS["customfield_np_total"])   or 0)

        p2_apps.append({
            "name"      : f"A{idx}",
            "prod_done" : prod_done,
            "prod_total": prod_total,
            "np_done"   : np_done,
            "np_total"  : np_total,
        })
        idx += 1

    return p2_apps


# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Build S3 blockers across all phases
# ─────────────────────────────────────────────────────────────────────────────

def build_s3_blockers(issues):
    """Build the cross-phase blockers for Slide 3."""
    blockers = []
    idx = 1
    for issue in issues:
        is_blocker = _field(issue, JIRA_FIELDS["customfield_blocker"])
        if str(is_blocker).lower() not in ("yes", "true", "1"):
            continue

        impact  = _field(issue, JIRA_FIELDS["customfield_impact"]) or "Med"
        owner   = _field(issue, JIRA_FIELDS["customfield_owner"])  or "TBD"
        phase   = _field(issue, JIRA_FIELDS["customfield_phase"])  or "Phase 1"
        summary = (issue.get("fields") or {}).get("summary", "No description")

        blockers.append({
            "id"    : f"B{idx}",
            "text"  : summary,
            "owner" : owner,
            "impact": impact,
            "phase" : phase,
        })
        idx += 1

    return blockers


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point — called by generator.py
# ─────────────────────────────────────────────────────────────────────────────

def load_from_jira():
    """
    Fetch all data from JIRA and return it in the same shape as data.py.
    Returns a dict with keys: p1_apps, p1_blockers, p2_apps, s3_blockers.
    TIER_SUMMARY and MILESTONES are not in JIRA — they come from data.py always.
    """
    print("Connecting to JIRA...")
    issues = fetch_all_issues()

    return {
        "p1_apps"     : build_p1_apps(issues),
        "p1_blockers" : build_p1_blockers(issues),
        "p2_apps"     : build_p2_apps(issues),
        "s3_blockers" : build_s3_blockers(issues),
    }
