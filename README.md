# SSPM PPT Generator

Generates a PowerPoint status deck from JIRA data (or a local mock dataset).

---

## Files

| File | Purpose | Edit? |
|---|---|---|
| `config.py` | **All settings** — JIRA connection, JQL, field mappings, status labels | ✅ Yes — main config |
| `data.py` | Mock/manual data used when `USE_JIRA = False` | ✅ Yes — for testing |
| `generator.py` | Builds the PowerPoint slides | ❌ Do not edit |
| `jira_loader.py` | Fetches and transforms live JIRA data | ❌ Do not edit |
| `find_jira_fields.py` | Discovers JIRA custom field keys (run once) | ❌ Just run it |

---

## Quick Start

```bash
pip install python-pptx requests
python generator.py          # produces SSPM_Status.pptx
```

---

## config.py — Section by Section

### Section 1 — Output filename

```python
OUTPUT_FILE = "SSPM_Status.pptx"
```

---

### Section 2 — JIRA connection

```python
USE_JIRA       = False                             # True = live JIRA, False = data.py mock
JIRA_BASE_URL  = "https://yourcompany.atlassian.net"
JIRA_EMAIL     = "you@yourcompany.com"
JIRA_API_TOKEN = "YOUR_API_TOKEN_HERE"
```

Get an API token: **https://id.atlassian.com → Security → API tokens → Create**

---

### Section 3 — Two JQL queries

```python
JQL_STORIES  = 'project = "SSPM" AND issuetype = Story ORDER BY created ASC'
JQL_SUBTASKS = 'project = "SSPM" AND issuetype = Sub-task ORDER BY created ASC'
```

- **JQL_STORIES** — one Story = one SaaS instance (e.g. Salesforce APAC Prod).
  Stories with the same application name are grouped together.
- **JQL_SUBTASKS** — each sub-task under a story = one Prod or Non-Prod environment.

JQL may contain spaces — that is normal.
JIRA field names that have spaces must be quoted **inside** the JQL string:

```
"Epic Link" = SSPM-10          ✅  field name with space — quoted inside JQL
project = "MY PROJECT"         ✅  project name with space — quoted inside JQL
customfield_10042 = "Phase 1"  ✅  values with spaces are fine
```

---

### Section 4 — Application grouping

Controls how stories are grouped into one application block (e.g. all Salesforce stories → one Salesforce row).

```python
APPLICATION_GROUPING = "epic_name"   # recommended
```

| Option | Behaviour |
|--------|-----------|
| `"epic_name"` | Group by the Epic the story belongs to |
| `"custom_field"` | Group by a custom field (set `APPLICATION_FIELD = "customfield_XXXXX"`) |
| `"label"` | Group by the first JIRA label |
| `"component"` | Group by the first JIRA component |
| `"summary_prefix"` | Split story summary on `APPLICATION_SUMMARY_SEPARATOR` (e.g. `" - "`) |

---

### Section 5 — Phase identification

```python
PHASE_FIELD  = "customfield_XXXXX"     # field KEY from find_jira_fields.py
PHASE_VALUES = ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5"]
```

Run `python find_jira_fields.py SSPM-001` to find the correct field key.

---

### Section 6 — Project status field

```python
STATUS_FIELD = "status"    # built-in JIRA status, OR "customfield_XXXXX"
```

Raw JIRA values are mapped to one of 5 internal statuses via `STATUS_MAPPING` (Section 10b below).

---

### Section 7 — Region field

```python
REGION_FIELD = "customfield_XXXXX"
REGIONS      = ["APAC", "EMEA", "Global", "Japan", "North America", "TG"]
```

---

### Section 8 — Prod vs Non-Prod (from sub-tasks)

```python
INSTANCE_TYPE_FIELD   = "customfield_XXXXX"    # field on each sub-task
INSTANCE_TYPE_MAPPING = {
    "prod":     ["Production", "Prod", "PRD"],
    "non_prod": ["Non-Production", "Non-Prod", "UAT", "Staging", "Dev"],
}
```

If the field is absent, set `INSTANCE_TYPE_FROM_SUMMARY = True` to infer type from keywords in the sub-task title.

---

### Section 10b — Status mapping *(most commonly edited)*

This is the 4-step pipeline that converts raw JIRA dropdown text into what appears in the deck.

#### Step 2 — STATUS_MAPPING: Map raw JIRA value → internal key

Add every exact dropdown value your JIRA project uses. Matching is **case-insensitive**.
The 5 internal key names on the left are fixed — only edit the lists on the right.

```python
STATUS_MAPPING = {
    "completed":      ["Completed", "Done", "Closed"],
    "de_scoped":      ["De-Scoped", "Cancelled", "Won't Do"],
    "future_request": [
        "Future Request",
        "Future Request - Integration Not currently Supported",  # long JIRA value — add as-is
    ],
    "not_started":    ["Not Started", "To Do", "Backlog", "Open"],
    "in_progress":    [
        "Onboarding In Progress",    # exact JIRA dropdown text
        "In Progress", "In Development",
    ],
}
```

#### Step 3 — STATUS_LABELS: PPT pill labels (shown on detail slides)

Edit the right-hand values. These appear inside status pills on slides 3+.
**Keep ≤ 20 characters** — pills are narrow.

```python
STATUS_LABELS = {
    "completed":      "Completed",
    "de_scoped":      "De-Scoped",
    "future_request": "Future Request",
    "not_started":    "Not Started",
    "in_progress":    "In Progress",      # short label, not the full JIRA string
}
```

#### Step 4 — STATUS_SHORT: KPI bar chip labels (Slide 1)

These appear in the tiny chip row under the colour bar on Slide 1.
**Must be ≤ 8 characters** to avoid overlap.

```python
STATUS_SHORT = {
    "completed":      "Done",
    "de_scoped":      "D-Scoped",
    "future_request": "Future",
    "not_started":    "Not Strt",
    "in_progress":    "In Prog",
}
```

---

### Section 9 — Blockers slide JQL

```python
EXTRA_SECTIONS = {
    "blockers": {
        "jql": 'project = SSPM AND labels = "blocker" ORDER BY priority DESC',
        # Other options:
        # '"Epic Link" = SSPM-99 ORDER BY created ASC'
        # 'project = SSPM AND issuetype = "Impediment"'
        # 'project = SSPM AND "Blocker Flag" = Yes'
        ...
    },
```

Set `jql = ""` to skip the Blockers slide entirely.

Also set the field keys for impact and phase on each blocker issue:

```python
        "fields": {
            "owner_field":  "assignee",           # built-in — keep as-is
            "impact_field": "customfield_XXXXX",  # High / Med / Low dropdown field
            "phase_field":  "customfield_XXXXX",  # same key as PHASE_FIELD
        },
```

---

### Section 9 — Milestones slide JQL

```python
    "milestones": {
        "jql": '"Epic Link" = SSPM-20 ORDER BY key ASC',
        # Other options:
        # 'project = SSPM AND labels = "milestone" ORDER BY duedate ASC'
        # 'project = SSPM AND issuetype = Epic ORDER BY created ASC'
        ...
    },
```

- Each issue returned becomes **one milestone section** header.
- Its sub-tasks automatically become the **task rows** below.
- Task count is **fully dynamic** — 5 tasks or 50 tasks, the slide auto-paginates.
- Set `jql = ""` to skip the Milestones slide.

Also set the field keys for phase, target date, and status:

```python
        "fields": {
            "phase_field":  "customfield_XXXXX",  # same key as PHASE_FIELD
            "target_field": "customfield_XXXXX",  # target date or sprint field
            "status_field": "status",             # or a custom field key
        },
```

---

### Section 11 — Detail slide scope

```python
IN_SCOPE_PHASES       = ["Phase 1", "Phase 2"]  # phases that get full detail slides
ROWS_PER_DETAIL_SLIDE = 6                        # apps per page (6–10 recommended)
```

---

## Slide structure

| Slide | Content |
|-------|---------|
| 1 | Summary dashboard — phase KPI cards + instance onboarding table |
| 2 | Region-wise summary table |
| 3…N | Phase 1 detail — auto-paginated at `ROWS_PER_DETAIL_SLIDE` apps/page |
| N+1…M | Phase 2 detail — auto-paginated |
| M+1 | Blockers & Impediments |
| M+2 | Milestones & Roadmap |

Each detail slide shows per-application:
- **3 mini-boxes**: ×instances (total orgs) / ×Prod / ×Non-Prod counts
- **Status pill**: Completed+De-Scoped → green "Completed"; others show their own label
- **PROD done/total** and **NP done/total** progress pills

---

## Field key discovery

```bash
python find_jira_fields.py SSPM-001
```

Output:

```
FIELD KEY (paste into config.py)     DISPLAY NAME         CURRENT VALUE
customfield_10042                    Phase Name           Phase 1   ◄ HAS VALUE
customfield_10085                    Region               APAC      ◄ HAS VALUE
customfield_10091                    Integration Status   Onboarding In Progress  ◄ HAS VALUE
```

Copy the **FIELD KEY** (left column) into `config.py`. Never paste the display name as a key.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: pptx` | `pip install python-pptx` |
| `401 Unauthorized` from JIRA | Check `JIRA_EMAIL` and `JIRA_API_TOKEN` in config.py |
| `404 Not Found` from JIRA | Check `JIRA_BASE_URL` and issue key in `find_jira_fields.py` |
| Status always shows "Not Started" | Add the exact JIRA dropdown text to `STATUS_MAPPING` |
| Text overlapping in pills | Shorten `STATUS_LABELS` values; shorten `STATUS_SHORT` to ≤ 8 chars |
| Too many detail slides | Increase `ROWS_PER_DETAIL_SLIDE` in config.py |
| Custom field always 0 | Re-run `find_jira_fields.py` and verify the field key |
