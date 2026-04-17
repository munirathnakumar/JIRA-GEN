# SSPM PPT Generator

Automatically generates a 3-slide PowerPoint deck showing SSPM integration
status across P1 and P2 applications. Data can be entered manually or pulled
live from JIRA.

---

## Files in this folder

| File | Purpose | Edit? |
|---|---|---|
| `config.py` | Settings: output filename, JIRA connection, colours | ✅ Yes — your main config |
| `data.py` | Slide content when not using JIRA | ✅ Yes — update before each presentation |
| `generator.py` | Builds the PowerPoint slides | ❌ No — do not edit |
| `jira_loader.py` | Fetches and transforms JIRA data | ❌ No — do not edit |
| `find_jira_fields.py` | Tool to discover your JIRA custom field names | ❌ No — just run it once |

---

## Quick Start (Manual Data — No JIRA)

### Step 1 — Install Python dependency

```bash
pip install python-pptx
```

### Step 2 — Update your data

Open `data.py` and edit the app lists and blockers to reflect current status.
Each section has comments explaining exactly what to fill in.

### Step 3 — Run the generator

```bash
python generator.py
```

This creates `SSPM_Status_Light.pptx` in the same folder.

---

## JIRA Integration

Follow these steps once to wire the generator to your JIRA project.
After setup, every run will automatically pull live data.

### Step 1 — Get a JIRA API token

1. Go to: https://id.atlassian.com
2. Click **Security** → **Create and manage API tokens**
3. Click **Create API token**, give it a name (e.g. "SSPM PPT Generator")
4. Copy the token — you will only see it once

### Step 2 — Update config.py

Open `config.py` and fill in:

```python
USE_JIRA       = True                           # Switch on JIRA mode
JIRA_BASE_URL  = "https://yourcompany.atlassian.net"
JIRA_EMAIL     = "you@yourcompany.com"
JIRA_API_TOKEN = "paste-your-token-here"
JIRA_PROJECT   = "SSPM"                         # Your project key
```

### Step 3 — Discover your custom field names

Your JIRA instance uses auto-generated IDs for custom fields
(e.g. `customfield_10045`). Run this once to find them:

```bash
python find_jira_fields.py SSPM-001
```

Replace `SSPM-001` with any real issue key from your project.

This prints every field on that issue. Look for the ones marked `◄ CUSTOM`
and match them to their meaning (Prod instances completed, Non-Prod total etc.).

Example output:

```
FIELD KEY                           VALUE
----------------------------------------------------------------------
  customfield_10042                 3              ◄ CUSTOM
  customfield_10043                 5              ◄ CUSTOM
  customfield_10044                 Yes            ◄ CUSTOM
  customfield_10045                 High           ◄ CUSTOM
  priority                          Highest
  status                            In Progress
```

### Step 4 — Map fields in config.py

Update the `JIRA_FIELDS` section in `config.py` with the field names you found:

```python
JIRA_FIELDS = {
    "priority"              : "tier",
    "status"                : "onboard_status",
    "customfield_10042"     : "prod_done",      # No. of Prod instances completed
    "customfield_10043"     : "prod_total",     # Total Prod instances
    "customfield_10044"     : "is_blocker",     # "Yes" / "No"
    "customfield_10045"     : "impact",         # "High" / "Med" / "Low"
    # add np_done, np_total, owner, phase similarly
}
```

### Step 5 — Run

```bash
python generator.py
```

The generator will print what it fetches and then save the deck.

---

## What JIRA provides vs what stays in data.py

Even with JIRA enabled, two things always come from `data.py`:

| Item | Why it stays manual |
|---|---|
| `TIER_SUMMARY` (P3/P4/P5 table) | These tiers are out of scope — no JIRA tickets yet |
| `MILESTONES` (Phase 2, Phase 3 tasks) | Editorial content, not tracked per ticket |

Everything else — P1 apps, P2 apps, and blockers — comes from JIRA.

---

## Updating data manually (no JIRA)

Make sure `USE_JIRA = False` in `config.py`, then edit `data.py`:

**To add a new P1 app:**
```python
{"name": "A9", "instances": [
    {"env": "Prod",     "done": True },
    {"env": "Non-Prod", "done": False},
]},
```

**To mark an instance as completed:**
Change `"done": False` to `"done": True`.

**To add a blocker:**
```python
{"id": "B4", "text": "Description of blocker", "owner": "Team Name", "impact": "High"},
```

**To update a milestone task status:**
Change `"status"` to `"Completed"`, `"In Progress"`, or `"Not Started"`.

---

## Changing the output filename

In `config.py`:
```python
OUTPUT_FILE = "SSPM_Weekly_Update.pptx"
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: pptx` | Run `pip install python-pptx` |
| `401 Unauthorized` from JIRA | Check `JIRA_EMAIL` and `JIRA_API_TOKEN` in config.py |
| `404 Not Found` from JIRA | Check `JIRA_PROJECT` and `JIRA_BASE_URL` in config.py |
| Custom field always shows 0 | Run `find_jira_fields.py` and re-check the field name |
| Deck looks the same after editing | Make sure you saved `data.py` before running |
