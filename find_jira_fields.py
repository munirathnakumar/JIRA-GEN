# =============================================================================
# find_jira_fields.py  —  JIRA Field Discovery Tool
# =============================================================================
# Run this ONCE to find the internal names of your custom fields.
# It prints every field available on a sample JIRA issue so you can
# copy the correct names into config.py → JIRA_FIELDS.
#
# Usage:
#   python find_jira_fields.py SSPM-001
#
# Replace SSPM-001 with any real issue key from your project.
# =============================================================================

import sys
import json
import requests
from requests.auth import HTTPBasicAuth
from config import JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN

def main():
    if len(sys.argv) < 2:
        print("Usage: python find_jira_fields.py <ISSUE-KEY>")
        print("Example: python find_jira_fields.py SSPM-001")
        sys.exit(1)

    issue_key = sys.argv[1]
    url  = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

    print(f"\nFetching fields for issue: {issue_key}")
    print(f"URL: {url}\n")

    resp = requests.get(url, auth=auth, headers={"Accept": "application/json"})

    if resp.status_code == 401:
        print("ERROR: Authentication failed. Check JIRA_EMAIL and JIRA_API_TOKEN in config.py")
        sys.exit(1)
    elif resp.status_code == 404:
        print(f"ERROR: Issue '{issue_key}' not found. Check the issue key and JIRA_PROJECT in config.py")
        sys.exit(1)

    resp.raise_for_status()
    data   = resp.json()
    fields = data.get("fields", {})

    print("=" * 70)
    print(f"  Issue: {issue_key}  —  {fields.get('summary', '')}")
    print("=" * 70)
    print(f"\n{'FIELD KEY':<35} {'VALUE'}")
    print("-" * 70)

    for key, value in sorted(fields.items()):
        # Format the value for display
        if isinstance(value, dict):
            display = value.get("name") or value.get("value") or str(value)[:60]
        elif isinstance(value, list):
            display = f"[list of {len(value)} items]"
        elif value is None:
            display = "(empty)"
        else:
            display = str(value)[:60]

        # Highlight custom fields
        marker = "  ◄ CUSTOM" if key.startswith("customfield_") else ""
        print(f"  {key:<33} {display}{marker}")

    print("\n" + "=" * 70)
    print("  NEXT STEPS:")
    print("  1. Find rows labelled '◄ CUSTOM' above")
    print("  2. Match each one to its meaning (Prod instances, NP instances, Blocker flag etc.)")
    print("  3. Copy the field key (e.g. customfield_10045) into config.py → JIRA_FIELDS")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
