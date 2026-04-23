# =============================================================================
# find_jira_fields.py  —  JIRA Field Discovery Tool
# =============================================================================
# Run this ONCE to find the internal field KEYS for your JIRA instance.
#
# Usage:
#   python find_jira_fields.py SSPM-001
#
# Output explains:
#   LEFT column  = FIELD KEY  →  paste this into config.py
#   RIGHT column = display name / current value  →  for reference only
#
# SPACES NOTE:
#   Field display names often have spaces (e.g. "Prod Instances Done").
#   Field KEYS never have spaces (e.g. "customfield_10042").
#   Always use the KEY (left column) in config.py — never the display name.
# =============================================================================

import sys
import requests
from requests.auth import HTTPBasicAuth
from config import JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN

def main():
    if len(sys.argv) < 2:
        print("\nUsage:   python find_jira_fields.py <ISSUE-KEY>")
        print("Example: python find_jira_fields.py SSPM-001\n")
        sys.exit(1)

    issue_key = sys.argv[1]
    url  = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

    print(f"\nFetching fields for:  {issue_key}")
    resp = requests.get(url, auth=auth, headers={"Accept": "application/json"})

    if resp.status_code == 401:
        print("\n❌  Authentication failed.")
        print("    Check JIRA_EMAIL and JIRA_API_TOKEN in config.py\n")
        sys.exit(1)
    if resp.status_code == 404:
        print(f"\n❌  Issue '{issue_key}' not found.")
        print("    Check the issue key and JIRA_PROJECT in config.py\n")
        sys.exit(1)

    resp.raise_for_status()
    fields = resp.json().get("fields", {})

    # Also fetch field metadata to get display names
    meta_url = f"{JIRA_BASE_URL}/rest/api/3/field"
    meta_resp = requests.get(meta_url, auth=auth, headers={"Accept": "application/json"})
    display_names = {}
    if meta_resp.status_code == 200:
        for f in meta_resp.json():
            display_names[f["id"]] = f.get("name", "")

    print("\n" + "=" * 80)
    print(f"  Issue: {issue_key}  —  {fields.get('summary', '')}")
    print("=" * 80)
    print()
    print("  HOW TO READ THIS OUTPUT:")
    print("  ┌─────────────────────────────────────┬──────────────────────────────────────┐")
    print("  │  FIELD KEY  (paste into config.py)  │  DISPLAY NAME / CURRENT VALUE        │")
    print("  │  ← Use this — no spaces, always     │  ← For reference only, do NOT paste  │")
    print("  └─────────────────────────────────────┴──────────────────────────────────────┘")
    print()
    print(f"  {'FIELD KEY':<38}  {'DISPLAY NAME':<28}  CURRENT VALUE")
    print("  " + "-" * 78)

    # Separate built-in vs custom fields
    builtins  = {k: v for k, v in fields.items() if not k.startswith("customfield_")}
    customs   = {k: v for k, v in fields.items() if k.startswith("customfield_")}

    def fmt_value(v):
        if isinstance(v, dict):  return v.get("name") or v.get("value") or v.get("key") or str(v)[:40]
        if isinstance(v, list):  return f"[{len(v)} items]"
        if v is None:            return "(empty)"
        return str(v)[:40]

    print("\n  ── Built-in JIRA fields (no spaces in key — always safe) ──")
    for key in sorted(builtins):
        dn  = display_names.get(key, "")
        val = fmt_value(fields[key])
        print(f"  {key:<38}  {dn:<28}  {val}")

    print("\n  ── Custom fields (use the KEY — ignore the display name) ──")
    for key in sorted(customs):
        dn  = display_names.get(key, "")
        val = fmt_value(fields[key])
        # Highlight non-empty custom fields
        marker = "  ◄ HAS VALUE" if fields[key] is not None and fields[key] != [] else ""
        print(f"  {key:<38}  {dn:<28}  {val}{marker}")

    print()
    print("=" * 80)
    print("  NEXT STEPS:")
    print()
    print("  1. Find rows marked '◄ HAS VALUE' — these are the fields in use")
    print("  2. Match the DISPLAY NAME to its purpose (Prod Done, NP Total etc.)")
    print("  3. Copy the FIELD KEY from the left column (e.g. customfield_10042)")
    print("  4. Paste the FIELD KEY into config.py for the relevant setting:")
    print()
    print("     PHASE_FIELD        → field that holds Phase 1 / Phase 2 etc.")
    print("     STATUS_FIELD       → field that holds integration status")
    print("     REGION_FIELD       → field that holds region (APAC, EMEA …)")
    print("     INSTANCE_TYPE_FIELD→ field on Sub-task that says Prod / Non-Prod")
    print("     APPLICATION_FIELD  → field that identifies the application name")
    print("     INSTANCE_COUNT_FIELDS → prod_done / prod_total / np_done / np_total")
    print()
    print("  SPACES REMINDER:")
    print("  ✅  customfield_10042          → correct — use this in config.py")
    print("  ❌  'Phase Name'               → display name — do NOT use in config.py")
    print("  ✅  'Phase 1' as a VALUE       → fine, spaces OK in STATUS_MAPPING values")
    print("  ✅  'In Progress' as a VALUE   → fine, spaces OK in STATUS_MAPPING values")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
