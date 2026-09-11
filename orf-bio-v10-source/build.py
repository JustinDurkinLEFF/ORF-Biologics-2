#!/usr/bin/env python3
"""
ORF Bio v10 static build — v9 structure/content + colour-field system.
src/pages/*.html + src/css/orf.css + src/js/orf.js + src/images  ->  dist/
Header and footer are baked into every page (v9 fetched them at runtime,
which fails when files are opened locally).
"""
import math, re, shutil, pathlib

ROOT = pathlib.Path(__file__).parent
SRC, DIST = ROOT / "src", ROOT / "dist"

NAVY, ORANGE, YELLOW, TEAL, SAGE, WHITE = "#0A2747", "#F26522", "#FFDE17", "#00546E", "#83B4B2", "#FFFFFF"

PAGES = [
    # slug, file, nav label, <title>, description
    ("index", "index.html", None, "ORF BIO • Next-Gen Biologics & Therapeutics",
     "We revolutionize the journey from molecule design to clinical manufacturing, with a vertically integrated business model offering everything you need under one roof."),
    ("therapeutics", "therapeutics.html", "Therapeutics", "Therapeutics • ORF BIO",
     "Our therapeutics are paving the way for revolutionary treatments."),
    ("pipeline", "pipeline.html", "Pipeline", "Pipeline • ORF BIO",
     "From rare disease and traumatic brain injury to oncology, regenerative medicine, inflammation, cell therapy, and beyond."),
    ("services", "services.html", "Services", "Services • ORF BIO",
     "We deliver hard-to-access or entirely novel biologics and rapidly prototype cellular disease models."),
    ("news", "news.html", "News", "News • ORF BIO", "Latest news and events from ORF Bio."),
    ("about", "about.html", "About", "About • ORF BIO",
     "We are reimagining next-generation therapeutics to bring modern solutions to patients everywhere."),
    ("registry", "registry.html", "Registry", "Rare Disease Tissue Registry • ORF BIO",
     "By providing essential resources for researchers, our registry advances the understanding and treatment of rare diseases."),
    ("contact", "contact.html", None, "Contact Us • ORF BIO",
     "Partner with ORF Bio to advance therapeutic treatments, or learn more about our work."),
    ("distributors", "distributors.html", "Distributors", "Distributors • ORF BIO",
     "We offer our legacy products through distributors around the globe."),
]
NAV = [p for p in PAGES if p[2]]
CUR = ' aria-current="page"'

ARROW = ('<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3.5 10h12.5M11 5l5 5-5 5" fill="none" '
         'stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>')
LINKEDIN = ('<svg viewBox="0 0 382 382" aria-hidden="true"><path fill="currentColor" d="M347.4 0H34.6C15.5 0 0 15.5 0 34.6v312.8C0 366.5 15.5 382 34.6 382h312.8c19.1 0 34.6-15.5 34.6-34.6V34.6C382 15.5 366.5 0 347.4 0zM118.2 329.8c0 5.6-4.5 10.1-10.1 10.1H65.3c-5.6 0-10.1-4.5-10.1-10.1V150.4c0-5.6 4.5-10.1 10.1-10.1h42.8c5.6 0 10.1 4.5 10.1 10.1v179.4zM86.7 123.4c-22.5 0-40.7-18.2-40.7-40.7S64.3 42.1 86.7 42.1s40.7 18.2 40.7 40.7-18.2 40.6-40.7 40.6zM341.9 330.7c0 5.1-4.1 9.2-9.2 9.2h-45.9c-5.1 0-9.2-4.1-9.2-9.2v-84.2c0-12.6 3.7-55-32.8-55-28.3 0-34.1 29.1-35.2 42.1v97.1c0 5.1-4.1 9.2-9.2 9.2h-44.4c-5.1 0-9.2-4.1-9.2-9.2V149.6c0-5.1 4.1-9.2 9.2-9.2h44.4c5.1 0 9.2 4.1 9.2 9.2v15.7c10.5-15.8 26.1-27.9 59.3-27.9 73.6 0 73.1 68.7 73.1 106.5v86.8z"/></svg>')

def logo(where):
    if where == "footer":
        return '<span class="logo"><img src="images/logo-white-footer.png" width="1599" height="405" alt="ORF Bio"></span>'
    return '<span class="logo"><img src="images/logo-white-nav.png" width="859" height="218" alt="ORF Bio"></span>'

# ---------------------------------------------------------------------------
# Generative art
# ---------------------------------------------------------------------------
def antibody(x, y, s=1.0, rot=0, heavy=NAVY, light=None, cls="", style=""):
    light = light or heavy
    c = f' class="{cls}"' if cls else ""
    st = f' style="{style}"' if style else ""
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})"><g{c}{st}>'
            f'<rect x="-9" y="2" width="18" height="54" rx="9" fill="{heavy}"/>'
            f'<g transform="rotate(-36 0 6)"><rect x="-9" y="-54" width="18" height="60" rx="9" fill="{heavy}"/>'
            f'<rect x="-24" y="-50" width="12" height="36" rx="6" fill="{light}"/></g>'
            f'<g transform="rotate(36 0 6)"><rect x="-9" y="-54" width="18" height="60" rx="9" fill="{heavy}"/>'
            f'<rect x="12" y="-50" width="12" height="36" rx="6" fill="{light}"/></g></g></g>')

def cubic(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d for a, b, c, d in zip(p0, p1, p2, p3))

def strands():
    paths = [
        [(-30, 390), (140, 300), (220, 110), (380, 160), (540, 210), (560, 60), (640, 40)],
        [(-30, 110), (120, 170), (250, 370), (420, 300), (560, 240), (560, 420), (640, 400)],
        [(-30, 260), (160, 250), (290, 190), (420, 230), (540, 266), (570, 190), (640, 170)],
    ]
    out, defs = [], []
    for i, p in enumerate(paths):
        d = f"M{p[0][0]} {p[0][1]} C{p[1][0]} {p[1][1]} {p[2][0]} {p[2][1]} {p[3][0]} {p[3][1]} C{p[4][0]} {p[4][1]} {p[5][0]} {p[5][1]} {p[6][0]} {p[6][1]}"
        defs.append(f'<path id="st{i}" d="{d}"/>')
        out.append(f'<use href="#st{i}" fill="none" stroke="rgba(131,180,178,.55)" stroke-width="{2.5 - i * .5}"/>')
        for seg in (p[0:4], p[3:7]):
            for t in (.18, .42, .66, .9):
                x, y = cubic(*seg, t)
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5 + (i % 2) * 2}" fill="rgba(131,180,178,.4)"/>')
        for b in range(3):
            col = [YELLOW, ORANGE, WHITE][(i + b) % 3]
            r = [11, 8, 6][b]
            dur = 9 + i * 2.5 + b
            out.append(f'<circle r="{r}" fill="{col}"><animateMotion dur="{dur}s" begin="-{b * dur / 3 + i:.1f}s" repeatCount="indefinite"><mpath href="#st{i}"/></animateMotion></circle>')
    return f'<svg viewBox="0 0 600 480" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><defs>{"".join(defs)}</defs>{"".join(out)}</svg>'

def antibodies_tile():
    parts = [
        '<circle cx="470" cy="120" r="70" fill="none" stroke="rgba(255,255,255,.5)" stroke-width="3"/>',
        '<circle cx="110" cy="380" r="46" fill="none" stroke="rgba(10,39,71,.18)" stroke-width="3"/>',
        '<circle cx="520" cy="400" r="18" fill="rgba(255,255,255,.7)"/>',
        '<circle cx="80" cy="110" r="10" fill="rgba(10,39,71,.35)"/>',
        antibody(300, 250, 2.6, -8, NAVY, "#FFFFFF", "tile__float", "--dl:0s"),
        antibody(120, 190, 1.1, -34, "#FFFFFF", NAVY, "tile__float", "--dl:-3s"),
        antibody(480, 300, 1.25, 28, "#FFFFFF", ORANGE, "tile__float", "--dl:-5s"),
        antibody(200, 410, .8, 150, NAVY, ORANGE, "tile__float", "--dl:-1.5s"),
        antibody(430, 90, .7, 200, NAVY, "#FFFFFF", "tile__float", "--dl:-6s"),
    ]
    return f'<svg viewBox="0 0 600 480" preserveAspectRatio="xMidYMid slice" aria-hidden="true">{"".join(parts)}</svg>'

def cells_art(seed=3):
    import random
    rnd = random.Random(seed)
    parts = []
    for _ in range(26):
        x, y, r = rnd.uniform(-20, 660), rnd.uniform(-20, 380), rnd.choice([8, 12, 16, 22, 30, 44, 60])
        col = rnd.choice(["rgba(10,39,71,.35)", "rgba(255,255,255,.7)", "rgba(0,84,110,.45)"])
        parts.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="none" stroke="{col}" stroke-width="{rnd.choice([2, 3, 4])}"/>')
        if rnd.random() < .4:
            parts.append(f'<circle cx="{x + r * .2:.0f}" cy="{y - r * .15:.0f}" r="{r * .32:.0f}" fill="{col}"/>')
    parts.append('<circle cx="400" cy="170" r="54" fill="#FFDE17"/><circle cx="412" cy="160" r="18" fill="#F26522"/>')
    return f'<svg viewBox="0 0 640 360" preserveAspectRatio="xMidYMid slice" aria-hidden="true">{"".join(parts)}</svg>'

def glyph(kind):
    vb = '0 0 320 200'
    e = []
    if kind == "neuro":
        ends = [(62, 52), (48, 122), (104, 172), (236, 40), (272, 104), (222, 170)]
        for (x, y) in ends:
            e.append(f'<path d="M160 100 Q{(160 + x) / 2 + 12:.0f} {(100 + y) / 2 - 10:.0f} {x} {y}" fill="none" stroke="{NAVY}" stroke-width="5" stroke-linecap="round"/>')
            e.append(f'<path d="M{x} {y} l{-18 if x < 160 else 18} {-14} M{x} {y} l{-20 if x < 160 else 20} {12}" fill="none" stroke="{NAVY}" stroke-width="3" stroke-linecap="round"/>')
            e.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{NAVY}"/>')
        e.append(f'<circle cx="160" cy="100" r="30" fill="{NAVY}"/>')
        e.append(f'<circle cx="166" cy="94" r="11" fill="{YELLOW}"/>')
    elif kind == "rare":
        for i in range(22):
            a, rad = i * 2.39996, 19 * math.sqrt(i + .3)
            x, y = 160 + math.cos(a) * rad * 1.35, 100 + math.sin(a) * rad * .92
            fill = NAVY if i % 5 == 0 else "none"
            e.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="{fill}" stroke="{NAVY}" stroke-width="3.5"/>')
        e.append(f'<circle cx="160" cy="100" r="7" fill="{ORANGE}"/>')
    elif kind == "onco":
        e.append('<circle cx="72" cy="150" r="46" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="3"/>')
        e.append('<circle cx="262" cy="56" r="30" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="3"/>')
        e.append(antibody(160, 108, 1.35, 0, YELLOW, WHITE))
        for (x, y) in [(112, 40), (208, 40), (150, 186), (170, 186)]:
            e.append(f'<circle cx="{x}" cy="{y}" r="8" fill="{ORANGE}"/>')
    elif kind == "wound":
        pts = []
        for r in range(4):
            for c in range(7):
                x = 50 + c * 37 + (18 if r % 2 else 0)
                y = 40 + r * 40
                pts.append((x, y))
        links = []
        for i, (x, y) in enumerate(pts):
            for (x2, y2) in pts[i + 1:]:
                if 30 < math.hypot(x2 - x, y2 - y) < 46:
                    links.append(f'M{x} {y}L{x2} {y2}')
        e.append(f'<path d="{"".join(links)}" stroke="{NAVY}" stroke-width="2.5" stroke-linecap="round" fill="none"/>')
        for i, (x, y) in enumerate(pts):
            e.append(f'<circle cx="{x}" cy="{y}" r="{8 if i % 6 == 0 else 5}" fill="{WHITE if i % 6 == 0 else NAVY}"/>')
    elif kind == "animal":
        e.append(f'<circle cx="160" cy="100" r="88" fill="none" stroke="rgba(131,180,178,.4)" stroke-width="3"/>')
        e.append(f'<ellipse cx="160" cy="124" rx="40" ry="33" fill="{YELLOW}"/>')
        for (x, y, r) in [(110, 80, 16), (138, 54, 17), (182, 54, 17), (210, 80, 16)]:
            e.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{YELLOW}"/>')
        e.append(f'<circle cx="160" cy="124" r="10" fill="{ORANGE}"/>')
    elif kind == "growth":
        vb = '0 0 200 200'
        for (x, y, r, c) in [(100, 100, 40, NAVY), (58, 78, 26, ORANGE), (142, 74, 28, TEAL), (60, 136, 24, TEAL), (140, 138, 30, ORANGE), (100, 46, 18, NAVY), (100, 158, 16, NAVY)]:
            e.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" stroke="var(--bg)" stroke-width="5"/>')
    elif kind == "fusion":
        vb = '0 0 200 200'
        e.append(f'<circle cx="58" cy="118" r="40" fill="{NAVY}"/>')
        e.append(f'<path d="M92 100 l10 -14 l10 14 l10 -14 l10 14" fill="none" stroke="{NAVY}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
        e.append(f'<rect x="126" y="42" width="54" height="104" rx="27" fill="{ORANGE}"/>')
        e.append(f'<circle cx="153" cy="72" r="10" fill="var(--bg)"/>')
    elif kind == "antibody":
        vb = '0 0 200 200'
        e.append(antibody(100, 104, 1.45, 0, NAVY, ORANGE))
    elif kind == "genomic":
        vb = '0 0 240 150'
        a, b = [], []
        for i in range(0, 241, 6):
            y1 = 75 + math.sin(i / 240 * math.pi * 3) * 44
            y2 = 75 - math.sin(i / 240 * math.pi * 3) * 44
            a.append(f'{i},{y1:.1f}'); b.append(f'{i},{y2:.1f}')
        for i in range(12, 240, 20):
            y1 = 75 + math.sin(i / 240 * math.pi * 3) * 44
            y2 = 75 - math.sin(i / 240 * math.pi * 3) * 44
            e.append(f'<line x1="{i}" y1="{y1:.1f}" x2="{i}" y2="{y2:.1f}" stroke="rgba(255,255,255,.3)" stroke-width="3"/>')
        e.append(f'<polyline points="{" ".join(a)}" fill="none" stroke="{YELLOW}" stroke-width="5" stroke-linecap="round"/>')
        e.append(f'<polyline points="{" ".join(b)}" fill="none" stroke="{ORANGE}" stroke-width="5" stroke-linecap="round"/>')
    elif kind == "tissue":
        vb = '0 0 240 150'
        for r in range(4):
            for c in range(7):
                x, y = 22 + c * 33 + (16 if r % 2 else 0), 20 + r * 36
                e.append(f'<circle cx="{x}" cy="{y}" r="17" fill="none" stroke="{SAGE if (r + c) % 3 else YELLOW}" stroke-width="3.5"/>')
                if (r * 7 + c) % 4 == 0:
                    e.append(f'<circle cx="{x + 3}" cy="{y - 2}" r="6" fill="{ORANGE}"/>')
    elif kind == "blood":
        vb = '0 0 240 160'
        e.append(f'<path d="M120 12 C148 52 170 78 170 106 A50 50 0 0 1 70 106 C70 78 92 52 120 12Z" fill="{ORANGE}"/>')
        for (x, y, r, c) in [(104, 104, 14, YELLOW), (138, 96, 10, NAVY), (124, 128, 9, YELLOW), (36, 60, 12, SAGE), (206, 50, 16, SAGE), (212, 118, 9, YELLOW), (30, 124, 8, YELLOW)]:
            e.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>')
    elif kind == "k-academic":
        vb = '0 0 48 48'
        e = [f'<circle cx="24" cy="24" r="20" fill="none" stroke="{NAVY}" stroke-width="3"/>', f'<circle cx="24" cy="24" r="9" fill="{NAVY}"/>']
    elif kind == "k-biotech":
        vb = '0 0 48 48'
        e = [antibody(24, 26, .36, 0, NAVY, ORANGE)]
    elif kind == "k-advocacy":
        vb = '0 0 48 48'
        e = [f'<circle cx="17" cy="24" r="13" fill="none" stroke="{NAVY}" stroke-width="3"/>', f'<circle cx="31" cy="24" r="13" fill="{NAVY}"/>']
    elif kind == "k-preclinical":
        vb = '0 0 48 48'
        e = [f'<circle cx="24" cy="24" r="20" fill="none" stroke="{NAVY}" stroke-width="3"/>',
             f'<circle cx="18" cy="20" r="4" fill="{NAVY}"/>', f'<circle cx="29" cy="17" r="3" fill="{NAVY}"/>',
             f'<circle cx="27" cy="30" r="5" fill="{ORANGE}"/>', f'<circle cx="16" cy="31" r="2.5" fill="{NAVY}"/>']
    staggered = []
    for i, el in enumerate(e):
        m = re.match(r'<(\w+)', el)
        staggered.append(el[:m.end()] + f' style="--i:{i}"' + el[m.end():])
    cls = ' class="kind__glyph"' if kind.startswith("k-") else ""
    return f'<svg{cls} viewBox="{vb}" aria-hidden="true">{"".join(staggered)}</svg>'

def orbit():
    cx, cy = 450, 330
    programs = [("Neuroscience", ORANGE, True), ("Rare disease", YELLOW, True), ("Oncology", SAGE, True),
                ("Wound healing", WHITE, True), ("Infectious disease", None, False), ("Metabolic disease", None, False),
                ("Animal Health", SAGE, True)]
    spokes, nodes, labels, pulses = [], [], [], []
    n = len(programs)
    for i, (name, col, live) in enumerate(programs):
        a = math.radians(-90 + i * 360 / n)
        c, s = math.cos(a), math.sin(a)
        x1, y1 = cx + c * 112, cy + s * 112
        x2, y2 = cx + c * 232, cy + s * 232
        spokes.append(f'<line class="orbit__spoke" style="--i:{i}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
        if live:
            nodes.append(f'<circle class="orbit__node" style="--i:{i}" cx="{x2:.1f}" cy="{y2:.1f}" r="14" fill="{col}"/>')
            pulses.append(f'<circle r="4.5" fill="{YELLOW}" opacity="0"><animateMotion dur="2.6s" begin="{1.4 + i * .37:.2f}s" repeatCount="indefinite" path="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}"/><animate attributeName="opacity" values="0;1;1;0" dur="2.6s" begin="{1.4 + i * .37:.2f}s" repeatCount="indefinite"/></circle>')
        else:
            nodes.append(f'<circle class="orbit__node" style="--i:{i}" cx="{x2:.1f}" cy="{y2:.1f}" r="12" fill="#0A2747" stroke="rgba(255,255,255,.55)" stroke-width="2.5" stroke-dasharray="4 4"/>')
        lx, ly = cx + c * 262, cy + s * 262
        if abs(c) < .3:
            anchor, ly = "middle", ly + (-6 if s < 0 else 26)
        else:
            anchor, ly = ("start" if c > 0 else "end"), ly + 7
        fill = "#FFFFFF" if live else "rgba(255,255,255,.6)"
        sub = '' if live else f'<tspan x="{lx:.1f}" dy="24" font-size="15" font-weight="400" fill="rgba(255,255,255,.55)">In development</tspan>'
        labels.append(f'<text class="orbit__label" style="--i:{i}" x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" font-size="21" font-weight="500" fill="{fill}">{name}{sub}</text>')
    hub = (f'<circle cx="{cx}" cy="{cy}" r="104" fill="{YELLOW}"/>'
           f'<text x="{cx}" y="{cy - 18}" text-anchor="middle" font-size="24" font-weight="600" fill="{NAVY}" letter-spacing="-.5">Central</text>'
           f'<text x="{cx}" y="{cy + 10}" text-anchor="middle" font-size="24" font-weight="600" fill="{NAVY}" letter-spacing="-.5">biologics</text>'
           f'<text x="{cx}" y="{cy + 38}" text-anchor="middle" font-size="24" font-weight="600" fill="{NAVY}" letter-spacing="-.5">capability</text>')
    return (f'<svg class="orbit" data-inview viewBox="0 0 900 660" role="img" aria-label="Hub-and-spoke diagram: a central biologics capability supporting programs in neuroscience, rare disease, oncology, wound healing and animal health, with infectious and metabolic disease in development.">'
            f'<circle class="orbit__ring" cx="{cx}" cy="{cy}" r="232"/><circle cx="{cx}" cy="{cy}" r="150" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="1.5"/>'
            f'{"".join(spokes)}{"".join(pulses)}{"".join(nodes)}{hub}{"".join(labels)}</svg>')

# ---------------------------------------------------------------------------
# Partials
# ---------------------------------------------------------------------------
def culture(density=1):
    return (f'<div class="culture" data-culture data-density="{density}" aria-hidden="true">'
            '<div class="culture__blob culture__blob--a"></div><div class="culture__blob culture__blob--b"></div>'
            '<canvas></canvas></div>')

def nav(slug):
    links = "".join(f'<a class="nav__link" href="{f}"{CUR if s == slug else ""}>{label}</a>' for s, f, label, *_ in NAV)
    mlinks = "".join(f'<li><a href="{f}" style="--i:{i}"{CUR if s == slug else ""}>{label}</a></li>'
                     for i, (s, f, label, *_) in enumerate(NAV + [("contact", "contact.html", "Contact")]))
    return f'''<header class="nav">
  <div class="nav__bar">
    <a href="index.html" aria-label="ORF Bio home">{logo("nav")}</a>
    <nav class="nav__links" aria-label="Primary">{links}</nav>
    <a class="btn btn--sm nav__cta" href="contact.html"{CUR if slug == "contact" else ""}>Contact</a>
    <button class="nav__burger" type="button" aria-expanded="false" aria-controls="menu"><span class="sr">Menu</span><i></i><i></i></button>
  </div>
</header>
<div class="menu" id="menu" data-surface="navy" hidden>
  <nav aria-label="Mobile"><ul class="menu__list">{mlinks}</ul></nav>
  <div class="menu__foot"><a href="mailto:contact@orfbio.com">contact@orfbio.com</a><span>1110 Tall Grass Ave., Tiffin, IA 52340</span></div>
</div>'''

def footer():
    return f'''<footer class="footer" data-surface="navy">
  <div class="wrap">
    <div class="footer__grid">
      <div class="footer__brand">
        <a href="index.html" aria-label="ORF Bio home">{logo("footer")}</a>
        <address>1110 Tall Grass Ave.<br>Tiffin, IA 52340<br><a href="mailto:contact@orfbio.com">contact@orfbio.com</a></address>
      </div>
      <ul class="footer__list">
        <li><a href="https://orfbiologics.com/shop/">Legacy Products</a></li>
        <li><a href="distributors.html">Distributors</a></li>
        <li><a href="registry.html#patients">Information for Patients</a></li>
      </ul>
      <ul class="footer__list">
        <li><a class="footer__social" href="https://www.linkedin.com/company/orf-biologics-inc/" target="_blank" rel="noopener">{LINKEDIN}LinkedIn</a></li>
      </ul>
      <a class="btn btn--accent footer__contact" href="contact.html">Contact Us <span class="btn__icon">{ARROW}</span></a>
    </div>
    <div class="footer__legal"><p>© 2026 ORF Bio. All rights reserved.</p><a href="#" data-todo="Privacy policy URL">Privacy Policy</a></div>
  </div>
</footer>'''

def hero(title, sub=None, short=False, density=.8):
    s = f'\n    <p class="page-sub hero__rise" style="--d:.4s">{sub}</p>' if sub else ""
    cls = "hero hero--page hero--short" if short else "hero hero--page"
    return f'''<section class="{cls}" data-theme="paper" data-surface="sun" aria-labelledby="page-title">
  {culture(density)}
  <div class="wrap">
    <h1 class="d-page page-title" id="page-title"><span class="hero__line"><span style="--d:.05s">{title}</span></span></h1>{s}
  </div>
</section>'''

def placeholder(ratio):
    return f'<div class="ph" aria-hidden="true"></div><span class="ph__label" aria-hidden="true"><span>Image placeholder</span><span>{ratio}</span></span>'

def go(href, label):
    return f'<a class="go" href="{href}" aria-label="{label}">{ARROW}</a>'

TOKENS = {
    "arrow": lambda a: ARROW,
    "culture": lambda a: culture(float(a) if a else 1),
    "strands": lambda a: strands(),
    "antibodies": lambda a: antibodies_tile(),
    "cells": lambda a: cells_art(int(a) if a else 3),
    "ph": lambda a: placeholder(a or "4:3"),
    "glyph": lambda a: glyph(a),
    "orbit": lambda a: orbit(),
}

def expand(text):
    text = re.sub(r"\{\{\s*hero\|([^|}]*)\|?([^|}]*)\|?(short)?\s*\}\}",
                  lambda m: hero(m.group(1), m.group(2) or None, bool(m.group(3))), text)
    text = re.sub(r"\{\{\s*go\|([^|}]*)\|([^}]*)\}\}", lambda m: go(m.group(1), m.group(2)), text)
    return re.sub(r"\{\{\s*([a-z]+)(?::([a-z0-9.:\-]+))?\s*\}\}", lambda m: TOKENS[m.group(1)](m.group(2)), text)

def build():
    if DIST.exists(): shutil.rmtree(DIST)
    (DIST / "css").mkdir(parents=True); (DIST / "js").mkdir()
    shutil.copy(SRC / "css/orf.css", DIST / "css/orf.css")
    shutil.copy(SRC / "js/orf.js", DIST / "js/orf.js")
    shutil.copytree(SRC / "images", DIST / "images")
    for slug, fname, label, title, desc in PAGES:
        body = expand((SRC / "pages" / fname).read_text())
        page = f'''<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0A2747">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<link rel="preconnect" href="https://use.typekit.net" crossorigin>
<link rel="stylesheet" href="https://use.typekit.net/idg1sih.css">
<link rel="stylesheet" href="css/orf.css">
<script>(function(h){{h.classList.remove('no-js');h.classList.add('js');if('IntersectionObserver'in window)h.classList.add('morph');}})(document.documentElement);</script>
</head>
<body data-page="{slug}" data-theme="paper">
<a class="skip" href="#main">Skip to content</a>
{nav(slug)}
<main id="main">
{body}
</main>
{footer()}
<script src="js/orf.js"></script>
</body>
</html>
'''
        (DIST / fname).write_text(page)
        print(f"built {fname:20s} {len(page) / 1024:6.1f} KB")

if __name__ == "__main__":
    build()
