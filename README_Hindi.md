# SSPM PPT Generator — उपयोग निर्देश (Hindi / Hinglish)

यह tool automatically एक PowerPoint deck बनाता है जो SSPM (SaaS Security Posture Management)
integration की status दिखाता है।  
Data manually `data.py` में भरें, या JIRA से live fetch करें।

---

## फ़ाइलें और उनका काम

| फ़ाइल | क्या करती है | Edit करें? |
|---|---|---|
| `config.py` | Settings: output filename, JIRA connection, colours | ✅ हाँ — main config |
| `data.py` | Slide का सारा content जब JIRA नहीं use हो रहा | ✅ हाँ — हर presentation से पहले update करें |
| `generator.py` | Slides build करती है | ❌ नहीं |
| `jira_loader.py` | JIRA से data fetch करती है | ❌ नहीं |
| `find_jira_fields.py` | JIRA के custom field names ढूंढने का tool | ❌ बस एक बार run करें |

---

## Slides का Structure

| Slide | Title | Content |
|---|---|---|
| 1 | Summary Dashboard | Stat bar + Tier table (P1–P5) + Region table |
| 2 | P1 Applications | 8 apps की detailed integration status |
| 3 | P2 Applications | 14 apps का compact grid |
| 4 | Milestones | Out-of-scope tiers + Phase 2/3 roadmap |
| 5 | Blockers | P1 blockers + Milestone blockers अलग slide पर |
| 6 | Score Improvement | 8 panes — हर P1 app का 3-month score trend |

---

## Quick Start — Manual Data (JIRA के बिना)

### Step 1 — Library install करें

```bash
pip install python-pptx
```

### Step 2 — `data.py` update करें

`data.py` खोलें और अपने actual numbers fill करें:

- **`SUMMARY_STATS`** — Top stat cards (Total Apps, Prod Onboarded, Blockers etc.)
- **`TIER_TABLE`** — P1 से P5 तक हर tier का Completed/Descoped/Not Started count
- **`REGION_TABLE`** — APAC, EMEA, Global, Japan, North America, TG का count
- **`P1_APPS`** — हर P1 app के instances (Prod/Non-Prod, done/pending)
- **`P1_BLOCKERS`** — P1 के blockers
- **`P2_APPS`** — हर P2 app का prod/np count
- **`S3_BLOCKERS`** — Cross-phase blockers

### Step 3 — Run करें

```bash
python generator.py
```

Output: `SSPM_Status_Light.pptx` उसी folder में बन जाएगी।

### Step 4 — Score Improvement Slide (Slide 6)

Slide 6 में 8 panes हैं — हर pane में "Paste screenshot" लिखा है।  
PowerPoint में खोलकर हर pane में अपना screenshot paste करें:
1. PowerPoint में Slide 6 खोलें
2. सही pane select करें
3. अपना score trend screenshot `Ctrl+V` से paste करें
4. Size adjust करें

---

## JIRA Integration

### Step 1 — API Token बनाएं

1. https://id.atlassian.com पर जाएं
2. **Security → API tokens → Create API token** click करें
3. Token copy करें (यह सिर्फ एक बार दिखता है)

### Step 2 — `config.py` fill करें

```python
USE_JIRA       = True
JIRA_BASE_URL  = "https://yourcompany.atlassian.net"
JIRA_EMAIL     = "aap@company.com"
JIRA_API_TOKEN = "yahan-token-paste-karein"
JIRA_PROJECT   = "SSPM"
```

### Step 3 — Field names ढूंढें

```bash
python find_jira_fields.py SSPM-001
```

SSPM-001 की जगह अपना कोई real JIRA issue key डालें।  
Output में `◄ CUSTOM` वाले fields आपके custom fields हैं।

### Step 4 — `config.py` में field mapping करें

```python
# Tier कैसे identify होगा
TIER_SOURCE = "priority"   # या "customfield_XXXXX" या "epic"

# Prod vs Non-Prod कैसे identify होगा
INSTANCE_SOURCE = "custom_fields"
INSTANCE_FIELDS = {
    "prod_done"  : "customfield_10042",   # Prod onboarded instances
    "prod_total" : "customfield_10043",   # Total Prod instances
    "np_done"    : "customfield_10044",   # Non-Prod onboarded
    "np_total"   : "customfield_10045",   # Total Non-Prod (0 = कोई NP नहीं)
}

# हर slide section के लिए Epic ID
EPIC_IDS = {
    "p1_apps"     : "SSPM-10",   # P1 onboarding stories
    "p2_apps"     : "SSPM-11",   # P2 onboarding stories
    "p1_blockers" : "SSPM-12",   # P1 blocker tickets
    "s3_blockers" : "SSPM-13",   # Phase 2/3 blockers
    "milestones"  : "SSPM-14",   # Phase tasks
}

# Region कैसे identify होगा
REGION_SOURCE = "custom_field"
REGION_FIELD  = "customfield_10046"
```

### Step 5 — Run करें

```bash
python generator.py
```

---

## Data Update कैसे करें (Manual Mode)

### नया P1 app add करना

`data.py` में `P1_APPS` list में add करें:

```python
{"name": "A9", "instances": [
    {"env": "Prod",     "done": True },
    {"env": "Non-Prod", "done": False},
]},
```

### Instance को Completed mark करना

`"done": False`  को  `"done": True`  कर दें।

### Blocker add करना

```python
{"id": "B4", "text": "App XYZ — issue description", "owner": "Team Name", "impact": "High"},
```

### Stat card update करना

`SUMMARY_STATS` में numbers बदलें — slide automatically update हो जाएगी।

---

## Org Footer Add करना

हर slide के bottom पर `[ Add your org footer here ]` placeholder है।  
इसे हटाने के लिए `generator.py` में यह line ढूंढें:

```python
def org_footer_space(slide):
```

उस function में last `add_text(...)` line comment out या delete कर दें।  
फिर PowerPoint में footer manually add करें, या generator में अपना text set करें।

---

## Common Errors और Solution

| Error | Solution |
|---|---|
| `ModuleNotFoundError: pptx` | `pip install python-pptx` run करें |
| `401 Unauthorized` | JIRA_EMAIL और JIRA_API_TOKEN check करें |
| `404 Not Found` | JIRA_PROJECT और JIRA_BASE_URL check करें |
| Custom field 0 दिखा रहा है | `find_jira_fields.py` से सही field ID confirm करें |
| Slide same दिख रही है | `data.py` save किया? फिर run करें |

---

## हर हफ्ते का workflow

```
हर Monday / Presentation से पहले:
  1. data.py खोलें → numbers update करें → save करें
  2. python generator.py run करें
  3. SSPM_Status_Light.pptx खुलेगी → Slide 6 में screenshots paste करें
  4. Present करें ✅
```
