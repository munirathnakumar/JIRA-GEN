# =============================================================================
# test_jira_connection.py  —  Diagnose JIRA API connectivity
# =============================================================================
# Run:  python test_jira_connection.py
# =============================================================================

import json
import requests
from requests.auth import HTTPBasicAuth
from config import JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JQL_STORIES

auth    = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers_get  = {"Accept": "application/json"}
headers_post = {"Accept": "application/json", "Content-Type": "application/json"}

SEP = "=" * 60

def ok(msg):  print(f"  ✅  {msg}")
def err(msg): print(f"  ❌  {msg}")
def info(msg):print(f"  ℹ️   {msg}")

print(f"\n{SEP}")
print("  JIRA Connection Diagnostic")
print(SEP)
info(f"Base URL : {JIRA_BASE_URL}")
info(f"Email    : {JIRA_EMAIL}")
info(f"Token    : {'*' * 8}{JIRA_API_TOKEN[-4:] if len(JIRA_API_TOKEN) > 4 else '****'}")
print()

# ── Step 1: Basic auth check ─────────────────────────────────────────────────
print("Step 1 — Auth check (GET /rest/api/3/myself)")
try:
    r = requests.get(f"{JIRA_BASE_URL}/rest/api/3/myself",
                     headers=headers_get, auth=auth)
    if r.status_code == 200:
        name = r.json().get("displayName", "?")
        ok(f"Authenticated as: {name}")
    elif r.status_code == 401:
        err("401 Unauthorised — check JIRA_EMAIL and JIRA_API_TOKEN in config.py")
        print(f"  Response: {r.text[:200]}")
        raise SystemExit(1)
    else:
        err(f"Unexpected status {r.status_code}")
        print(f"  Response: {r.text[:200]}")
        raise SystemExit(1)
except requests.exceptions.ConnectionError as e:
    err(f"Cannot connect to {JIRA_BASE_URL}")
    err(f"Check JIRA_BASE_URL in config.py ({e})")
    raise SystemExit(1)

# ── Step 2: POST search/jql with minimal body ────────────────────────────────
print("\nStep 2 — POST /rest/api/3/search/jql (minimal body)")
url  = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
body = {"jql": "ORDER BY created DESC", "maxResults": 1}
r = requests.post(url, headers=headers_post, auth=auth, json=body)
print(f"  Status : {r.status_code}")
if r.ok:
    ok(f"Search endpoint works — total issues: {r.json().get('total','?')}")
else:
    err(f"Failed — raw response:")
    print(f"  {r.text[:600]}")

# ── Step 3: POST search/jql with fields array ────────────────────────────────
print("\nStep 3 — POST /rest/api/3/search/jql (with fields array)")
body = {
    "jql"       : "ORDER BY created DESC",
    "maxResults": 1,
    "fields"    : ["summary", "status", "assignee"],
}
r = requests.post(url, headers=headers_post, auth=auth, json=body)
print(f"  Status : {r.status_code}")
if r.ok:
    ok("fields array accepted")
    issues = r.json().get("issues", [])
    if issues:
        ok(f"Sample issue: {issues[0].get('key')} — {(issues[0].get('fields') or {}).get('summary','')[:50]}")
else:
    err("Failed with fields array")
    print(f"  {r.text[:600]}")

# ── Step 4: JQL_STORIES from config ─────────────────────────────────────────
print(f"\nStep 4 — Your JQL_STORIES query")
info(f"JQL: {JQL_STORIES[:80]}")
body = {"jql": JQL_STORIES, "maxResults": 1, "fields": ["summary", "status"]}
r = requests.post(url, headers=headers_post, auth=auth, json=body)
print(f"  Status : {r.status_code}")
if r.ok:
    total = r.json().get("total", 0)
    ok(f"Query valid — {total} issues match")
else:
    err("JQL query rejected")
    print(f"  {r.text[:600]}")

print(f"\n{SEP}\n")
