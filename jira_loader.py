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
    SLIDE1_APP_GROUPING, SLIDE1_APP_FIELD, SLIDE1_APP_SEPARATOR,
    SLIDE3_APP_FIELD,
    APPENDIX_APP_FIELD, INSTANCE_NAME_FIELD, APP_ID_FIELD,
    PHASE_FIELD, PHASE_DISPLAY_NAMES,
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
        print(f"\n{'='*60}")
        print(f"❌  JIRA {resp.status_code} — {url}")
        print(f"    Raw response: {resp.text[:600]}")
        print(f"{'='*60}\n")
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

def _get_slide1_app(story):
    """App group for Slide 1 — read from Story using SLIDE1_APP_GROUPING."""
    if SLIDE1_APP_GROUPING == "epic_name":
        epic = _field(story, "epic") or {}
        return epic.get("name") or epic.get("summary") or "Unknown"
    if SLIDE1_APP_GROUPING == "custom_field":
        return _field_value(_field(story, SLIDE1_APP_FIELD)) or "Unknown"
    if SLIDE1_APP_GROUPING == "label":
        labels = _field(story, "labels") or []
        return labels[0] if labels else "Unknown"
    if SLIDE1_APP_GROUPING == "component":
        comps = _field(story, "components") or []
        return comps[0].get("name", "Unknown") if comps else "Unknown"
    if SLIDE1_APP_GROUPING == "summary_prefix":
        summary = _field(story, "summary") or ""
        sep = SLIDE1_APP_SEPARATOR
        return summary.split(sep)[0].strip() if sep in summary else summary.split()[0]
    return "Unknown"

def _get_slide3_app(subtask):
    """App group for Slide 3 — read from Sub-task using SLIDE3_APP_FIELD."""
    return _field_value(_field(subtask, SLIDE3_APP_FIELD)) or "Unknown"

def _get_appendix_app(subtask):
    """App name for Appendix — read from Sub-task using APPENDIX_APP_FIELD."""
    return _field_value(_field(subtask, APPENDIX_APP_FIELD)) or "Unknown"


def _get_phase(issue):
    """Return raw JIRA phase value — display name mapping applied in generator."""
    return _field_value(_field(issue, PHASE_FIELD)) or ""

def _get_instance_name(issue):
    if INSTANCE_NAME_FIELD == "summary":
        return _field(issue, "summary") or ""
    return _field_value(_field(issue, INSTANCE_NAME_FIELD)) or _field(issue, "summary") or ""

def _get_app_id(issue):
    if APP_ID_FIELD and APP_ID_FIELD != "customfield_XXXXX":
        return _field_value(_field(issue, APP_ID_FIELD)) or "—"
    return "—"


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
    """Fields to fetch on Stories (for Slide 1)."""
    fields = [PHASE_FIELD, REGION_FIELD]
    if STATUS_FIELD != "status":
        fields.append(STATUS_FIELD)
    if SLIDE1_APP_GROUPING == "custom_field":
        fields.append(SLIDE1_APP_FIELD)
    if SLIDE1_APP_GROUPING == "epic_name":
        fields.append("epic")
    if SLIDE1_APP_GROUPING == "label":
        fields.append("labels")
    if SLIDE1_APP_GROUPING == "component":
        fields.append("components")
    for f in INSTANCE_COUNT_FIELDS.values():
        if f and f != "customfield_XXXXX":
            fields.append(f)
    return ",".join(f for f in fields if f and f != "customfield_XXXXX")

def _subtask_extra_fields():
    """Fields to fetch on Sub-tasks (for Slide 3 + Appendix)."""
    fields = [PHASE_FIELD, REGION_FIELD, SLIDE3_APP_FIELD, APPENDIX_APP_FIELD]
    if STATUS_FIELD != "status":
        fields.append(STATUS_FIELD)
    if INSTANCE_TYPE_FIELD and INSTANCE_TYPE_FIELD != "customfield_XXXXX":
        fields.append(INSTANCE_TYPE_FIELD)
    if INSTANCE_NAME_FIELD and INSTANCE_NAME_FIELD != "summary":
        fields.append(INSTANCE_NAME_FIELD)
    if APP_ID_FIELD and APP_ID_FIELD != "customfield_XXXXX":
        fields.append(APP_ID_FIELD)
    return ",".join(f for f in fields if f and f != "customfield_XXXXX")



# ─────────────────────────────────────────────────────────────────────────────
# Milestone builder — groups Stories by parent summary
# ─────────────────────────────────────────────────────────────────────────────

def _build_milestones(issues, cfg):
    """
    Group a flat list of Stories by their parent issue's summary.
    Each unique parent summary → one milestone section.
    Each story under that parent → one task row.

    Returns:
        [{"name": parent_summary, "phase": ..., "status": ..., "tasks": [...]}, ...]
    """
    fields       = cfg.get("fields", {})
    status_field = fields.get("status_field", "status")
    phase_field  = fields.get("phase_field", PHASE_FIELD)

    group_map   = {}   # parent_summary -> list of task dicts
    group_order = []   # preserve encounter order

    for iss in issues:
        # Parent summary is in fields.parent.fields.summary (JIRA REST v3)
        parent_raw     = _field(iss, "parent") or {}
        parent_fields  = parent_raw.get("fields") or {}
        group_name     = parent_fields.get("summary") or parent_raw.get("summary") or "Unknown"

        if group_name not in group_map:
            group_map[group_name] = []
            group_order.append(group_name)

        # Resolve status
        if status_field == "status":
            raw_status = (_field(iss, "status") or {}).get("name", "")
        else:
            raw_status = _field_value(_field(iss, status_field))

        val_lower = raw_status.lower()
        canonical = "not_started"
        for key, values in STATUS_MAPPING.items():
            if any(v.lower() == val_lower for v in values):
                canonical = key
                break

        group_map[group_name].append({
            "key"   : iss.get("key", ""),
            "task"  : _field(iss, "summary") or "",
            "status": canonical,
            "phase" : _field_value(_field(iss, phase_field)) or "",
        })

    # Derive section-level status from tasks (any in_progress → in_progress, all done → completed)
    result = []
    for name in group_order:
        tasks   = group_map[name]
        t_statuses = [t["status"] for t in tasks]
        if all(s == "completed" for s in t_statuses):
            sec_status = "completed"
        elif any(s == "in_progress" for s in t_statuses):
            sec_status = "in_progress"
        else:
            sec_status = "not_started"
        result.append({
            "name"  : name,
            "phase" : tasks[0]["phase"] if tasks else "",
            "status": sec_status,
            "tasks" : tasks,
        })

    return result

def load_from_jira():
    """
    Fetch data from JIRA and return three separate datasets:

      slide1_apps   — Stories grouped by SLIDE1_APP_FIELD  → Slide 1 KPI + region table
      slide3_apps   — Sub-tasks grouped by SLIDE3_APP_FIELD → Slide 3 detail rows
      appendix_rows — Sub-tasks flat list with APPENDIX_APP_FIELD → Appendix table
      extra_sections — blockers / milestones raw issues
    """
    print("Connecting to JIRA...")

    # ── Fetch stories (Slide 1) ───────────────────────────────────────────────
    print(f"  Fetching stories:  {JQL_STORIES[:80]}...")
    stories = _fetch_all(JQL_STORIES, extra_fields=_story_extra_fields())
    print(f"  → {len(stories)} stories")

    # ── Fetch sub-tasks (Slide 3 + Appendix) ─────────────────────────────────
    subtasks = []
    if JQL_SUBTASKS:
        print(f"  Fetching subtasks: {JQL_SUBTASKS[:80]}...")
        subtasks = _fetch_all(JQL_SUBTASKS, extra_fields=_subtask_extra_fields())
        print(f"  → {len(subtasks)} subtasks")

    # ── Build Slide 1 apps — from Stories, grouped by SLIDE1_APP_FIELD ────────
    s1_dict = {}
    subtasks_by_parent = {}
    for st in subtasks:
        pk = ((_field(st, "parent") or {}).get("key") or "")
        if pk:
            subtasks_by_parent.setdefault(pk, []).append(st)

    for story in stories:
        app_name  = _get_slide1_app(story)
        story_key = story.get("key", "")

        if subtasks_by_parent:
            sts = subtasks_by_parent.get(story_key, [])
            prod_sts = [s for s in sts if _get_instance_type(s) == "prod"]
            np_sts   = [s for s in sts if _get_instance_type(s) == "non_prod"]
            counts = {
                "prod_done"      : sum(1 for s in prod_sts if _subtask_done(s)),
                "prod_total"     : len(prod_sts),
                "non_prod_done"  : sum(1 for s in np_sts  if _subtask_done(s)),
                "non_prod_total" : len(np_sts),
            }
        else:
            counts = _instance_counts_from_fields(story)

        s1_dict.setdefault(app_name, []).append({
            "key"    : story_key,
            "summary": _field(story, "summary") or "",
            "phase"  : _get_phase(story),
            "status" : _map_status(story),
            "region" : _get_region(story),
            **counts,
        })

    slide1_apps = [{"name": n, "instances": i}
                   for n, i in sorted(s1_dict.items())]
    print(f"  → {len(slide1_apps)} Slide 1 applications (from stories)")

    # Lookup: story_key → canonical status (for Slide 3 instance status)
    story_status_by_key = {
        story.get("key", ""): _map_status(story)
        for story in stories
    }

    # ── Build Slide 3 apps — from Sub-tasks, grouped by SLIDE3_APP_FIELD ──────
    s3_dict = {}
    for st in subtasks:
        app_name  = _get_slide3_app(st)
        st_key    = st.get("key", "")
        env_type  = _get_instance_type(st)
        done      = _subtask_done(st)
        phase     = _get_phase(st)
        region    = _get_region(st)
        parent_key = ((_field(st, "parent") or {}).get("key") or st_key)

        # Each unique parent = one instance row inside the app
        inst_map = s3_dict.setdefault(app_name, {})
        if parent_key not in inst_map:
            # Use parent story's status — sub-task statuses are just workflow steps
            inst_status = story_status_by_key.get(parent_key, _map_status(st))
            inst_map[parent_key] = {
                "key"          : parent_key,
                "summary"      : (_field(st, "summary") or ""),
                "instance_name": _get_instance_name(st),
                "app_id"       : _get_app_id(st),
                "phase"        : phase,
                "status"       : inst_status,
                "region"       : region,
                "prod_done": 0, "prod_total": 0,
                "non_prod_done": 0, "non_prod_total": 0,
                "subtasks": [],
            }
        inst = inst_map[parent_key]
        if env_type == "prod":
            inst["prod_total"] += 1
            if done: inst["prod_done"] += 1
        else:
            inst["non_prod_total"] += 1
            if done: inst["non_prod_done"] += 1
        inst["subtasks"].append({
            "key"   : st_key,
            "name"  : _field(st, "summary") or "",
            "env"   : "Prod" if env_type == "prod" else "Non-Prod",
            "status": (_field(st, "status") or {}).get("name", ""),
            "done"  : done,
        })

    slide3_apps = [
        {"name": app, "instances": list(inst_map.values())}
        for app, inst_map in sorted(s3_dict.items())
    ]
    print(f"  → {len(slide3_apps)} Slide 3 applications (from sub-tasks)")

    # ── Build Appendix rows — flat list from Sub-tasks ─────────────────────────
    appendix_rows = []
    for st in subtasks:
        env_type  = _get_instance_type(st)
        done      = _subtask_done(st)
        raw_st    = (_field(st, "status") or {}).get("name", "")
        canonical = "completed" if done else _map_status(st)
        appendix_rows.append({
            "app_name" : _get_appendix_app(st),
            "inst_name": _get_instance_name(st),
            "app_id"   : _get_app_id(st),
            "phase"    : _get_phase(st),
            "env"      : "Prod" if env_type == "prod" else "Non-Prod",
            "sub_key"  : st.get("key", ""),
            "sub_name" : _field(st, "summary") or "",
            "status"   : canonical,
        })
    print(f"  → {len(appendix_rows)} Appendix rows (from sub-tasks)")

    # ── Fetch extra sections ──────────────────────────────────────────────────
    extra_sections = {}
    for section_key, cfg in EXTRA_SECTIONS.items():
        jql = cfg.get("jql", "")
        if jql:
            print(f"  Fetching {section_key}: {jql[:60]}...")
            issues = _fetch_all(jql)
            print(f"  → {len(issues)} issues")
            if section_key == "milestones":
                extra_sections[section_key] = _build_milestones(issues, cfg)
            else:
                extra_sections[section_key] = issues
        else:
            extra_sections[section_key] = []

    print("JIRA data loaded.\n")
    return {
        "slide1_apps"   : slide1_apps,
        "slide3_apps"   : slide3_apps,
        "appendix_rows" : appendix_rows,
        "extra_sections": extra_sections,
    }
