from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.colors import HexColor, Color
import math

W, H = landscape(letter)  # 11 x 8.5 inches

# ── Palette (matching original) ──────────────────────────────────────────
NAVY    = HexColor("#1B2A5B")
PURPLE  = HexColor("#8E44AD")
TEAL    = HexColor("#00BCD4")
PINK    = HexColor("#E91E63")
GOLD    = HexColor("#FFC107")
ORANGE  = HexColor("#FF9800")
WHITE   = colors.white
CHARCOAL= HexColor("#333333")
LIGHT_BG= HexColor("#EEF1FB")   # icy blue-lavender
LAVENDER= HexColor("#EAD9F7")   # soft lilac
MID_LAV = HexColor("#D8C4F0")
GREEN_OK= HexColor("#1A8C4E")
RED_BAD = HexColor("#C0392B")
CARD_BG = HexColor("#FFFFFF")

out = "/root/.openclaw/workspace/May_2026_Walkthrough_Slides_v2.pdf"
c = rl_canvas.Canvas(out, pagesize=landscape(letter))

# ── Drawing helpers ───────────────────────────────────────────────────────

def gradient_bg(c):
    """Fake gradient: icy blue left → lavender right using thin vertical strips."""
    steps = 40
    r1,g1,b1 = 0xEE/255, 0xF1/255, 0xFB/255   # LIGHT_BG
    r2,g2,b2 = 0xEA/255, 0xD9/255, 0xF7/255   # LAVENDER
    strip = W / steps
    for i in range(steps):
        t = i / steps
        r = r1 + (r2-r1)*t
        g = g1 + (g2-g1)*t
        b = b1 + (b2-b1)*t
        c.setFillColor(Color(r,g,b))
        c.rect(i*strip, 0, strip+1, H, fill=1, stroke=0)

def draw_waves(c, alpha=0.12):
    """Draw soft decorative wave curves across the bottom half."""
    # approximate alpha by mixing with background color
    r = int(0x9B + (0xEE - 0x9B) * (1 - alpha))
    g = int(0x59 + (0xF1 - 0x59) * (1 - alpha))
    b = int(0xB6 + (0xFB - 0xB6) * (1 - alpha))
    wave_col = Color(r/255, g/255, b/255)
    c.setStrokeColor(wave_col)
    c.setLineWidth(1.2)
    offsets = [0, 0.4*inch, 0.8*inch, 1.2*inch]
    for dy in offsets:
        p = c.beginPath()
        p.moveTo(0, 1.2*inch + dy)
        p.curveTo(W*0.25, 2.5*inch+dy, W*0.5, 0.3*inch+dy, W*0.75, 1.8*inch+dy)
        p.curveTo(W*0.9, 2.8*inch+dy, W, 1.0*inch+dy, W, 1.0*inch+dy)
        c.drawPath(p, stroke=1, fill=0)

def draw_cross_accents(c):
    """Scatter small + crosses in teal/mint around edges."""
    c.saveState()
    c.setStrokeColor(HexColor("#80DDE8"))  # light teal approximating alpha
    positions = [
        (0.3*inch, H-0.4*inch, 0.18*inch),
        (0.5*inch, H-0.7*inch, 0.12*inch),
        (W-0.4*inch, H-0.3*inch, 0.15*inch),
        (W-0.3*inch, 0.5*inch, 0.18*inch),
        (0.4*inch, 0.35*inch, 0.14*inch),
        (W*0.92, H*0.5, 0.12*inch),
    ]
    for (x,y,s) in positions:
        c.setLineWidth(1.5)
        c.line(x-s, y, x+s, y)
        c.line(x, y-s, x, y+s)
    c.restoreState()

def draw_logo_placeholder(c):
    """Small 'VTC' badge in top-right corner."""
    x, y = W - 1.3*inch, H - 0.75*inch
    c.setFillColor(PURPLE)
    c.circle(x, y, 0.28*inch, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x, y - 0.05*inch, "VTC")

def stat_circle(c, cx, cy, r, number, label, icon_char=""):
    """Draw a decorative stat circle."""
    # outer ring
    c.setStrokeColor(PURPLE)
    c.setFillColor(HexColor("#F3EAFC"))
    c.setLineWidth(2.5)
    c.circle(cx, cy, r, fill=1, stroke=1)
    # number
    c.setFillColor(PURPLE)
    c.setFont("Helvetica-Bold", 44)
    c.drawCentredString(cx, cy + 0.05*inch, number)
    # label
    c.setFillColor(NAVY)
    c.setFont("Helvetica", 16)
    c.drawCentredString(cx, cy - 0.45*inch, label)
    if icon_char:
        c.setFillColor(PURPLE)
        c.setFont("Helvetica", 22)
        c.drawCentredString(cx, cy + 0.55*inch, icon_char)

def bullet_line(c, x, y, text, level=0, flag=None, font_size=None):
    """Draw a single bullet line with colored icon prefix."""
    if font_size is None:
        font_size = 16 if level == 0 else 13

    indent = level * 0.35*inch

    # pick icon & color
    if flag == 'bad':
        icon = "🔴"; col = RED_BAD
    elif flag == 'ok':
        icon = "✅"; col = GREEN_OK
    elif flag == 'warn':
        icon = "⚠️"; col = ORANGE
    elif flag == 'section':
        icon = "▌"; col = NAVY
    else:
        icon = "◆" if level == 0 else "›"
        col = PURPLE if level == 0 else CHARCOAL

    c.setFont("Helvetica-Bold" if level == 0 else "Helvetica", font_size)
    c.setFillColor(col)

    # Draw icon
    c.setFont("Helvetica-Bold", font_size)
    c.drawString(x + indent, y, icon + "  ")

    # Draw text (word-wrapped)
    c.setFillColor(CHARCOAL if level > 0 else NAVY)
    c.setFont("Helvetica-Bold" if level == 0 else "Helvetica", font_size)
    text_x = x + indent + 0.32*inch
    max_w = W - text_x - 0.4*inch
    chars_per = int(max_w / (font_size * 0.52))
    words = text.split()
    lines = []
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if len(test) <= chars_per:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)

    line_h = font_size * 1.35
    for i, ln in enumerate(lines):
        if i == 0:
            c.drawString(text_x, y, ln)
        else:
            y -= line_h * 0.72
            c.drawString(text_x, y, ln)
    return y  # return final y after wrapping

# ── Slide builders ────────────────────────────────────────────────────────

def title_slide(title, subtitle=""):
    gradient_bg(c)
    draw_waves(c, alpha=0.15)
    draw_logo_placeholder(c)

    # Decorative purple arc accent (light, approximating low alpha)
    c.setStrokeColor(HexColor("#C8A8E0"))
    c.setLineWidth(4)
    c.arc(W*0.05, H*0.1, W*0.45, H*0.9, startAng=200, extent=140)

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 46)
    c.drawCentredString(W/2, H/2 + 0.8*inch, title)

    # gold underline
    uw = len(title) * 14
    c.setStrokeColor(GOLD)
    c.setLineWidth(3)
    c.line(W/2 - uw*0.5, H/2 + 0.55*inch, W/2 + uw*0.5, H/2 + 0.55*inch)

    if subtitle:
        c.setFillColor(PURPLE)
        c.setFont("Helvetica", 22)
        c.drawCentredString(W/2, H/2 + 0.1*inch, subtitle)

    # Rounded white card for sites
    card_x, card_y = W/2 - 2.2*inch, H/2 - 1.4*inch
    card_w, card_h = 4.4*inch, 1.1*inch
    c.setFillColor(WHITE)
    c.setStrokeColor(MID_LAV)
    c.setLineWidth(1)
    c.roundRect(card_x, card_y, card_w, card_h, 0.15*inch, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W/2, card_y + 0.72*inch, "Princeton 5/6  ·  Bethesda 5/13  ·  Bowie 5/14")
    c.setFont("Helvetica", 13)
    c.setFillColor(PURPLE)
    c.drawCentredString(W/2, card_y + 0.35*inch, "Multi-Site Quality Review  |  May 2026")
    c.showPage()


def section_slide(location, date):
    gradient_bg(c)
    draw_waves(c, alpha=0.18)
    draw_logo_placeholder(c)

    # Big location name
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 64)
    c.drawCentredString(W/2, H/2 + 0.4*inch, location)

    # Gold line
    uw = len(location) * 19
    c.setStrokeColor(GOLD)
    c.setLineWidth(3)
    c.line(W/2 - uw*0.5, H/2 + 0.1*inch, W/2 + uw*0.5, H/2 + 0.1*inch)

    # Date in purple
    c.setFillColor(PURPLE)
    c.setFont("Helvetica", 32)
    c.drawCentredString(W/2, H/2 - 0.4*inch, date)
    c.showPage()


def stats_slide(location, patients, scans, techs):
    gradient_bg(c)
    draw_waves(c, alpha=0.1)
    draw_cross_accents(c)
    draw_logo_placeholder(c)

    # Header
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(0.5*inch, H - 0.7*inch, location)
    c.setStrokeColor(PURPLE)
    c.setLineWidth(2)
    c.line(0.5*inch, H - 0.8*inch, 4.5*inch, H - 0.8*inch)

    # Three circles
    cx_list = [W*0.22, W*0.5, W*0.78]
    cy = H/2 - 0.1*inch
    r = 1.15*inch
    data = [(patients,"Patients","👤"), (scans,"Scans","🔬"), (techs,"Techs","👥")]
    for (num, label, icon), cx in zip(data, cx_list):
        stat_circle(c, cx, cy, r, num, label, icon)
    c.showPage()


def body_slide(header, bullets, two_col=False):
    gradient_bg(c)
    draw_waves(c, alpha=0.08)
    draw_logo_placeholder(c)

    # Header bar (rounded pill style)
    c.setFillColor(NAVY)
    c.roundRect(0.3*inch, H - 1.0*inch, W - 0.6*inch, 0.75*inch, 0.12*inch, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(0.65*inch, H - 0.68*inch, header)

    if not two_col:
        y = H - 1.3*inch
        line_gap_main = 0.36*inch
        line_gap_sub  = 0.28*inch
        for (text, level, flag) in bullets:
            if y < 0.4*inch: break
            new_y = bullet_line(c, 0.55*inch, y, text, level, flag)
            gap = line_gap_main if level == 0 else line_gap_sub
            y = new_y - gap
    else:
        # split bullets into two columns
        mid = len(bullets) // 2
        col1, col2 = bullets[:mid], bullets[mid:]
        for col_bullets, col_x in [(col1, 0.45*inch), (col2, W/2 + 0.1*inch)]:
            y = H - 1.3*inch
            for (text, level, flag) in col_bullets:
                if y < 0.4*inch: break
                font_size = 14 if level == 0 else 12
                # restrict width for two-col
                c.saveState()
                new_y = bullet_line(c, col_x, y, text, level, flag, font_size=font_size)
                c.restoreState()
                gap = 0.32*inch if level == 0 else 0.26*inch
                y = new_y - gap
    c.showPage()


def summary_section_slide():
    gradient_bg(c)
    draw_waves(c, alpha=0.18)
    draw_logo_placeholder(c)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 52)
    c.drawCentredString(W/2, H/2 + 0.4*inch, "Key Themes")
    c.setFont("Helvetica-Bold", 52)
    c.drawCentredString(W/2, H/2 - 0.2*inch, "& Action Items")
    c.setStrokeColor(GOLD)
    c.setLineWidth(3)
    c.line(W/2 - 3.0*inch, H/2 - 0.55*inch, W/2 + 3.0*inch, H/2 - 0.55*inch)
    c.showPage()


# ══════════════════════════════════════════════════════════════════════════
# BUILD ALL SLIDES
# ══════════════════════════════════════════════════════════════════════════

title_slide("May 2026 Clinical Walkthrough")

# ── PRINCETON ─────────────────────────────────────────────────────────────
section_slide("Princeton", "May 6, 2026")

stats_slide("Princeton", "20", "16", "3")

body_slide("Princeton – Clinic Overview", [
    ("Medications not labeled",                      0, 'bad'),
    ("Storage room needs an additional shelf",       0, 'warn'),
])

body_slide("Princeton – Varithena (Cortney)", [
    ("20 minutes total",                             0, None),
    ("Measured all artifact",                        1, None),
    ("DVT r/o performed before procedure ✓",         1, 'ok'),
    ("Optisign video played ✓",                      1, 'ok'),
    ("Consents signed ✓",                            1, 'ok'),
    ("Sharps disposed of properly ✓",                1, 'ok'),
    ("Time-out performed out loud ✓",                1, 'ok'),
    ("Scanned SSV — documented as GSV",              1, 'bad'),
    ("Patient experience felt cosmetics-focused",    1, 'warn'),
])

body_slide("Princeton – Varithena (McKinley)", [
    ("8 minutes total  (1 hour total appointment)",  0, None),
    ("Talk ran 12 minutes — overtime",               1, 'warn'),
    ("Presenter not fully confident",                1, 'warn'),
    ('"Knock on wood" language used',                1, 'warn'),
    ("Consents signed ✓",                            1, 'ok'),
    ("Sharps disposed of properly ✓",               1, 'ok'),
    ("Time-out performed out loud ✓",               1, 'ok'),
])

body_slide("Princeton – RFA (Jen)", [
    ("23 minutes total  (13 min RFA,  1 hr total)",  0, None),
    ("Scan took 40 minutes",                         1, 'warn'),
    ("Optisign video NOT played",                    1, 'bad'),
    ("Refused scan-assist; accepted after trial",    1, 'warn'),
    ("Consent signed ✓",                            1, 'ok'),
    ("Sharps disposed of properly ✓",               1, 'ok'),
    ("Time-out performed out loud ✓",               1, 'ok'),
])

# ── BETHESDA ──────────────────────────────────────────────────────────────
section_slide("Bethesda", "May 13, 2026")

stats_slide("Bethesda", "26", "18", "3")

body_slide("Bethesda – Clinic Overview", [
    ("Front desk rooms all patients",                0, 'warn'),
    ("Techs prep RFAs independently",                0, 'warn'),
    ("Medications not labeled",                      0, 'bad'),
])

body_slide("Bethesda – Varithena + US (Rob)", [
    ("24 minutes total  (8 min for Varithena)",      0, None),
    ("All consents signed ✓",                        1, 'ok'),
    ("Varithena tray set-up efficient ✓",            1, 'ok'),
    ("Rob very outgoing with patient ✓",             1, 'ok'),
    ("Sharps disposed of properly ✓",               1, 'ok'),
    ("Time-out NOT performed out loud",              1, 'bad'),
])

body_slide("Bethesda – US Review", [
    ("14 minutes total",                             0, None),
    ("Findings thoroughly explained ✓",              1, 'ok'),
    ("Folder given by front desk ✓",                 1, 'ok'),
    ("Optisign video played ✓",                      1, 'ok'),
    ("Note completed properly ✓",                    1, 'ok'),
    ("No iPad available",                            1, 'bad'),
])

body_slide("Bethesda – RFA + US  (Dr. Green / Ruth – Training)", [
    ("40 minutes total  (14 min for RFA)",           0, None),
    ("Consent signed ✓",                             1, 'ok'),
    ("Sharps disposed of properly ✓",               1, 'ok'),
    ("Note completed ✓",                             1, 'ok'),
    ("Time-out NOT performed out loud",              1, 'bad'),
    ("Wrong note opened initially",                  1, 'bad'),
    ("US note not completed properly",               1, 'bad'),
])

# ── BOWIE ─────────────────────────────────────────────────────────────────
section_slide("Bowie", "May 14, 2026")

body_slide("Bowie – Clinic Overview", [
    ("Front desk rooms all patients",                0, 'warn'),
    ("RFA times are stretched",                      0, 'warn'),
    ("Techs prep RFAs independently",                0, 'warn'),
])

body_slide("Bowie – RFA + US  (Case 1)", [
    ("55 minutes total  (15 min for RFA)",                   0, None),
    ("Sharps disposed of properly ✓",                        1, 'ok'),
    ("Topical lidocaine used — no access issues ✓",          1, 'ok'),
    ("Time-out NOT performed out loud",                      1, 'bad'),
    ("16g needle used before intro documented",              1, 'bad'),
    ("Physician bent over during ablation",                  1, 'warn'),
    ("Sonographer assisting patient — limits availability",  1, 'warn'),
])

body_slide("Bowie – RFA + US  (Case 2)", [
    ("1.5 hours total  (RFA 35 min)",                        0, None),
    ("Sharps disposed of properly ✓",                        1, 'ok'),
    ("Time-out NOT performed out loud",                      1, 'bad'),
    ("RFA performed before post-scan",                       1, 'bad'),
    ("Multiple failed GSV attempts — switched to SSV",       1, 'warn'),
    ("Physician looked to observer for guidance",            1, 'warn'),
    ("US note not completed properly",                       1, 'bad'),
])

body_slide("Bowie – US Review", [
    ("10 minutes total",                             0, None),
    ("Findings thoroughly explained ✓",              1, 'ok'),
    ("Folder given by front desk ✓",                 1, 'ok'),
    ("Optisign video played ✓",                      1, 'ok'),
    ("Note completed ✓",                             1, 'ok'),
    ("No iPad available",                            1, 'bad'),
])

# ── SUMMARY ───────────────────────────────────────────────────────────────
summary_section_slide()

body_slide("Recurring Issues Across All Sites", [
    ("CRITICAL — Address Immediately",                                    0, 'bad'),
    ("Medications NOT labeled at Princeton, Bethesda, Bowie",             1, 'bad'),
    ("Time-out NOT performed out loud at multiple sites",                 1, 'bad'),
    ("OPERATIONAL CONCERNS",                                              0, 'warn'),
    ("Front desk rooming patients (Bethesda, Bowie)",                     1, 'warn'),
    ("Techs prepping RFAs independently (Bethesda, Bowie)",               1, 'warn'),
    ("No iPad for US reviews (Bethesda, Bowie)",                          1, 'warn'),
    ("Optisign video not played in some cases (Princeton RFA)",           1, 'warn'),
    ("POSITIVE OBSERVATIONS",                                             0, 'ok'),
    ("Sharps disposal consistently compliant across all sites",           1, 'ok'),
    ("Most consents signed",                                              1, 'ok'),
    ("Patient education thorough in US reviews",                          1, 'ok'),
])

body_slide("Action Items", [
    ("Label ALL medications — no exceptions",                             0, 'bad'),
    ("Reinforce time-out protocol — must be performed out loud",         0, 'bad'),
    ("Clarify front desk vs. tech rooming responsibilities",              0, 'warn'),
    ("Ensure Optisign video plays for every eligible patient",            0, 'warn'),
    ("Provide iPads at Bethesda and Bowie for US reviews",               0, 'warn'),
    ("Fix RFA documentation — correct note, complete US notes",          0, 'warn'),
    ("Coach McKinley on confidence and talk timing",                      0, 'warn'),
    ("Bowie: review RFA sequencing (post-scan must follow RFA)",         0, 'warn'),
])

c.save()
print(f"Saved: {out}")
