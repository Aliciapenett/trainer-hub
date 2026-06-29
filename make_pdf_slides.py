from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

W, H = landscape(letter)  # 11 x 8.5

NAVY  = HexColor("#1F3564")
GOLD  = HexColor("#F0B323")
WHITE = colors.white
LIGHT = HexColor("#F2F4F8")
RED   = HexColor("#C0392B")
GREEN = HexColor("#1A8C4E")
DARK  = HexColor("#1F3564")

out = "/root/.openclaw/workspace/May_2026_Walkthrough_Slides.pdf"
c = canvas.Canvas(out, pagesize=landscape(letter))

def title_page(title, subtitle=""):
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, 0.6*inch, W, 0.18*inch, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(W/2, H/2 + 0.3*inch, title)
    if subtitle:
        c.setFillColor(GOLD)
        c.setFont("Helvetica", 20)
        c.drawCentredString(W/2, H/2 - 0.4*inch, subtitle)
    c.showPage()

def section_page(title):
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0.4*inch, H/2 - 0.05*inch, W - 0.8*inch, 0.07*inch, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(W/2, H/2 + 0.3*inch, title)
    c.showPage()

def body_page(title, bullets):
    # background
    c.setFillColor(LIGHT)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    # title bar
    c.setFillColor(NAVY)
    c.rect(0, H - 1.0*inch, W, 1.0*inch, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, H - 1.05*inch, W, 0.05*inch, fill=1, stroke=0)
    # title text
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(0.35*inch, H - 0.72*inch, title)

    # bullets
    y = H - 1.35*inch
    for (text, level, flag) in bullets:
        if y < 0.4*inch:
            break
        x = 0.5*inch + level * 0.3*inch
        if flag == 'bad':
            col = RED
        elif flag == 'ok':
            col = GREEN
        else:
            col = NAVY

        c.setFillColor(col)
        if level == 0:
            c.setFont("Helvetica-Bold", 14)
            prefix = "▸  "
        else:
            c.setFont("Helvetica", 12)
            prefix = "    •  "

        # simple word-wrap
        full = prefix + text
        max_w = W - x - 0.5*inch
        # estimate chars per line
        font_size = 14 if level == 0 else 12
        chars_per_line = int(max_w / (font_size * 0.52))
        
        words = full.split()
        lines = []
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if len(test) <= chars_per_line:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)

        for i, ln in enumerate(lines):
            if y < 0.4*inch:
                break
            draw_x = x if i == 0 else x + (0.35*inch if level == 0 else 0.5*inch)
            c.drawString(draw_x, y, ln)
            y -= (0.28*inch if level == 0 else 0.24*inch)

        y -= 0.06*inch  # extra gap between bullets

    c.showPage()

# ── SLIDES ────────────────────────────────────────────────────────────────

title_page("May 2026 Clinical Walkthrough",
           "Multi-Site Quality Review  |  May 2026")

body_page("Overview", [
    ("Sites Visited",           0, None),
    ("Princeton  –  May 6",     1, None),
    ("Bethesda  –  May 13",     1, None),
    ("Bowie  –  May 14",        1, None),
    ("Key Themes & Action Items", 0, None),
])

section_page("Princeton  |  May 6, 2026")

body_page("Princeton – Clinic Overview", [
    ("20 patients  •  16 scans  •  3 techs", 0, None),
    ("Issues & Complaints",                  0, 'bad'),
    ("Medications not labeled",              1, 'bad'),
    ("Storage room needs an additional shelf", 1, 'warn'),
])

body_page("Princeton – Varithena (Cortney)", [
    ("20 minutes total",                               0, None),
    ("Measured all artifact",                          1, None),
    ("DVT r/o performed before procedure",             1, 'ok'),
    ("Optisign video played",                          1, 'ok'),
    ("Consents signed",                                1, 'ok'),
    ("Sharps disposed of properly",                    1, 'ok'),
    ("Time-out performed out loud",                    1, 'ok'),
    ("Areas for Improvement",                          0, 'warn'),
    ("Scanned SSV but documented as GSV",              1, 'bad'),
    ("Patient felt experience focused on cosmetics, not her concern", 1, 'warn'),
])

body_page("Princeton – Varithena (McKinley)", [
    ("8 minutes total",                   0, None),
    ("Talk ran 12 minutes",               1, 'warn'),
    ("Presenter not fully confident",     1, 'warn'),
    ('"Knock on wood" language used',     1, 'warn'),
    ("1 hour total appointment",          1, None),
    ("Consents signed",                   1, 'ok'),
    ("Sharps disposed of properly",       1, 'ok'),
    ("Time-out performed out loud",       1, 'ok'),
])

body_page("Princeton – RFA (Jen)", [
    ("23 minutes total  (13 min for RFA)",              0, None),
    ("Scan took 40 minutes  –  1 hr total",             1, 'warn'),
    ("Optisign video NOT played",                       1, 'bad'),
    ("Initially refused scan-assist; accepted after trial", 1, 'warn'),
    ("Consent signed",                                  1, 'ok'),
    ("Sharps disposed of properly",                    1, 'ok'),
    ("Time-out performed out loud",                    1, 'ok'),
])

section_page("Bethesda  |  May 13, 2026")

body_page("Bethesda – Clinic Overview", [
    ("26 patients  •  18 scans  •  3 techs", 0, None),
    ("Issues & Complaints",                  0, 'bad'),
    ("Front desk rooms all patients",        1, 'warn'),
    ("Techs prep RFAs independently",        1, 'warn'),
    ("Medications not labeled",              1, 'bad'),
])

body_page("Bethesda – Varithena + US (Rob)", [
    ("24 minutes total  (8 min for Varithena)",  0, None),
    ("All consents signed",                      1, 'ok'),
    ("Varithena tray set-up was efficient",      1, 'ok'),
    ("Rob was very outgoing with patient",       1, 'ok'),
    ("Sharps disposed of properly",             1, 'ok'),
    ("Time-out NOT performed out loud",          1, 'bad'),
])

body_page("Bethesda – US Review", [
    ("14 minutes total",                           0, None),
    ("Thoroughly explained findings to patient",   1, 'ok'),
    ("Folder given by front desk",                 1, 'ok'),
    ("Optisign video played",                      1, 'ok'),
    ("Note completed properly",                    1, 'ok'),
    ("No iPad available",                          1, 'bad'),
])

body_page("Bethesda – RFA + US (Dr. Green / Ruth – Training)", [
    ("40 minutes total  (14 min for RFA)",    0, None),
    ("Consent signed",                        1, 'ok'),
    ("Sharps disposed of properly",          1, 'ok'),
    ("Note completed",                       1, 'ok'),
    ("Time-out NOT performed out loud",       1, 'bad'),
    ("Wrong note opened initially",          1, 'bad'),
    ("US note not completed properly",       1, 'bad'),
])

section_page("Bowie  |  May 14, 2026")

body_page("Bowie – Clinic Overview", [
    ("Issues & Complaints",             0, 'bad'),
    ("Front desk rooms all patients",   1, 'warn'),
    ("RFA times are stretched",         1, 'warn'),
    ("Techs prep RFAs independently",   1, 'warn'),
])

body_page("Bowie – RFA + US (Case 1)", [
    ("55 minutes total  (15 min for RFA)",                    0, None),
    ("Sharps disposed of properly",                           1, 'ok'),
    ("Topical lidocaine used — no access issues",             1, 'ok'),
    ("Time-out NOT performed out loud",                       1, 'bad'),
    ("16g needle used before intro noted",                    1, 'bad'),
    ("Physician bent over during ablation",                   1, 'warn'),
    ("Sonographer assisting patient — limits availability",   1, 'warn'),
])

body_page("Bowie – RFA + US (Case 2)", [
    ("1.5 hours total  (RFA 35 min)",                         0, None),
    ("Sharps disposed of properly",                           1, 'ok'),
    ("Time-out NOT performed out loud",                       1, 'bad'),
    ("RFA performed before post-scan",                        1, 'bad'),
    ("Multiple failed GSV access attempts — switched to SSV", 1, 'warn'),
    ("Physician looked to observer for guidance",             1, 'warn'),
    ("US note not completed properly",                        1, 'bad'),
])

body_page("Bowie – US Review", [
    ("10 minutes total",                           0, None),
    ("Thoroughly explained findings to patient",   1, 'ok'),
    ("Folder given by front desk",                 1, 'ok'),
    ("Optisign video played",                      1, 'ok'),
    ("Note completed",                             1, 'ok'),
    ("No iPad available",                          1, 'bad'),
])

section_page("Key Themes & Action Items")

body_page("Recurring Issues Across All Sites", [
    ("CRITICAL — Address Immediately",                        0, 'bad'),
    ("Medications NOT labeled at all sites",                  1, 'bad'),
    ("Time-out NOT performed out loud (multiple sites)",      1, 'bad'),
    ("OPERATIONAL CONCERNS",                                  0, 'warn'),
    ("Front desk rooming patients (Bethesda, Bowie)",         1, 'warn'),
    ("Techs prepping RFAs independently (Bethesda, Bowie)",   1, 'warn'),
    ("No iPad for US reviews (Bethesda, Bowie)",              1, 'warn'),
    ("Optisign video not played in some cases",               1, 'warn'),
    ("POSITIVE OBSERVATIONS",                                 0, 'ok'),
    ("Sharps disposal consistently compliant",                1, 'ok'),
    ("Most consents signed",                                  1, 'ok'),
    ("Patient education thorough in US reviews",              1, 'ok'),
])

body_page("Action Items", [
    ("Label ALL medications — no exceptions",                              0, 'bad'),
    ("Reinforce time-out protocol — must be out loud every time",         0, 'bad'),
    ("Clarify front desk vs. tech rooming responsibilities",               0, 'warn'),
    ("Ensure Optisign video plays for every eligible patient",             0, 'warn'),
    ("Provide iPads at Bethesda and Bowie for US reviews",                 0, 'warn'),
    ("Fix RFA documentation — correct note, complete US notes",           0, 'warn'),
    ("Coach McKinley on confidence and talk timing",                       0, 'warn'),
    ("Bowie: review RFA sequencing (post-scan should follow RFA)",        0, 'warn'),
])

c.save()
print(f"Saved: {out}")
