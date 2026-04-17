# =============================================================================
# generator.py  —  SSPM PPT Slide Builder  (do not edit)
# =============================================================================
# Slides produced:
#   1 — Summary Dashboard  (stat bar + Tier table + Region table)
#   2 — P1 Applications    (detailed rows, NO blockers)
#   3 — P2 Applications    (4-col grid,   NO blockers)
#   4 — Milestones & Out-of-Scope overview (NO blockers)
#   5 — Blockers           (dedicated slide)
#   6 — P1 Score Improvement (8-pane screenshot layout)
# =============================================================================

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

import config
import data as manual_data

# ── Palette ───────────────────────────────────────────────────────────────────
def _rgb(k):
    r, g, b = config.THEME[k]; return RGBColor(r, g, b)

class C: pass
for _k in config.THEME: setattr(C, _k, _rgb(_k))

STATUS_COLOR  = {"Completed":C.green,"In Progress":C.amber,"Not Started":C.gray,"Planned":C.gray}
TIER_COLOR_MAP= {"purple":C.purple,"teal":C.teal,"amber":C.amber,"green":C.green,"gray":C.gray}
SLIDE_W, SLIDE_H = 10.0, 5.625

# ── Primitives ────────────────────────────────────────────────────────────────
def i(v): return Inches(v)

def add_rect(slide, x, y, w, h, fill, border=None, bw=0.75):
    s = slide.shapes.add_shape(1, i(x), i(y), i(w), i(h))
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if border: s.line.color.rgb = border; s.line.width = Pt(bw)
    else:       s.line.fill.background()
    return s

def add_text(slide, text, x, y, w, h, sz=9, bold=False, color=None,
             align=PP_ALIGN.LEFT, va="middle", italic=False):
    tb = slide.shapes.add_textbox(i(x), i(y), i(w), i(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.auto_size = None
    tf.vertical_anchor = {"middle":MSO_ANCHOR.MIDDLE,"top":MSO_ANCHOR.TOP,
                           "bottom":MSO_ANCHOR.BOTTOM}.get(va, MSO_ANCHOR.MIDDLE)
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = str(text)
    r.font.size = Pt(sz); r.font.bold = bold; r.font.italic = italic
    r.font.name = "Calibri"; r.font.color.rgb = color or C.txt_dark

def add_line(slide, x1, y1, x2, y2, color=None, width=0.5):
    ln = slide.shapes.add_connector(1, i(x1), i(y1), i(x2), i(y2))
    ln.line.color.rgb = color or C.border; ln.line.width = Pt(width)

def pill(slide, x, y, w, h, label, color, sz=7.5):
    light = RGBColor(min(color[0]+210,255), min(color[1]+210,255), min(color[2]+210,255))
    add_rect(slide, x, y, w, h, light, color, 0.75)
    add_text(slide, label, x, y, w, h, sz=sz, bold=True, color=color, align=PP_ALIGN.CENTER)

def mini_pill(slide, label, done, total, col, x, y, w=1.75):
    H = 0.44
    add_rect(slide, x, y, w, H, C.card, C.border, 0.75)
    add_text(slide, label, x+0.08, y+0.03, w-0.16, 0.16, sz=7, bold=True, color=C.txt_muted, va="top")
    add_text(slide, f"{done}/{total}", x+0.08, y+0.16, w-0.16, 0.20, sz=13, bold=True, color=col, va="middle")
    add_rect(slide, x+0.08, y+H-0.07, w-0.16, 0.04, C.border)
    if total>0 and done>0:
        add_rect(slide, x+0.08, y+H-0.07, max(0.05,(done/total)*(w-0.16)), 0.04, col)

def stat_card(slide, x, y, w, h, label, value, sub, color):
    """Single KPI stat card with large number."""
    add_rect(slide, x, y, w, h, C.card, C.border, 0.75)
    add_rect(slide, x, y, 0.06, h, color)
    add_text(slide, label, x+0.12, y+0.04, w-0.16, 0.18, sz=7.5, bold=True, color=C.txt_muted, va="top")
    add_text(slide, value, x+0.12, y+0.20, w-0.16, 0.26, sz=18, bold=True, color=color, va="middle")
    if sub:
        add_text(slide, sub, x+0.12, y+0.46, w-0.16, 0.14, sz=6.5, color=C.txt_muted, va="top")

def header(slide, subtitle, badge=None):
    add_rect(slide, 0, 0, SLIDE_W, 0.60, C.header)
    add_rect(slide, 0, 0, 0.18, 0.60, C.accent)
    add_text(slide, f"SSPM Initiative  |  {subtitle}",
             0.28, 0.06, 8.3, 0.48, sz=13, bold=True, color=C.white, va="middle")
    if badge:
        add_rect(slide, 8.7, 0.09, 1.10, 0.42, C.accent)
        add_text(slide, badge, 8.7, 0.09, 1.10, 0.42, sz=9, bold=True,
                 color=C.white, align=PP_ALIGN.CENTER)

def org_footer_space(slide):
    """Leaves the bottom 0.28 inches blank with a faint placeholder."""
    add_rect(slide, 0, 5.345, SLIDE_W, 0.28, C.card_alt)
    add_text(slide, "[ Add your org footer here ]",
             0.3, 5.35, 9.4, 0.25, sz=7, italic=True,
             color=C.border, align=PP_ALIGN.CENTER)

def overall_status(app):
    insts = app["instances"]; done = sum(1 for x in insts if x["done"])
    if done==len(insts): return "Completed"
    if done==0:          return "Not Started"
    return "In Progress"


# =============================================================================
# SLIDE 1 — Summary Dashboard  (Apps KPI strip + Instances table + Notes)
# =============================================================================
def build_slide1(prs, app_summary, inst_summary):
    """
    app_summary  : list of tier dicts — unique app counts per tier
    inst_summary : list of tier dicts — instance counts (prod + np) per tier
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = C.bg
    header(slide, "SSPM Integration — Summary Dashboard")

    TIER_COLORS = {
        "P1": C.accent,  "P2": C.green,
        "P3": C.purple,  "P4": C.teal,  "P5": C.gray,
    }
    SCOPE_TIERS = {"P1", "P2"}

    # ── Section label: Unique Apps ────────────────────────────────────────────
    CY = 0.66
    add_text(slide, "UNIQUE APPLICATIONS — BY PRIORITY TIER",
             0.18, CY, 9.64, 0.18,
             sz=7.5, bold=True, color=C.txt_muted, va="middle")
    add_line(slide, 0.18, CY+0.18, 9.82, CY+0.18, C.border, 0.5)

    # ── Apps KPI strip ────────────────────────────────────────────────────────
    CY += 0.22
    # Grand-total card (slightly wider) + 5 tier cards
    STRIP_H   = 0.70
    TOTAL_W   = 1.50
    TIER_W    = (9.64 - TOTAL_W - 0.30) / 5   # remaining width split equally
    GAP       = 0.06

    # Grand total card
    total_apps = sum(r.get("total_apps", 0) for r in app_summary)
    inscope    = sum(r.get("total_apps", 0) for r in app_summary if r["tier"] in SCOPE_TIERS)
    add_rect(slide, 0.18, CY, TOTAL_W, STRIP_H, C.header, C.header)
    add_rect(slide, 0.18, CY, 0.05, STRIP_H, C.accent)
    add_text(slide, "All Tiers", 0.30, CY+0.04, TOTAL_W-0.16, 0.16,
             sz=7, bold=True, color=RGBColor(0x7d,0xd3,0xfc), va="top")
    add_text(slide, str(total_apps), 0.30, CY+0.18, TOTAL_W-0.16, 0.30,
             sz=26, bold=True, color=C.white, va="middle")
    add_text(slide, f"{inscope} in-scope", 0.30, CY+0.52, TOTAL_W-0.16, 0.16,
             sz=7, color=RGBColor(0x94,0xa3,0xb8), va="top")

    # Per-tier cards
    for ci, row in enumerate(app_summary):
        X    = 0.18 + TOTAL_W + GAP + ci*(TIER_W + GAP)
        tc   = TIER_COLORS.get(row["tier"], C.gray)
        done = row.get("done", 0)
        pend = row.get("pending", 0)
        in_s = row["tier"] in SCOPE_TIERS

        add_rect(slide, X, CY, TIER_W, STRIP_H, C.card, C.border, 0.75)
        add_rect(slide, X, CY, 0.05, STRIP_H, tc)

        # IN/OUT SCOPE badge
        badge_bg = RGBColor(0xdc,0xfc,0xe7) if in_s else RGBColor(0xf1,0xf5,0xf9)
        badge_fc = RGBColor(0x16,0x65,0x34) if in_s else RGBColor(0x47,0x55,0x69)
        add_rect(slide, X+TIER_W-1.02, CY+0.04, 0.98, 0.16, badge_bg)
        add_text(slide, "IN SCOPE" if in_s else "OUT OF SCOPE",
                 X+TIER_W-1.02, CY+0.04, 0.98, 0.16,
                 sz=5.5, bold=True, color=badge_fc, align=PP_ALIGN.CENTER, va="middle")

        add_text(slide, row["tier"],  X+0.10, CY+0.04, 0.5, 0.16,
                 sz=8, bold=True, color=tc, va="top")
        add_text(slide, str(row.get("total_apps", 0)),
                 X+0.10, CY+0.18, TIER_W-0.15, 0.28,
                 sz=24, bold=True, color=tc, va="middle")
        add_text(slide, "Unique Apps", X+0.10, CY+0.46, TIER_W-0.15, 0.14,
                 sz=6.5, color=C.txt_muted, va="top")
        add_text(slide, f"{done} done  ·  {pend} pending",
                 X+0.10, CY+0.56, TIER_W-0.15, 0.13,
                 sz=6, color=C.txt_muted, va="top")

    # ── Section label: Instances ──────────────────────────────────────────────
    CY += STRIP_H + 0.10
    add_text(slide, "INSTANCES — PROD & NON-PROD ONBOARDING STATUS",
             0.18, CY, 9.64, 0.18,
             sz=7.5, bold=True, color=C.txt_muted, va="middle")
    add_line(slide, 0.18, CY+0.18, 9.82, CY+0.18, C.border, 0.5)
    CY += 0.22

    # ── Instances table ───────────────────────────────────────────────────────
    TX, TW = 0.18, 9.64
    LW     = 0.60   # row-label column
    # 3 groups: Prod(3 sub) | NP(3 sub) | Grand(2 sub)  = 8 sub-columns
    N_PROD, N_NP, N_GRAND = 3, 3, 2
    N_SUB  = N_PROD + N_NP + N_GRAND
    SUB_W  = (TW - LW) / N_SUB
    GH     = 0.195  # group header height
    SH2    = 0.155  # sub-header height
    DR     = 0.205  # data row height

    # Group headers
    grp_defs = [
        ("Prod Instances",    N_PROD,  RGBColor(0x06,0x5a,0x8a)),
        ("Non-Prod Instances",N_NP,    RGBColor(0x04,0x60,0x4a)),
        ("Grand Total",       N_GRAND, RGBColor(0x2d,0x2d,0x6a)),
    ]
    gx = TX + LW
    # Tier label header cell
    add_rect(slide, TX, CY, LW, GH+SH2, C.header)
    add_rect(slide, TX, CY, 0.04, GH+SH2, C.accent)
    add_text(slide, "Tier", TX+0.08, CY, LW-0.10, GH+SH2,
             sz=8, bold=True, color=C.white, va="middle")
    for grp_lbl, n_cols, grp_col in grp_defs:
        gw = n_cols * SUB_W
        add_rect(slide, gx, CY, gw-0.02, GH, grp_col)
        add_text(slide, grp_lbl, gx, CY, gw-0.02, GH,
                 sz=7.5, bold=True, color=C.white, align=PP_ALIGN.CENTER, va="middle")
        # Sub-headers
        sub_labels = (["Completed","Pending","Total"] if n_cols==3
                      else ["Instances","Done"])
        for si, sl in enumerate(sub_labels):
            SX = gx + si*SUB_W
            add_rect(slide, SX, CY+GH, SUB_W-0.01, SH2, C.card_alt, C.border, 0.4)
            add_text(slide, sl, SX, CY+GH, SUB_W-0.01, SH2,
                     sz=6, bold=True, color=C.txt_muted, align=PP_ALIGN.CENTER, va="middle")
        gx += gw

    # Data rows
    for ri, row in enumerate(inst_summary):
        RY  = CY + GH + SH2 + ri*DR
        bg  = C.card if ri%2==0 else C.card_alt
        tc  = TIER_COLORS.get(row["tier"], C.gray)
        add_rect(slide, TX, RY, TW, DR, bg, C.border, 0.4)
        add_rect(slide, TX, RY, 0.04, DR, tc)
        add_text(slide, row["tier"], TX+0.08, RY, LW-0.10, DR,
                 sz=8.5, bold=True, color=tc, va="middle")

        pd = row.get("prod_done",0); pp = row.get("prod_pend",0); pt = row.get("prod_total",0)
        nd = row.get("np_done",0);   np_ = row.get("np_pend",0); nt = row.get("np_total",0)
        has_np = (nt > 0)
        gt  = (pt + nt) if has_np else f"{pt}+"
        gd  = pd + (nd if has_np else 0)

        prod_vals  = [str(pd), str(pp), str(pt)]
        np_vals    = ([str(nd), str(np_), str(nt)] if has_np
                      else ["N/A", "N/A", "N/A"])
        grand_vals = [str(gt), str(gd)]

        def cell(val, x, is_done=False, is_na=False, is_total=False):
            col = (C.gray if is_na else
                   C.green if is_done else
                   C.txt_muted if val=="0" else
                   C.header if is_total else C.txt_dark)
            add_text(slide, val, x, RY, SUB_W-0.01, DR,
                     sz=8, bold=(is_done or is_total) and not is_na,
                     italic=is_na, color=col, align=PP_ALIGN.CENTER, va="middle")

        # Prod cells
        cell(prod_vals[0], TX+LW+0*SUB_W, is_done=True)
        cell(prod_vals[1], TX+LW+1*SUB_W)
        cell(prod_vals[2], TX+LW+2*SUB_W, is_total=True)
        # NP cells
        np_is_na = not has_np
        cell(np_vals[0],   TX+LW+3*SUB_W, is_done=(has_np and nd>0), is_na=np_is_na)
        cell(np_vals[1],   TX+LW+4*SUB_W, is_na=np_is_na)
        cell(np_vals[2],   TX+LW+5*SUB_W, is_total=has_np, is_na=np_is_na)
        # Grand total cells
        cell(str(gt),      TX+LW+6*SUB_W, is_total=True)
        cell(str(gd),      TX+LW+7*SUB_W, is_done=True)

    # Total row
    TR_Y = CY + GH + SH2 + len(inst_summary)*DR
    add_rect(slide, TX, TR_Y, TW, DR, C.header, C.header)
    add_rect(slide, TX, TR_Y, 0.04, DR, C.accent)
    add_text(slide, "TOTAL", TX+0.08, TR_Y, LW-0.10, DR,
             sz=8.5, bold=True, color=C.accent, va="middle")
    tot_pd = sum(r.get("prod_done",0)  for r in inst_summary)
    tot_pp = sum(r.get("prod_pend",0)  for r in inst_summary)
    tot_pt = sum(r.get("prod_total",0) for r in inst_summary)
    tot_nd = sum(r.get("np_done",0)    for r in inst_summary if r.get("np_total",0)>0)
    tot_np2= sum(r.get("np_pend",0)    for r in inst_summary if r.get("np_total",0)>0)
    tot_nt = sum(r.get("np_total",0)   for r in inst_summary)
    tot_gt = tot_pt + tot_nt
    tot_gd = tot_pd + tot_nd
    tr_vals = [str(tot_pd),str(tot_pp),str(tot_pt),
               str(tot_nd),str(tot_np2),str(tot_nt),
               str(tot_gt),str(tot_gd)]
    tr_colors = [RGBColor(0x34,0xd3,0x99),C.amber,C.white,
                 RGBColor(0x34,0xd3,0x99),C.amber,C.white,
                 C.white,RGBColor(0x34,0xd3,0x99)]
    for ci2, (tv, tfc) in enumerate(zip(tr_vals, tr_colors)):
        add_text(slide, tv, TX+LW+ci2*SUB_W, TR_Y, SUB_W-0.01, DR,
                 sz=8.5, bold=True, color=tfc, align=PP_ALIGN.CENTER, va="middle")

    # ── Notes band ────────────────────────────────────────────────────────────
    NB_Y = TR_Y + DR + 0.06
    NB_H = 0.50
    NB_W = (TW - 0.10) / 2
    note_defs = [
        ("What is a Unique Application?",
         "A Unique Application is a distinct SaaS product registered in the SSPM "
         "programme — e.g. Salesforce, Workday. It is counted once regardless "
         "of how many environments or regions it operates in.",
         "Example: Salesforce = 1 unique app, even if it has multiple regional tenants.",
         C.accent),
        ("What is an Instance?",
         "An Instance is a specific deployment of an app — a particular "
         "environment (Prod or Non-Prod) or tenant. One app can have "
         "multiple instances, each onboarded into SSPM separately.",
         "Example: Salesforce has 3 instances — APAC Prod, EMEA Prod, AMER Non-Prod.",
         C.teal),
    ]
    for ni, (title, body, example, nc) in enumerate(note_defs):
        NX = TX + ni*(NB_W + 0.10)
        add_rect(slide, NX, NB_Y, NB_W, NB_H, C.card, C.border, 0.75)
        add_rect(slide, NX, NB_Y, 0.04, NB_H, nc)
        add_text(slide, title,   NX+0.10, NB_Y+0.04, NB_W-0.14, 0.16,
                 sz=7.5, bold=True, color=nc, va="top")
        add_text(slide, body,    NX+0.10, NB_Y+0.20, NB_W-0.14, 0.18,
                 sz=6.5, color=C.txt_mid, va="top")
        add_text(slide, example, NX+0.10, NB_Y+0.37, NB_W-0.14, 0.12,
                 sz=6, italic=True, color=C.txt_muted, va="top")

    # Legend
    LEG_Y = NB_Y + NB_H + 0.04
    for lx, lbl, lc in [(0.18,"● Completed",C.green),(1.55,"● Pending",C.amber),
                         (2.85,"● N/A — Non-Prod visibility not available for P3/P4/P5",C.gray)]:
        add_text(slide, lbl, lx, LEG_Y, 4.5, 0.16, sz=6.5, color=lc)

    org_footer_space(slide)


# =============================================================================
# SLIDE 2 — Region-wise Summary
# =============================================================================
def build_slide_region(prs, region_table):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = C.bg
    header(slide, "Integration Status — Region-wise Summary")

    REG_COLORS = {
        "APAC": C.accent, "EMEA": C.teal, "Global": C.green,
        "Japan": C.purple, "North America": C.amber, "TG": C.gray,
    }

    CY = 0.68
    add_text(slide, "INSTANCE ONBOARDING STATUS BY REGION — PROD & NON-PROD",
             0.18, CY, 9.64, 0.18,
             sz=7.5, bold=True, color=C.txt_muted, va="middle")
    add_line(slide, 0.18, CY+0.18, 9.82, CY+0.18, C.border, 0.5)
    CY += 0.22

    TX, TW = 0.18, 9.64
    LW     = 1.20
    N_SUB  = 8
    SUB_W  = (TW - LW) / N_SUB
    GH, SH2, DR = 0.21, 0.165, 0.215

    # Group headers
    grp_defs2 = [
        ("Prod Instances",    3, RGBColor(0x06,0x5a,0x8a)),
        ("Non-Prod Instances",3, RGBColor(0x04,0x60,0x4a)),
        ("Grand Total",       2, RGBColor(0x2d,0x2d,0x6a)),
    ]
    add_rect(slide, TX, CY, LW, GH+SH2, C.header)
    add_rect(slide, TX, CY, 0.05, GH+SH2, C.teal)
    add_text(slide, "Region", TX+0.10, CY, LW-0.12, GH+SH2,
             sz=8, bold=True, color=C.white, va="middle")
    gx = TX+LW
    for grp_lbl, n_cols, grp_col in grp_defs2:
        gw = n_cols*SUB_W
        add_rect(slide, gx, CY, gw-0.02, GH, grp_col)
        add_text(slide, grp_lbl, gx, CY, gw-0.02, GH,
                 sz=7.5, bold=True, color=C.white, align=PP_ALIGN.CENTER, va="middle")
        sub_lbls = (["Completed","Pending","Total"] if n_cols==3 else ["Instances","Done"])
        for si,sl in enumerate(sub_lbls):
            SX=gx+si*SUB_W
            add_rect(slide, SX, CY+GH, SUB_W-0.01, SH2, C.card_alt, C.border, 0.4)
            add_text(slide, sl, SX, CY+GH, SUB_W-0.01, SH2,
                     sz=6, bold=True, color=C.txt_muted, align=PP_ALIGN.CENTER, va="middle")
        gx += gw

    for ri, row in enumerate(region_table):
        RY  = CY+GH+SH2+ri*DR
        bg  = C.card if ri%2==0 else C.card_alt
        rc  = REG_COLORS.get(row["region"], C.gray)
        add_rect(slide, TX, RY, TW, DR, bg, C.border, 0.4)
        add_rect(slide, TX, RY, 0.05, DR, rc)
        add_text(slide, row["region"], TX+0.10, RY, LW-0.14, DR,
                 sz=8.5, bold=True, color=rc, va="middle")
        pd=row.get("prod_done",0); pp=row.get("prod_pend",0); pt=row.get("prod_total",0)
        nd=row.get("np_done",0);   np2=row.get("np_pend",0); nt=row.get("np_total",0)
        has_np=(nt>0)
        np_vals2 = ([str(nd),str(np2),str(nt)] if has_np else ["N/A","N/A","N/A"])
        all_vals = [str(pd),str(pp),str(pt)] + np_vals2 + [str(pt+nt),str(pd+nd)]
        is_na_v  = [False]*3 + ([False]*3 if has_np else [True]*3) + [False,False]
        is_done_v= [True,False,False,has_np,False,False,False,True]
        is_tot_v = [False,False,True,False,False,has_np,True,False]
        for ci2,(val,is_na2,is_done2,is_tot2) in enumerate(zip(all_vals,is_na_v,is_done_v,is_tot_v)):
            col=(C.gray if is_na2 else C.green if is_done2 else
                 C.header if is_tot2 else C.txt_muted if val=="0" else C.txt_dark)
            add_text(slide, val, TX+LW+ci2*SUB_W, RY, SUB_W-0.01, DR,
                     sz=8, bold=(is_done2 or is_tot2) and not is_na2,
                     italic=is_na2, color=col, align=PP_ALIGN.CENTER, va="middle")

    # Total row
    TR_Y2=CY+GH+SH2+len(region_table)*DR
    add_rect(slide, TX, TR_Y2, TW, DR, C.header, C.header)
    add_rect(slide, TX, TR_Y2, 0.05, DR, C.teal)
    add_text(slide,"TOTAL",TX+0.10,TR_Y2,LW-0.14,DR,sz=8.5,bold=True,color=C.accent,va="middle")
    for ci2, (tv, tfc) in enumerate(zip(
        [str(sum(r.get("prod_done",0) for r in region_table)),
         str(sum(r.get("prod_pend",0) for r in region_table)),
         str(sum(r.get("prod_total",0) for r in region_table)),
         str(sum(r.get("np_done",0)  for r in region_table)),
         str(sum(r.get("np_pend",0)  for r in region_table)),
         str(sum(r.get("np_total",0) for r in region_table)),
         str(sum(r.get("prod_total",0)+r.get("np_total",0) for r in region_table)),
         str(sum(r.get("prod_done",0)+r.get("np_done",0)   for r in region_table)),
        ],
        [RGBColor(0x34,0xd3,0x99),C.amber,C.white,
         RGBColor(0x34,0xd3,0x99),C.amber,C.white,
         C.white,RGBColor(0x34,0xd3,0x99)]
    )):
        add_text(slide, tv, TX+LW+ci2*SUB_W, TR_Y2, SUB_W-0.01, DR,
                 sz=8.5, bold=True, color=tfc, align=PP_ALIGN.CENTER, va="middle")

    LEG2_Y = TR_Y2+DR+0.08
    for lx,lbl,lc in [(0.18,"● Completed",C.green),(1.55,"● Pending",C.amber),
                       (2.85,"N/A — No Non-Prod environment",C.gray)]:
        add_text(slide, lbl, lx, LEG2_Y, 3.5, 0.18, sz=6.5, color=lc)

    org_footer_space(slide)




# =============================================================================
# SLIDE 2 — P1 Applications (no blockers)
# =============================================================================
def build_slide2(prs, p1_apps):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = C.bg
    header(slide, "P1 Applications — Integration Status", f"P1 · {len(p1_apps)} Apps")

    INST_Y = 0.68
    all_prod=[x for a in p1_apps for x in a["instances"] if x["env"]=="Prod"]
    all_np  =[x for a in p1_apps for x in a["instances"] if x["env"]!="Prod"]
    add_text(slide, "Instance Coverage", 0.3, INST_Y+0.08, 1.65, 0.28, sz=8, bold=True, color=C.txt_muted, va="middle")
    mini_pill(slide, "PROD",     sum(1 for x in all_prod if x["done"]), len(all_prod), C.green, 2.05, INST_Y)
    mini_pill(slide, "NON-PROD", sum(1 for x in all_np   if x["done"]), len(all_np),   C.teal,  3.95, INST_Y)
    for lx,lbl,lc in [(6.2,"● Completed",C.green),(7.3,"● In Progress",C.amber),(8.4,"● Not Started",C.gray)]:
        add_text(slide, lbl, lx, INST_Y+0.10, 1.1, 0.22, sz=8, color=lc)
    for cx,lbl in [(3.1,"Status"),(6.3,"PROD"),(8.0,"NON-PROD")]:
        add_text(slide, lbl, cx, 1.16, 1.6, 0.17, sz=7.5, bold=True, color=C.txt_muted, align=PP_ALIGN.CENTER)
    add_line(slide, 0.3, 1.35, 9.7, 1.35)

    APP_Y, ROW_H = 1.38, 0.435
    for idx,app in enumerate(p1_apps):
        Y   = APP_Y + idx*ROW_H
        st  = overall_status(app); sc  = STATUS_COLOR.get(st,C.gray)
        prod=[x for x in app["instances"] if x["env"]=="Prod"]
        np_i=[x for x in app["instances"] if x["env"]!="Prod"]
        pd  = sum(1 for x in prod if x["done"]); nd = sum(1 for x in np_i if x["done"])
        pc  = C.green if pd==len(prod) else (C.amber if pd>0 else C.gray)
        nc  = C.teal  if (np_i and nd==len(np_i)) else (C.amber if nd>0 else C.gray)
        add_rect(slide, 0.3, Y, 9.4, ROW_H-0.03, C.card if idx%2==0 else C.card_alt, C.border, 0.5)
        add_rect(slide, 0.3, Y, 0.06, ROW_H-0.03, sc)
        add_text(slide, app["name"], 0.45, Y, 2.4, ROW_H-0.03, sz=11, bold=True, color=C.txt_dark, va="middle")
        pill(slide, 3.1, Y+0.07, 2.3, ROW_H-0.17, st, sc)
        pill(slide, 6.3, Y+0.07, 1.5, ROW_H-0.17, f"PROD  {pd}/{len(prod)}", pc)
        if np_i: pill(slide, 8.0, Y+0.07, 1.6, ROW_H-0.17, f"NP  {nd}/{len(np_i)}", nc)
        else:    add_text(slide, "—", 8.0, Y, 1.6, ROW_H-0.03, sz=9, color=C.txt_muted, align=PP_ALIGN.CENTER)

    org_footer_space(slide)


# =============================================================================
# SLIDE 3 — P2 Applications (no blockers)
# =============================================================================
def build_slide3(prs, p2_apps):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = C.bg
    header(slide, "P2 Applications — Integration Status", f"P2 · {len(p2_apps)} Apps")

    INST_Y=0.68
    p2_pd=sum(a["prod_done"] for a in p2_apps); p2_pt=sum(a["prod_total"] for a in p2_apps)
    p2_nd=sum(a["np_done"]   for a in p2_apps); p2_nt=sum(a["np_total"]   for a in p2_apps)
    add_text(slide,"Instance Coverage",0.3,INST_Y+0.08,1.65,0.28,sz=8,bold=True,color=C.txt_muted,va="middle")
    mini_pill(slide,"PROD",    p2_pd,p2_pt,C.green,2.05,INST_Y)
    mini_pill(slide,"NON-PROD",p2_nd,p2_nt,C.teal, 3.95,INST_Y)
    for lx,lbl,lc in [(6.2,"● All Done",C.green),(7.25,"● Partial",C.amber),(8.2,"● Not Started",C.gray)]:
        add_text(slide,lbl,lx,INST_Y+0.10,1.1,0.22,sz=8,color=lc)
    add_line(slide,0.3,1.15,9.7,1.15)

    GCW,GGAP,GY,GRH=2.27,0.07,1.20,0.77
    for idx,app in enumerate(p2_apps):
        c,r=idx%4,idx//4; X,Y=0.3+c*(GCW+GGAP),GY+r*GRH
        pd_ok=app["prod_done"]==app["prod_total"]
        np_ex=app["np_total"]>0; np_ok=np_ex and app["np_done"]==app["np_total"]
        cc=C.green if (pd_ok and (not np_ex or np_ok)) else (C.amber if (app["prod_done"]>0 or app["np_done"]>0) else C.gray)
        pc=C.green if pd_ok else (C.amber if app["prod_done"]>0 else C.gray)
        add_rect(slide,X,Y,GCW,GRH-0.05,C.card,C.border,0.75)
        add_rect(slide,X,Y,0.06,GRH-0.05,cc)
        add_text(slide,app["name"],X+0.12,Y+0.06,GCW-0.18,0.26,sz=10,bold=True,color=C.txt_dark)
        t1="  ✓" if pd_ok else ("  …" if app["prod_done"]>0 else "  ○")
        add_text(slide,f"PROD  {app['prod_done']}/{app['prod_total']}{t1}",X+0.12,Y+0.35,GCW-0.18,0.20,sz=8,color=pc)
        if np_ex:
            nc=C.teal if np_ok else (C.amber if app["np_done"]>0 else C.gray)
            t2="  ✓" if np_ok else ("  …" if app["np_done"]>0 else "  ○")
            add_text(slide,f"NP  {app['np_done']}/{app['np_total']}{t2}",X+0.12,Y+0.53,GCW-0.18,0.20,sz=8,color=nc)
        else:
            add_text(slide,"NP  —",X+0.12,Y+0.53,GCW-0.18,0.20,sz=8,color=C.txt_muted)

    org_footer_space(slide)


# =============================================================================
# SLIDE 4 — Milestones & Out-of-Scope (no blockers)
# =============================================================================
def build_slide4(prs, tier_summary, milestones):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = C.bg
    header(slide, "Milestone Roadmap & Out-of-Scope Overview")

    T_COLS=[{"l":"Tier","x":0.30,"w":0.85},{"l":"Total Apps","x":1.15,"w":1.55},
            {"l":"Prod Completed","x":2.70,"w":2.00},{"l":"Prod Pending","x":4.70,"w":1.85},
            {"l":"Non-Prod","x":6.55,"w":3.15}]
    TY,TH=0.68,0.23
    add_rect(slide,0.3,TY,9.4,TH,C.header)
    for col in T_COLS:
        add_text(slide,col["l"],col["x"]+0.10,TY,col["w"]-0.12,TH,sz=8,bold=True,color=C.white,va="middle")
    for i_r,row in enumerate(tier_summary):
        RY=TY+TH+i_r*TH; tc=TIER_COLOR_MAP.get(row["color"],C.gray)
        add_rect(slide,0.3,RY,9.4,TH,C.card if i_r%2==0 else C.card_alt,C.border,0.5)
        add_rect(slide,0.3,RY,0.06,TH,tc)
        vals=[row["tier"],row["total"],row["prod_done"],row["prod_pending"],"N/A — Visibility Pending"]
        for c_i,col in enumerate(T_COLS):
            is_na=str(vals[c_i]).startswith("N/A")
            add_text(slide,vals[c_i],col["x"]+0.12,RY,col["w"]-0.14,TH,
                     sz=8.5 if c_i==0 else 8,bold=(c_i==0),italic=is_na,
                     color=tc if c_i==0 else (C.amber if is_na else C.txt_dark),va="middle")

    SEP_Y=TY+TH*4+0.08; add_line(slide,0.3,SEP_Y,9.7,SEP_Y)
    TX,TW=0.3,9.4; curY=SEP_Y+0.06; THdr,TRH,TGAP=0.27,0.255,0.07
    for m in milestones:
        mc=TIER_COLOR_MAP.get(m["color"],C.gray)
        lbg=RGBColor(min(mc[0]+215,255),min(mc[1]+215,255),min(mc[2]+215,255))
        sc=STATUS_COLOR.get(m["status"],C.gray)
        add_rect(slide,TX,curY,TW,THdr,lbg,mc,0.75)
        add_rect(slide,TX,curY,0.06,THdr,mc)
        add_text(slide,m["name"],TX+0.14,curY,7.0,THdr,sz=9.5,bold=True,color=mc,va="middle")
        pill(slide,TX+TW-1.5,curY+0.04,1.45,THdr-0.08,m["status"],sc)
        for ri,task in enumerate(m["tasks"]):
            RY=curY+THdr+ri*TRH; ts=STATUS_COLOR.get(task["status"],C.gray)
            add_rect(slide,TX,RY,TW,TRH-0.03,C.card if ri%2==0 else C.card_alt,C.border,0.5)
            add_text(slide,str(ri+1),TX+0.10,RY,0.28,TRH-0.03,sz=8,bold=True,color=mc,align=PP_ALIGN.CENTER,va="middle")
            add_text(slide,task["task"],TX+0.42,RY,7.1,TRH-0.03,sz=9,color=C.txt_dark,va="middle")
            pill(slide,TX+TW-1.5,RY+0.04,1.45,TRH-0.11,task["status"],ts)
        curY+=THdr+len(m["tasks"])*TRH+TGAP

    org_footer_space(slide)


# =============================================================================
# SLIDE 5 — Dedicated Blockers Slide
# =============================================================================
def build_slide5(prs, p1_blockers, s3_blockers):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = C.bg
    header(slide, "Blockers & Impediments")

    PHASE_COL={"Phase 1":C.accent,"Phase 2":C.amber,"Phase 3":C.purple}
    CY = 0.68

    # ── P1 Integration Blockers ───────────────────────────────────────────────
    add_rect(slide, 0.18, CY, 9.64, 0.26, RGBColor(0xFF,0xED,0xED), C.red, 0.75)
    add_rect(slide, 0.18, CY, 0.06, 0.26, C.red)
    add_text(slide, "🚧  P1 Integration Blockers",
             0.30, CY, 6, 0.26, sz=9.5, bold=True, color=C.red, va="middle")
    CY += 0.28
    BRH = 0.215
    for b in p1_blockers:
        ic = C.red if b["impact"]=="High" else C.amber
        add_rect(slide, 0.18, CY, 9.64, BRH-0.02, C.card, C.border, 0.5)
        add_rect(slide, 0.18, CY, 0.06, BRH-0.02, ic)
        add_text(slide, b["id"],   0.30, CY, 0.40, BRH-0.02, sz=8, bold=True, color=ic, va="middle")
        add_text(slide, b["text"], 0.74, CY, 7.20, BRH-0.02, sz=8.5, color=C.txt_dark, va="middle")
        add_text(slide, "Owner: "+b["owner"], 8.0, CY, 1.1, BRH-0.02, sz=7.5, color=C.txt_muted, align=PP_ALIGN.RIGHT, va="middle")
        pill(slide, 9.16, CY+0.03, 0.58, BRH-0.08, b["impact"], ic)
        CY += BRH

    CY += 0.10
    add_line(slide, 0.18, CY, 9.82, CY, C.border, 0.75)
    CY += 0.10

    # ── Cross-phase / Milestone Blockers ──────────────────────────────────────
    add_rect(slide, 0.18, CY, 9.64, 0.26, RGBColor(0xFF,0xED,0xED), C.red, 0.75)
    add_rect(slide, 0.18, CY, 0.06, 0.26, C.red)
    add_text(slide, "🚧  Milestone & Phase Blockers",
             0.30, CY, 6, 0.26, sz=9.5, bold=True, color=C.red, va="middle")
    CY += 0.28
    for b in s3_blockers:
        ic = C.red if b["impact"]=="High" else C.amber
        pc = PHASE_COL.get(b.get("phase","Phase 1"), C.gray)
        add_rect(slide, 0.18, CY, 9.64, BRH-0.02, C.card, C.border, 0.5)
        add_rect(slide, 0.18, CY, 0.06, BRH-0.02, ic)
        add_text(slide, b["id"],   0.30, CY, 0.40, BRH-0.02, sz=8, bold=True, color=ic, va="middle")
        add_text(slide, b["text"], 0.74, CY, 5.70, BRH-0.02, sz=8.5, color=C.txt_dark, va="middle")
        pill(slide, 6.50, CY+0.03, 1.10, BRH-0.08, b.get("phase",""), pc)
        add_text(slide, "Owner: "+b["owner"], 7.68, CY, 1.1, BRH-0.02, sz=7.5, color=C.txt_muted, align=PP_ALIGN.RIGHT, va="middle")
        pill(slide, 9.16, CY+0.03, 0.58, BRH-0.08, b["impact"], ic)
        CY += BRH

    org_footer_space(slide)


# =============================================================================
# SLIDE 6 — P1 Score Improvement  (8-pane screenshot layout, 3 months)
# =============================================================================
def build_slide6(prs, p1_apps):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = C.bg
    header(slide, "P1 Apps — Security Score Improvement (Last 3 Months)")

    # Legend row
    LY = 0.66
    add_text(slide, "Each pane shows the score trend for one P1 app over Month 1 → Month 2 → Month 3.",
             0.18, LY, 9.64, 0.22, sz=8, color=C.txt_muted, va="middle")

    # 8 panes: 4 columns × 2 rows
    COLS, ROWS   = 4, 2
    PAD_X, PAD_Y = 0.18, 0.90   # left/top padding
    GAP_X, GAP_Y = 0.10, 0.10   # gap between panes
    AVAIL_W = SLIDE_W - 2*PAD_X
    AVAIL_H = 4.34               # leave space for header + legend + org footer
    PW = (AVAIL_W - (COLS-1)*GAP_X) / COLS
    PH = (AVAIL_H - (ROWS-1)*GAP_Y) / ROWS

    MONTH_LABELS = ["Month 1", "Month 2", "Month 3"]

    for idx in range(8):
        col = idx % COLS
        row = idx // COLS
        X   = PAD_X + col*(PW+GAP_X)
        Y   = PAD_Y + row*(PH+GAP_Y)
        app = p1_apps[idx] if idx < len(p1_apps) else {"name": f"A{idx+1}"}

        # Pane outer card
        add_rect(slide, X, Y, PW, PH, C.card, C.border, 0.75)
        # Coloured top bar
        tc = [C.accent,C.green,C.teal,C.purple,C.amber,C.accent,C.green,C.teal][idx]
        add_rect(slide, X, Y, PW, 0.22, tc)
        add_text(slide, app["name"], X+0.08, Y, PW-0.12, 0.22,
                 sz=9, bold=True, color=C.white, va="middle")

        # Month labels across the pane
        col_w = (PW - 0.12) / 3
        for mi, ml in enumerate(MONTH_LABELS):
            MX = X + 0.06 + mi*col_w
            add_rect(slide, MX, Y+0.24, col_w-0.04, 0.16,
                     C.card_alt, C.border, 0.4)
            add_text(slide, ml, MX, Y+0.24, col_w-0.04, 0.16,
                     sz=6, bold=True, color=C.txt_muted, align=PP_ALIGN.CENTER, va="middle")

        # Screenshot placeholder area (dashed border + instruction text)
        SHOT_Y = Y + 0.42
        SHOT_H = PH - 0.50
        # Draw a dashed-style placeholder using thin rect + inner text
        add_rect(slide, X+0.05, SHOT_Y, PW-0.10, SHOT_H,
                 RGBColor(0xF0,0xF4,0xFA), C.border, 0.5)
        add_text(slide,
                 f"📷  Paste screenshot\nof {app['name']} score\ntrend here",
                 X+0.05, SHOT_Y, PW-0.10, SHOT_H,
                 sz=7, color=C.txt_muted, align=PP_ALIGN.CENTER, va="middle")

    org_footer_space(slide)


# =============================================================================
# MAIN
# =============================================================================
def main():
    if config.USE_JIRA:
        from jira_loader import load_from_jira
        d            = load_from_jira()
        app_summary  = d.get("app_summary",  manual_data.APP_SUMMARY)
        inst_summary = d.get("inst_summary", manual_data.INST_SUMMARY)
        region_table = d.get("region_table", manual_data.REGION_TABLE)
        p1_apps      = d["p1_apps"]
        p1_blockers  = d["p1_blockers"]
        p2_apps      = d["p2_apps"]
        s3_blockers  = d["s3_blockers"]
        tier_summary = manual_data.TIER_SUMMARY
        milestones   = manual_data.MILESTONES
        print("  Data source: JIRA")
    else:
        app_summary  = manual_data.APP_SUMMARY
        inst_summary = manual_data.INST_SUMMARY
        region_table = manual_data.REGION_TABLE
        p1_apps      = manual_data.P1_APPS
        p1_blockers  = manual_data.P1_BLOCKERS
        p2_apps      = manual_data.P2_APPS
        tier_summary = manual_data.TIER_SUMMARY
        milestones   = manual_data.MILESTONES
        s3_blockers  = manual_data.S3_BLOCKERS
        print("  Data source: data.py (manual)")

    prs = Presentation()
    prs.slide_width  = Inches(SLIDE_W)
    prs.slide_height = Inches(SLIDE_H)

    print("  Slide 1 — Summary Dashboard (Apps + Instances + Notes)...")
    build_slide1(prs, app_summary, inst_summary)
    print("  Slide 2 — Region-wise Summary...")
    build_slide_region(prs, region_table)
    print("  Slide 3 — P1 Applications...")
    build_slide2(prs, p1_apps)
    print("  Slide 4 — P2 Applications...")
    build_slide3(prs, p2_apps)
    print("  Slide 5 — Milestones & Out-of-Scope...")
    build_slide4(prs, tier_summary, milestones)
    print("  Slide 6 — Blockers...")
    build_slide5(prs, p1_blockers, s3_blockers)
    print("  Slide 7 — P1 Score Improvement (8 panes)...")
    build_slide6(prs, p1_apps)

    prs.save(config.OUTPUT_FILE)
    print(f"\n✅  Saved: {config.OUTPUT_FILE}")

if __name__ == "__main__":
    print("\nSSPM PPT Generator")
    print("=" * 40)
    main()
