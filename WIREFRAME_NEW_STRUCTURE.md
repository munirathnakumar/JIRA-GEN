# SSPM PPT Generator — New Summary Deck Wireframe

## Current Project Overview
**Purpose:** Automatically generate PowerPoint decks to track SSPM (SaaS Security Posture Management) integration status

**Current Scope:** Organized by Priority Tiers (P1, P2, P3, P4, P5)

---

## 🎯 REQUESTED NEW STRUCTURE

### Hierarchy Levels (Top-Down)
```
Phase (e.g., Phase 1, Phase 2, Phase 3)
  ↓
Application (Unique business application)
  ↓
SaaS Application (e.g., Salesforce, ServiceNow, etc.)
  ↓
Environment (Dev, Non-Prod, Prod, Staging, etc.)
```

---

## 📊 CURRENT SUMMARY DECK (SLIDE 1) LAYOUT

### Current KPI Strip
- **Grand Total Card**: All apps count
- **Per-Tier Cards** (P1, P2, P3, P4, P5): Count of apps per tier
- Metric: `done_apps / total_apps`

### Current Tier Table
Rows: P1, P2, P3, P4, P5  
Columns: Completed | Descoped | Future-Request | Not Started | In-Progress | Total

### Current Region Table
Rows: APAC, EMEA, Global, Japan, North America, TG  
Columns: Same as Tier Table

---

## 🆕 PROPOSED NEW SUMMARY DECK STRUCTURE

### NEW KPI Strip Layout
**Reorganized by PHASE + APPLICATION hierarchy:**

```
┌─────────────────────────────────────────────────────────────────┐
│ SSPM Initiative | Phase 1 Summary                    [Badge]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASE OVERVIEW                                                 │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐     │
│  │  Phase 1    │  Phase 2    │  Phase 3    │ Total       │     │
│  │  5 / 8      │  2 / 6      │  0 / 3      │ 7 / 17      │     │
│  │  Apps       │  Apps       │  Apps       │ Apps        │     │
│  └─────────────┴─────────────┴─────────────┴─────────────┘     │
│                                                                 │
│  BY APPLICATION (Phase 1 Detail)                                │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │ Salesforce   │ ServiceNow   │ Workday      │ Microsoft    │  │
│  │ 3/4 SaaS     │ 2/2 SaaS     │ 0/1 SaaS     │ 0/1 SaaS     │  │
│  │ 8/11 Envs    │ 3/5 Envs     │ 0/2 Envs     │ 0/1 Envs     │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
│                                                                 │
│  BY SAAS + ENVIRONMENT (Phase 1 Detail)                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ SaaS Name        | Prod  | Non-Prod | Dev   | Status    │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │ Salesforce (1)   | 1/1   | 1/2      | 1/1   | In-Prog   │  │
│  │ Salesforce (2)   | 1/1   | 1/1      | -     | Completed │  │
│  │ ServiceNow (1)   | 1/1   | 1/1      | 1/1   | Completed │  │
│  │ ServiceNow (2)   | 0/1   | 1/1      | -     | In-Prog   │  │
│  │ Workday (1)      | 0/1   | 0/1      | -     | Not Start │  │
│  │ Microsoft (1)    | 0/1   | -        | -     | Not Start │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
```

---

## 📋 DATA STRUCTURE DESIGN

### Option A: Phase-Centric (Recommended)
```python
PHASES = [
    {
        "name": "Phase 1",
        "color": "accent",
        "applications": [
            {
                "app_name": "Salesforce",
                "app_id": "app_001",
                "saas_instances": [
                    {
                        "saas_name": "Salesforce Production",
                        "saas_id": "sf_prod",
                        "environments": [
                            {"env": "Prod",     "done": True,  "total": 1},
                            {"env": "Non-Prod", "done": True,  "total": 2},
                            {"env": "Dev",      "done": True,  "total": 1},
                        ]
                    },
                    {
                        "saas_name": "Salesforce Test",
                        "saas_id": "sf_test",
                        "environments": [
                            {"env": "Prod",     "done": True,  "total": 1},
                            {"env": "Non-Prod", "done": True,  "total": 1},
                        ]
                    }
                ]
            },
            {
                "app_name": "ServiceNow",
                "app_id": "app_002",
                "saas_instances": [
                    {
                        "saas_name": "ServiceNow ITSM",
                        "saas_id": "snow_itsm",
                        "environments": [
                            {"env": "Prod",     "done": True,  "total": 1},
                            {"env": "Non-Prod", "done": True,  "total": 1},
                            {"env": "Dev",      "done": True,  "total": 1},
                        ]
                    }
                ]
            }
        ]
    },
    {
        "name": "Phase 2",
        "color": "purple",
        "applications": [...]
    }
]
```

---

## 🎨 NEW SLIDE 1 LAYOUT SECTIONS

### Section 1: Phase-Level KPI Strip
- **Cards per phase**: Count of fully-onboarded apps vs total
- **Visual**: Horizontal strip (5-phase max)
- **Metric**: `completed_apps / total_apps`

### Section 2: Application-Level Cards (For selected Phase)
- **Cards per application**: Count of fully-onboarded SaaS instances vs total
- **Visual**: Horizontal strip (4-8 apps, wrapping if needed)
- **Metric**: `completed_saas / total_saas_instances`

### Section 3: SaaS Environment Table (For selected Phase)
- **Rows**: Each SaaS instance per application
- **Columns**: Prod | Non-Prod | Dev | Staging | (other custom envs) | Status
- **Cells**: Completed / Total instances in that environment
- **Visual**: Color-coded status badge

### Section 4: Summary Stats (Bottom)
- **Overall metrics**:
  - Total apps in phase
  - Total SaaS instances
  - Total environments
  - Overall % completion

---

## 🔄 INTERACTION / TAB CONCEPT (Optional)

If user selects a phase (e.g., Phase 1):
- **Section 2** updates to show apps in Phase 1
- **Section 3** updates to show SaaS instances for Phase 1
- This gives a clear "drill-down" experience

---

## 📝 DATA INPUT CHANGES REQUIRED

### Current `data.py` Format
```python
APP_SUMMARY = [
    {"tier": "P1", "total_apps": 8, "done": 5, "pending": 3}
]
```

### NEW `data.py` Format
```python
PHASES = [
    {
        "name": "Phase 1",
        "applications": [
            {
                "app_name": "Salesforce",
                "saas_instances": [
                    {
                        "saas_name": "Salesforce Prod",
                        "environments": [
                            {"env": "Prod", "done": 1, "total": 1},
                            {"env": "Non-Prod", "done": 2, "total": 2}
                        ]
                    }
                ]
            }
        ]
    }
]

# Helper function to compute summary stats on-the-fly
def compute_phase_stats(phase):
    """Returns: total_apps, completed_apps, total_saas, completed_saas, etc."""
```

---

## 🎯 MIGRATION PATH

### Phase 0: Data Layer (Data Shapes)
1. ✅ Design new Phase → App → SaaS → Environment hierarchy
2. ✅ Create conversion functions (old tier-based → new phase-based)
3. ✅ Add helper functions to compute stats

### Phase 1: Summary Deck Redesign (This Request)
1. Update Slide 1 generator to display new structure
2. Add phase selector (if needed)
3. Add application-level KPI cards
4. Update SaaS environment table

### Phase 2: Detailed Slides (Future)
1. Update P1/P2 detailed slides to show SaaS instances
2. Add environment breakdown per slide

---

## ✅ NEXT STEPS (For Your Confirmation)

1. **Do you approve** the Phase → App → SaaS → Environment hierarchy?
2. **Is the Slide 1 layout** clear? Any adjustments?
3. **Should we support multiple environments** (Prod, Non-Prod, Dev, Staging, UAT, etc.)?
4. **How many applications per phase** (max)? Should we paginate?
5. **Do you want a phase-selector** in the deck or show all phases in Slide 1?

Once you confirm, I will:
- Update `data.py` structure
- Rewrite `generator.py` Slide 1 builder
- Update `jira_loader.py` to fetch & organize by phase/app/saas/env
- Test the PPT generation
