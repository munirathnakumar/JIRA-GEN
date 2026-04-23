# =============================================================================
# jira_loader.py  —  JIRA Data Fetcher  (re-wired architecture)
# =============================================================================
# Called by generator.py when USE_JIRA = True.
# Uses two JQL queries from config.py:
#   JQL_STORIES  → one Story per SaaS instance; grouped by application
#   JQL_SUBTASKS → sub-tasks identify Prod vs Non-Prod environment per instance
#
# Returns a dict matching the structure of data.py APPLICATIONS.
# =============================================================================

import requests
from requests.auth import HTTPBasicAuth

from config import (
    JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN,
    JQL_STORIES, JQL_SUBTASKS,
    APPLICATION_GROUPING, APPLICATION_FIELD, APPLICATION_SUMMARY_SEPARATOR,
    PHASE_FIELD,
    STATUS_FIELD, STATUS_MAPPING,
    REGION_FIELD,
    INSTANCE_TYPE_FIELD, INSTANCE_TYPE_MAPPING,
    INSTANCE_TYPE_FROM_SUMMARY, SUBTASK_DONE_STATUSES,
    INSTANCE_COUNT_FIELDS,
    EXTRA_SECTIONS,
)


# ─────────────────────────────────────────────────────────────────────────────
# HTTP helpers
# ─────────────────────────────────────────────────────────────────────────────

def _auth():
    return HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

def _headers():
    return {"Accept": "application/json"}

def _get(url, params=None):
    resp = requests.get(url, headers=_headers(), auth=_auth(), params=params)
    resp.raise_for_status()
    return resp.json()

def _post(url, body):
    headers = {**_headers(), "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, auth=_auth(), json=body)
    if not resp.ok:
        print(f"\n❌  JIRA API error {resp.status_code} — {url}")
        try:
            err = resp.json()
            for msg in err.get("errorMessages", []):
                print(f"    {msg}")
            for k, v in err.get("errors", {}).items():
                print(f"    {k}: {v}")
        except Exception:
            print(f"    {resp.text[:300]}")
        resp.raise_for_status()
    return resp.json()

def _field(issue, key):
    """Safely read a field from a JIRA issue dict."""
    return (issue.get("fields") or {}).get(key)

def _field_value(raw):
    """Extract a string value from a JIRA field (handles dict, string, None)."""
    if raw is None:
        return ""
    if isinstance(raw, dict):
        return raw.get("value") or raw.get("name") or raw.get("displayName") or ""
    return str(raw)


# ─────────────────────────────────────────────────────────────────────────────
# Paginated JQL search
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_all(jql, extra_fields=""):
    """
    Execute a JQL query and return ALL matching issues (auto-paginated).
    Uses POST /rest/api/3/search/jql with cursor-based pagination (nextPageToken).
    jql may contain spaces and quoted field names — passed as-is to the API.
    """
    if not jql:
        return []

    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    base = ["summary", "status", "assignee", "parent", "subtasks"]
    if extra_fields:
        base += [f.strip() for f in extra_fields.split(",") if f.strip()]

    issues          = []
    next_page_token = None

    while True:
        body = {
            "jql"       : jql,
            "maxResults": 100,
            "fields"    : base,
        }
        if next_page_token:
            body["nextPageToken"] = next_page_token

        data  = _post(url, body)
        batch = data.get("issues", [])
        issues.extend(batch)

        next_page_token = data.get("nextPageToken")
        if not next_page_token or not batch:
            break

    return issues


# ─────────────────────────────────────────────────────────────────────────────
# Field extractors
# ─────────────────────────────────────────────────────────────────────────────

def _get_application(issue):
    """Determine which application a story belongs to."""
    if APPLICATION_GROUPING == "epic_name":
        epic = _field(issue, "epic") or {}
        return epic.get("name") or epic.get("summary") or "Unknown"

    if APPLICATION_GROUPING == "custom_field":
        return _field_value(_field(issue, APPLICATION_FIELD)) or "Unknown"

    if APPLICATION_GROUPING == "label":
        labels = _field(issue, "labels") or []
        return labels[0] if labels else "Unknown"

    if APPLICATION_GROUPING == "component":
        comps = _field(issue, "components") or []
        return comps[0].get("name", "Unknown") if comps else "Unknown"

    if APPLICATION_GROUPING == "summary_prefix":
        summary = _field(issue, "summary") or ""
        sep = APPLICATION_SUMMARY_SEPARATOR
        if sep in summary:
            return summary.split(sep)[0].strip()
        return summary.split()[0] if summary else "Unknown"

    return "Unknown"


def _get_phase(issue):
    return _field_value(_field(issue, PHASE_FIELD)) or ""


def _get_region(issue):
    return _field_value(_field(issue, REGION_FIELD)) or "Unknown"


def _map_status(issue):
    """Map a story's JIRA status to one of: completed|in_progress|backlog|de_scoped."""
    if STATUS_FIELD == "status":
        raw = (_field(issue, "status") or {}).get("name", "")
    else:
        raw = _field_value(_field(issue, STATUS_FIELD))

    val_lower = raw.lower()
    for canonical, values in STATUS_MAPPING.items():
        if any(v.lower() == val_lower for v in values):
            return canonical
    return "backlog"


def _get_instance_type(subtask):
    """Return "prod" or "non_prod" for a Sub-task."""
    if INSTANCE_TYPE_FROM_SUMMARY:
        summary = (_field(subtask, "summary") or "").lower()
        for kw in ["non-prod", "nonprod", "non_prod", "uat", "staging", "dev", "test", "sandbox"]:
            if kw in summary:
                return "non_prod"
        return "prod"

    raw = _field_value(_field(subtask, INSTANCE_TYPE_FIELD))
    raw_lower = raw.lower()
    for canonical, values in INSTANCE_TYPE_MAPPING.items():
        if any(v.lower() == raw_lower for v in values):
            return canonical
    return "prod"


def _subtask_done(subtask):
    status = (_field(subtask, "status") or {}).get("name", "")
    return status in SUBTASK_DONE_STATUSES


def _instance_counts_from_fields(story):
    """Fallback: read Prod/NP counts from number custom fields on the Story."""
    def _num(key):
        v = _field(story, INSTANCE_COUNT_FIELDS.get(key, ""))
        try:
            return int(v or 0)
        except (TypeError, ValueError):
            return 0
    return {
        "prod_done"      : _num("prod_done"),
        "prod_total"     : _num("prod_total"),
        "non_prod_done"  : _num("non_prod_done"),
        "non_prod_total" : _num("non_prod_total"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Build field list strings for API requests
# ─────────────────────────────────────────────────────────────────────────────

def _story_extra_fields():
    fields = [PHASE_FIELD, REGION_FIELD]
    if STATUS_FIELD != "status":
        fields.append(STATUS_FIELD)
    if APPLICATION_GROUPING == "custom_field":
        fields.append(APPLICATION_FIELD)
    if APPLICATION_GROUPING == "epic_name":
        fields.append("epic")
    if APPLICATION_GROUPING == "label":
        fields.append("labels")
    if APPLICATION_GROUPING == "component":
        fields.append("components")
    # instance count fields (used when no sub-tasks)
    for f in INSTANCE_COUNT_FIELDS.values():
        if f and f != "customfield_XXXXX":
            fields.append(f)
    return ",".join(f for f in fields if f and f != "customfield_XXXXX")


def _subtask_extra_fields():
    if INSTANCE_TYPE_FIELD and INSTANCE_TYPE_FIELD != "customfield_XXXXX":
        return INSTANCE_TYPE_FIELD
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def load_from_jira():
    """
    Fetch data from JIRA using the two JQL queries defined in config.py.

    Returns:
    {
        "applications": [
            {
                "name": "Salesforce",
                "instances": [
                    {
                        "key":           "SSPM-101",
                        "summary":       "Salesforce - APAC Prod",
                        "phase":         "Phase 1",
                        "status":        "completed",   # completed|in_progress|backlog|de_scoped
                        "region":        "APAC",
                        "prod_done":     1,
                        "prod_total":    1,
                        "non_prod_done": 0,
                        "non_prod_total":1,
                    },
                    ...
                ]
            },
            ...
        ],
        "extra_sections": {
            "blockers":   [ ...raw JIRA issue dicts... ],
            "milestones": [ ...raw JIRA issue dicts... ],
        }
    }
    """
    print("Connecting to JIRA...")

    # ── Fetch stories ─────────────────────────────────────────────────────────
    print(f"  Fetching stories:  {JQL_STORIES[:80]}...")
    stories = _fetch_all(JQL_STORIES, extra_fields=_story_extra_fields())
    print(f"  → {len(stories)} stories")

    # ── Fetch sub-tasks (if JQL_SUBTASKS configured) ──────────────────────────
    use_subtasks = bool(JQL_SUBTASKS)
    subtasks_by_parent = {}

    if use_subtasks:
        print(f"  Fetching subtasks: {JQL_SUBTASKS[:80]}...")
        subtasks = _fetch_all(JQL_SUBTASKS, extra_fields=_subtask_extra_fields())
        print(f"  → {len(subtasks)} subtasks")

        for st in subtasks:
            parent_key = ((_field(st, "parent") or {}).get("key") or "")
            if parent_key:
                subtasks_by_parent.setdefault(parent_key, []).append(st)

    # ── Group stories by application ──────────────────────────────────────────
    apps_dict = {}

    for story in stories:
        app_name = _get_application(story)
        story_key = story.get("key", "")

        if use_subtasks:
            story_subtasks = subtasks_by_parent.get(story_key, [])
            prod_sts  = [s for s in story_subtasks if _get_instance_type(s) == "prod"]
            np_sts    = [s for s in story_subtasks if _get_instance_type(s) == "non_prod"]
            counts = {
                "prod_done"      : sum(1 for s in prod_sts if _subtask_done(s)),
                "prod_total"     : len(prod_sts),
                "non_prod_done"  : sum(1 for s in np_sts  if _subtask_done(s)),
                "non_prod_total" : len(np_sts),
            }
        else:
            counts = _instance_counts_from_fields(story)

        instance = {
            "key"    : story_key,
            "summary": _field(story, "summary") or "",
            "phase"  : _get_phase(story),
            "status" : _map_status(story),
            "region" : _get_region(story),
            **counts,
        }

        apps_dict.setdefault(app_name, []).append(instance)

    applications = [
        {"name": name, "instances": instances}
        for name, instances in sorted(apps_dict.items())
    ]
    print(f"  → {len(applications)} applications identified")

    # ── Fetch extra sections ──────────────────────────────────────────────────
    extra_sections = {}
    for section_key, cfg in EXTRA_SECTIONS.items():
        jql = cfg.get("jql", "")
        if jql:
            print(f"  Fetching {section_key}: {jql[:60]}...")
            extra_sections[section_key] = _fetch_all(jql)
            print(f"  → {len(extra_sections[section_key])} issues")
        else:
            extra_sections[section_key] = []

    print("JIRA data loaded.\n")
    return {
        "applications"  : applications,
        "extra_sections": extra_sections,
    }
