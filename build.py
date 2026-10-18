#!/usr/bin/env python3
"""
Static site generator for oversightengineering.com

Writes plain HTML into docs/ (the GitHub Pages publish root).
Run:  python3 build.py
No dependencies. Re-run after editing the PAGES content below.

NOT PUBLISHED: this file, EVIDENCE-CHECKLIST.md, DEPLOY.md and README.md sit
outside docs/, so GitHub Pages never serves them.
"""

import html
import os
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).parent
OUT = pathlib.Path(os.environ.get("SITE_OUT") or ROOT / "docs")

SITE = {
    "domain": "oversightengineering.com",
    "base": "https://oversightengineering.com",
    "name": "Pravin Khandke",
    "tagline": "Applied researcher and systems architect",
    "field": "Human-in-the-Loop AI and Autonomous Agent Systems for Collaborative Workflows",
    "email": "pravin.khandke@ieee.org",
    "orcid": "https://orcid.org/0009-0004-9693-9334",
    "orcid_id": "0009-0004-9693-9334",
    "updated": "18 October 2026",
    "photo_w": "370",
    "photo_h": "480",
}

# Articles shown on the Writing page. The page, the nav item, the home card and the
# related links exist only while this list has entries. SITE_ARTICLES=none empties it,
# which the tests use to prove the page stays hidden.
ARTICLES = [
    {"title": "Feature Flags That Actually Ship: Lessons from the Trenches",
     "platform": "Dev.to",
     "url": "https://dev.to/pravin-khandke/feature-flags-that-actually-ship-lessons-from-the-trenches-b7a"},
    {"title": "Messaging in the Age of AI",
     "platform": "Dev.to",
     "url": "https://dev.to/pravin-khandke/messaging-in-the-age-of-ai-26h7"},
    {"title": "Clean Code at Scale: How Sonar Became Our Silent Reviewer",
     "platform": "Hashnode",
     "url": "https://pravin-khandke.hashnode.dev/clean-code-at-scale-how-sonar-became-our-silent-reviewer"},
    {"title": "The Emergence of Explainable AI in Deep Learning",
     "platform": "Hashnode",
     "url": "https://pravin-khandke.hashnode.dev/the-emergence-of-explainable-ai-in-deep-learning-bridging-the-gap-between-model-complexity-and-human-trust"},
    {"title": "Backend Architecture in the Age of AI",
     "platform": "Medium",
     "url": "https://medium.com/@Pravin-Khandke/backend-architecture-in-the-age-of-ai-e73cc8bbf599"},
]
if os.environ.get("SITE_ARTICLES") == "none":
    ARTICLES = []

# One table drives the nav, the sub-tab strip and the "current page" marker.
# label, landing page, pages that mark the item current
NAV_GROUPS = [
    ("Home", "", [""]),
    ("Career", "career/", ["career/"]),
    ("Work", "invention/", ["invention/", "consultancy/"]),
    ("Mentoring", "mentoring/", ["mentoring/", "inspiring/"]),
    ("Community", "standing/", ["standing/", "memberships/"]),
    ("Papers and talks", "publications/", ["publications/", "talks/"]),
    ("Peer review", "peer-review/", ["peer-review/"]),
]
if ARTICLES:
    NAV_GROUPS.append(("Writing", "writing/", ["writing/"]))

PAGE_LABELS = {
    "invention/": "Invention",
    "consultancy/": "Consultancy",
    "mentoring/": "Mentoring",
    "inspiring/": "Inspiring others",
    "career/": "Career",
    "standing/": "Standing",
    "memberships/": "Memberships",
    "publications/": "Publications",
    "talks/": "Talks",
    "peer-review/": "Peer review",
    "writing/": "Writing",
}

# Pages offered under "Related" in each page's sidebar.
RELATED = {
    "invention/": ["consultancy/", "publications/"],
    "consultancy/": ["invention/", "mentoring/"],
    "mentoring/": ["inspiring/", "standing/", "consultancy/"],
    "inspiring/": ["mentoring/", "standing/", "talks/"],
    "career/": ["consultancy/", "invention/"],
    "standing/": ["talks/", "peer-review/", "memberships/"],
    "memberships/": ["standing/", "publications/"],
    "publications/": ["talks/", "writing/"],
    "talks/": ["publications/", "standing/"],
    "peer-review/": ["standing/", "memberships/"],
    "writing/": ["publications/", "talks/"],
}

# Alt text and caption for every image that is not decorative card art, keyed by file
# name under docs/assets/img/. An image the pages reference (through figure or thumb) with no entry here stops the build.
# An unreferenced file is ignored.
IMAGES = {
    "diagram-reconciliation.svg": (
        "Diagram. Payments arrive through four channels and feed one step that reads each "
        "payment and scores every field. High confidence matches are assigned automatically. "
        "Middle band matches go to a person who chooses. Low confidence matches go to manual "
        "review. Every check and override is logged.",
        "How a payment moves through the pipeline. Schematic."),
    "diagram-strangler.svg": (
        "Diagram. Three stages from start to end. The legacy mainframe block shrinks while the "
        "block of new services grows, and a band underneath states that dealer operations "
        "continue throughout.",
        "Retiring the platform service by service. Schematic, not to scale."),
}

# ----------------------------------------------------------------------------
# shared fragments
# ----------------------------------------------------------------------------

IDENTIFIERS = """
<ul class="ids">
  <li><span class="k">ORCID</span> <a href="https://orcid.org/0009-0004-9693-9334">0009-0004-9693-9334</a></li>
  <li><span class="k">Email</span> <a href="mailto:pravin.khandke@ieee.org">pravin.khandke@ieee.org</a></li>
  <li><span class="k">IEEE</span> Senior Member #102303821</li>
  <li><span class="k">LinkedIn</span> <a href="https://www.linkedin.com/in/pravin-khandke">linkedin.com/in/pravin-khandke</a></li>
</ul>
"""

FOOTER = """
<footer class="site-footer">
  <div class="wrap">
    <p class="foot-line">{name}, {field}</p>
    <ul class="foot-links">
      <li><a href="https://orcid.org/0009-0004-9693-9334">ORCID</a></li>
      <li><a href="https://www.linkedin.com/in/pravin-khandke">LinkedIn</a></li>
      <li><a href="mailto:{email}">{email}</a></li>
    </ul>
    <p class="foot-line small">
      This site is the public record of the work cited in my fellowship application.
      It was last reviewed on {updated}. Where a claim rests on a document held by a
      third party, that document is linked rather than reproduced.
    </p>
  </div>
</footer>
"""

def page_key(path: str) -> str:
    return path[:-len("index.html")] if path.endswith("index.html") else path


def nav(key: str) -> str:
    out = []
    for label, landing, members in NAV_GROUPS:
        cur = ' aria-current="page"' if key in members else ""
        out.append(f'      <li><a href="/{landing}"{cur}>{label}</a></li>')
    return '<ul class="nav-list">\n' + "\n".join(out) + "\n    </ul>"


def subtabs(key: str) -> str:
    """A tab strip under the header for pages that share a nav item with a sibling."""
    for _, _, members in NAV_GROUPS:
        if key in members and len(members) > 1:
            items = []
            for m in members:
                cur = ' aria-current="page"' if m == key else ""
                items.append(f'<li><a href="/{m}"{cur}>{PAGE_LABELS[m]}</a></li>')
            return ('<nav class="subtabs" aria-label="In this section"><div class="wrap">'
                    "<ul>" + "".join(items) + "</ul></div></nav>")
    return ""


def add_sidebar(key: str, body: str) -> str:
    """Give each h2 an id and add an 'On this page' and 'Related' sidebar to the wrap."""
    if '<div class="wrap">' not in body:
        return body
    heads, used = [], set()

    def tag(m):
        text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
        slug, n = base, 2
        while slug in used:
            slug, n = f"{base}-{n}", n + 1
        used.add(slug)
        heads.append((slug, text))
        return f'<h2 id="{slug}">{m.group(1)}</h2>'

    body = re.sub(r"<h2>(.*?)</h2>", tag, body, flags=re.S)
    on_page = "".join(f'<li><a href="#{s}">{html.escape(t)}</a></li>' for s, t in heads)
    related = "".join(
        f'<li><a href="/{k}">{PAGE_LABELS[k]}</a></li>'
        for k in RELATED.get(key, []) if k != "writing/" or ARTICLES
    )
    aside = ('<aside class="side" aria-label="Page navigation">'
             f'<p class="side-h">On this page</p><ul>{on_page}</ul>'
             f'<p class="side-h">Related</p><ul>{related}</ul></aside>')
    body = body.replace('<div class="wrap">', '<div class="wrap topic">', 1)
    end = body.rfind("</div>")
    return body[:end] + aside + "\n" + body[end:]


BASE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="{name}">
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet">
<link rel="canonical" href="{base}/{canon}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{base}/{canon}">
<meta property="og:image" content="https://oversightengineering.com/assets/img/profile.jpg">
<meta property="og:image:alt" content="Pravin Khandke, headshot">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=Spectral:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/">
      <span class="brand-name">{name}</span>
      <span class="brand-sub">{tagline}</span>
    </a>
    <nav class="site-nav" aria-label="Primary">
{nav}
    </nav>
  </div>
</header>
<main id="main">
{subtabs}
{body}
</main>
{footer}
</body>
</html>
"""

# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def ext(href: str, label=None, note=None) -> str:
    """External evidence link with a visible marker so a reader can see the source."""
    lab = html.escape(label or href)
    tail = f' <span class="src-note">{html.escape(note)}</span>' if note else ""
    return (f'<a class="src" href="{html.escape(href)}" rel="noopener">{lab}'
            f'<span class="ext" aria-hidden="true">&nbsp;&#8599;</span></a>{tail}')

def claim(text: str, sources: list[str]) -> str:
    return (f'<li><span class="claim-text">{text}</span>\n'
            f'      <span class="claim-src">Source: {" \u00b7 ".join(sources)}</span></li>')

def _image(name: str):
    """(alt, caption) for an image file, or None while the file is absent.
    An image the pages reference with no IMAGES entry stops the build, so nothing ships without alt text."""
    if not (OUT / "assets" / "img" / name).exists():
        return None
    if name not in IMAGES:
        raise SystemExit(f"{name} is in docs/assets/img but has no entry in IMAGES. "
                         "Add its alt text and caption to IMAGES in build.py, then rebuild.")
    return IMAGES[name]


def figure(name: str) -> str:
    """A captioned image. Renders nothing until the file exists."""
    meta = _image(name)
    if meta is None:
        return ""
    alt, caption = meta
    return (f'<figure class="figure"><img src="/assets/img/{name}" '
            f'alt="{html.escape(alt, quote=True)}" loading="lazy">'
            f'<figcaption>{html.escape(caption)}</figcaption></figure>')


def thumb(name: str) -> str:
    """A small image for a talk card. Renders nothing until the file exists."""
    meta = _image(name)
    if meta is None:
        return ""
    return (f'<img class="talk-img" src="/assets/img/{name}" '
            f'alt="{html.escape(meta[0], quote=True)}" loading="lazy">')


def card(href: str, title: str, text: str, variant: int, art=None) -> str:
    """A home page card. The art is decorative, so its alt text is empty."""
    inner = ""
    if art and (OUT / "assets" / "img" / art).exists():
        inner = f'<img src="/assets/img/{art}" alt="" width="640" height="360" loading="lazy">'
    return (f'<a class="card" href="{href}">'
            f'<span class="card-art art-{variant}">{inner}</span>'
            f'<span class="card-body"><span class="card-title">{html.escape(title)}</span>'
            f'<span class="card-text">{html.escape(text)}</span>'
            f'<span class="more">Read more</span></span></a>')


def case_study(title, tagline, bullets, tags, sources, dates=None, art="") -> str:
    """A case-study block. Sources are already-built link strings from ext()."""
    when = f'<p class="case-dates">{html.escape(dates)}</p>' if dates else ""
    items = "".join(f"<li>{html.escape(b)}</li>" for b in bullets)
    chips = "".join(f"<span>{html.escape(t)}</span>" for t in tags)
    src = (f'<p class="claim-src">Source: {" · ".join(sources)}</p>' if sources else "")
    return (f'<article class="case">{when}<h3>{html.escape(title)}</h3>'
            f'<p class="case-tag">{html.escape(tagline)}</p><ul>{items}</ul>'
            f'<div class="tag-row">{chips}</div>{src}{art}</article>')


def page(path, title, desc, body):
    key = page_key(path)
    if key in PAGE_LABELS:
        body = add_sidebar(key, body)
    doc = BASE.format(
        title=title, desc=desc, name=SITE["name"], base=SITE["base"],
        tagline=SITE["tagline"], path=path, canon=key,
        nav=nav(key), subtabs=subtabs(key),
        body=body.strip(),
        footer=FOOTER.format(**SITE),
    )
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")
    return len(doc)

BUILT = []
def add(path, title, desc, body):
    n = page(path, title, desc, body)
    BUILT.append((path, n))

IJCA = "https://www.ijcaonline.org/"
SAS_VERIFY = "https://www.sassociety.com/membership-id-sas-sefm-770-2026/"
AIC_LIST = "https://scrs.in/conference/aic2026/speaker/talk/23186"
KIDS_REPO = "https://github.com/pravin-khandke/safe-ai-for-kids"
ORCID = "https://orcid.org/0009-0004-9693-9334"

# ============================================================================
# HOME
# ============================================================================

# name, location detail, url (None = no link, reason stated in the row)
VENUE_ROWS = [
    ("IECON 2026", "Doha, Qatar", "https://www.iecon2026.org/"),
    ("IEEE GLOBECOM 2026 CISS Symposium", "Macau, China", "https://globecom2026.ieee-globecom.org/"),
    ("ICCUBEA 2026", "Pune, India", "https://iccubea.pccoepune.com/iccubea.php"),
    ("ICETCI 2026", "Hyderabad, India", "http://www.ietcint.com/"),
    ("ICDCECE 2026", "Karnataka, India", "https://icdcece.in/"),
    ("AMLDS 2026", "Osaka, Japan", "https://amlds.site/"),
    ("NGSME 2026", "Vilamoura, Portugal", "https://sites.google.com/view/ngmse2026/home"),
    ("CAISAIS 2026", "Ajman, United Arab Emirates", "https://caisais26.ajman.ac.ae"),
    ("AIIoT 2026", "Seattle, United States", "https://worldaiiotcongress.org/technical-committee/"),
    ("CEECT 2026", "Bangkok, Thailand", "https://www.ceect.org/"),
    ("MeditCom 2026", "Cagliari, Italy", "https://meditcom2026.ieee-meditcom.org/"),
    ("ICoIAS 2026", "Qinhuangdao, China", "https://www.icias.org/index.html"),
    ("iSemantic 2026", "Semarang, Indonesia", "https://isemantic.dinus.ac.id/2026/"),
    ("INCOSST 2026", "Cirebon, Indonesia", "https://incosst.polteksci.ac.id/"),
    ("INTCEC 2026", "Kathmandu, Nepal", "https://intcec.org/"),
    ("ICTMOD 2026", "Paris, France", "https://ictmod-conference.com/"),
    ("ETECOM 2026", "Chennai, India", "https://ieee-etecom.org/"),
    ("SIME 2026", "Sousse, Tunisia", "https://sime-conf.org/committees/"),
    ("FOAN 2026", "Pisa, Italy", "https://foan.info/"),
    ("AI e-Health Workshop 2026", "New York, United States", "https://healthcom2026.ieee-healthcom.org/"),
    ("ICETM 2026", "New Jersey, United States", None),   # venue site returns 404
    ("CICBA 2026", "Malda, India", None),                # venue domain no longer resolves
    ("TEMSMET 2026", "", None),                          # no public listing in any record
    ("ARIIA 2026", "", None),
    ("ICNSBT 2026", "", None),
    ("CICA 2026", "", None),                             # reviewed as a book chapter
    ("ICAITech 2026", "", None),
    ("PlatCon 2026", "", None),
]

# committee name, venue detail, url (None = no link held)
COMMITTEE_ROWS = [
    ("AIIoT 2026", "IEEE World AI IoT Congress, Seattle, United States",
     "https://worldaiiotcongress.org/technical-committee/"),
    ("SIME 2026", "Sousse, Tunisia", "https://sime-conf.org/committees/"),
    ("NGSME 2026", "IEEE workshop, Vilamoura, Portugal",
     "https://sites.google.com/view/ngmse2026/home"),
]

# Reviewer certificates held on file. A conference that issues one has put its name to
# the review, so each row links the document itself rather than describing it.
# name in the venue row, what the certificate states, file under docs/assets/docs/
CERTIFICATE_ROWS = [
    ("IEEE SIME 2026", "Certificate of Recognition, technical reviewer. Sousse, Tunisia.",
     "reviewer-certificate-sime-2026.pdf"),
    ("IEEE TEMSMET 2026", "Certificate of Appreciation, reviewer. Hyderabad, India.",
     "reviewer-certificate-temsmet-2026.pdf"),
    ("ICETCI 2026", "Certificate of Appreciation, peer reviewer. Hyderabad, India.",
     "reviewer-certificate-icetci-2026.pdf"),
    ("ICDCECE 2026", "Certificate of Appreciation, reviewer. Ballari, India.",
     "reviewer-certificate-icdcece-2026.pdf"),
    ("ICNSBT 2026", "Certificate of Appreciation, paper reviewer. Kolkata, India.",
     "reviewer-certificate-icnsbt-2026.pdf"),
    ("INCOSST 2026", "Reviewer certificate. Cirebon, Indonesia.",
     "reviewer-certificate-incosst-2026.pdf"),
    ("AMLDS 2026", "Reviewer certificate. Osaka, Japan.",
     "reviewer-certificate-amlds-2026.pdf"),
]


def certificate_rows_html() -> str:
    """A row per certificate. A missing file stops the build, so no row links to nothing."""
    out = []
    for name, what, fname in CERTIFICATE_ROWS:
        if not (ROOT / "docs" / "assets" / "docs" / fname).exists():
            raise SystemExit(f"docs/assets/docs/{fname} is missing. Put the certificate "
                             "in place, or drop its row from CERTIFICATE_ROWS, then rebuild.")
        out.append(f'      <li class="cert-row">{html.escape(name)} '
                   f'<span class="where">{html.escape(what)}</span> '
                   f'<a class="src" href="/assets/docs/{fname}">certificate (PDF)</a></li>')
    return '\n'.join(out)


def venue_rows_html() -> str:
    out = []
    for name, where, url in VENUE_ROWS:
        if url:
            link = ext(url, "venue site")
            where_html = f' <span class="where">{html.escape(where)}</span>' if where else ""
            out.append(f'      <li class="venue-row">{html.escape(name)}{where_html} {link}</li>')
        else:
            reason = "no live listing" if not where else f'no live listing ({html.escape(where)})'
            out.append(f'      <li class="venue-row">{html.escape(name)} '
                       f'<span class="no-link">no link, {reason}</span></li>')
    return '\n'.join(out)

def committee_rows_html() -> str:
    out = []
    for name, where, url in COMMITTEE_ROWS:
        pill = '<span class="pill">Programme committee</span>'
        if url:
            link = ext(url, "committee page")
            out.append(f'      <li class="committee-row">{html.escape(name)} {pill} '
                       f'<span class="where">{html.escape(where)}</span> {link}</li>')
        else:
            out.append(f'      <li class="committee-row">{html.escape(name)} {pill} '
                       f'<span class="where">{html.escape(where)}</span></li>')
    return '\n'.join(out)

VERIFIED_DATE = "11 October 2026"

HIGHLIGHTS = [
    # sort key, label, text, [(url, link label)]
    ("2026-10", "October 2026", "Speaker at Extract Summit, Austin, Texas.",
     [("https://www.extractsummit.io/", "Extract Summit programme")]),
    ("2026-08", "August 2026",
     "Keynote at the IEEE 5th World Conference on Applied Intelligence and Computing, "
     "Jabalpur, India.",
     [(AIC_LIST, "Keynote talk page on the conference site")]),
    ("2026-07", "July 2026", "Became a Fellow of the Royal Statistical Society.",
     [("https://rss.org.uk/", "Royal Statistical Society")]),
    ("2026-06", "June 2026", "Elevated to IEEE Senior Member.",
     [("https://www.ieee.org/membership/senior-members.html", "IEEE, Senior Member grade")]),
    ("2026-06", "June 2026",
     "Conferred Eminent Fellow Member by The Scholars Academic and Scientific Society.",
     [(SAS_VERIFY, "Society verification page")]),
]


def highlights_html() -> str:
    rows = sorted(HIGHLIGHTS, key=lambda h: h[0], reverse=True)
    out = []
    for _, label, text, sources in rows:
        links = " · ".join(ext(u, l) for u, l in sources)
        out.append(f'      <li class="tl-item"><span class="tl-date">{html.escape(label)}</span>'
                   f'<span class="tl-text">{html.escape(text)}</span>'
                   f'<span class="claim-src">Source: {links}</span></li>')
    return '    <ol class="timeline">\n' + "\n".join(out) + "\n    </ol>"


# href, title, text, art variant, art file (decorative, optional)
HOME_CARDS = [
    ("/invention/", "Work",
     "A human-in-the-loop remittance pipeline and advisory work on retiring a mainframe platform.",
     1, "card-work.jpg"),
    ("/mentoring/", "Mentoring",
     "How I develop engineers inside my teams and through a university capstone.",
     2, "card-mentoring.jpg"),
    ("/standing/", "Community",
     "Standing in the community and the grades I hold, each with its public record.",
     3, "card-community.jpg"),
    ("/publications/", "Papers and talks",
     "Three peer-reviewed papers and the talks I have given, linked to the organiser's record.",
     4, "card-papers.jpg"),
    ("/peer-review/", "Peer review",
     "28 review venues and 3 committee appointments, each linked to its public listing where one exists.",
     5, "card-review.jpg"),
    ("/writing/", "Writing",
     "Technical articles for practising engineers on developer platforms.",
     6, "card-writing.jpg"),
]


def cards_html() -> str:
    rows = [c for c in HOME_CARDS if c[0] != "/writing/" or ARTICLES]
    return "\n".join("      " + card(*c) for c in rows)


add("index.html",
    "Pravin Khandke | Fellowship evidence record",
    "Public record of the work, recognition and professional service cited in "
    "Pravin Khandke's fellowship application.",
    """
<section class="hero">
  <div class="wrap hero-flex">
    <div class="hero-main">
      <p class="kicker">Fellowship evidence record</p>
      <h1>Pravin Khandke</h1>
      <p class="lede">Applied researcher and systems architect. 26 years building AI
      and distributed systems for retail, automotive and financial services.</p>
      <div class="badge-row">
        <span class="badge-chip">IEEE Senior Member</span>
        <span class="badge-chip">RSS Fellow</span>
        <span class="badge-chip">SEFM Eminent Fellow</span>
        <span class="badge-chip">SCRS Fellow</span>
      </div>
      <div class="cta-row">
        <a class="btn" href="#record">Read the record</a>
        <a class="btn ghost" href="/peer-review/">Peer review</a>
      </div>
      <div class="connect-row">
        <a href="https://orcid.org/0009-0004-9693-9334">ORCID 0009-0004-9693-9334</a>
        <a href="https://www.linkedin.com/in/pravin-khandke">linkedin.com/in/pravin-khandke</a>
        <a href="mailto:pravin.khandke@ieee.org">pravin.khandke@ieee.org</a>
      </div>
    </div>
    <div class="hero-photo">
      <img src="/assets/img/profile.jpg" alt="Pravin Khandke, headshot" width="370" height="480">
    </div>
  </div>
</section>

<div class="stats">
  <div class="wrap">
    <span class="stat"><span class="stat-n" data-counter="years">26</span><span class="stat-l">Years</span></span>
    <span class="stat"><span class="stat-n" data-counter="venues">28</span><span class="stat-l">Review venues</span></span>
    <span class="stat"><span class="stat-n" data-counter="committees">3</span><span class="stat-l">Committees</span></span>
    <span class="stat"><span class="stat-n" data-counter="publications">3</span><span class="stat-l">Publications</span></span>
  </div>
</div>

<div class="wrap">

  <section id="highlights">
    <h2 class="section-rule">Highlights</h2>
    <p class="section-intro">Dated items from the record, newest first. Each one links to its source.</p>
""" + highlights_html() + """
  </section>

  <section id="record">
    <h2 class="section-rule">The record, by topic</h2>
    <p class="section-intro">Each page holds the full evidence for one area, with a source line on every claim.</p>
    <div class="grid">
""" + cards_html() + """
    </div>
  </section>

  <section id="about">
    <h2 class="section-rule">About</h2>
    <p>
      I have spent 26 years building AI and distributed systems for businesses that
      cannot afford them to fail. The work began in retail platforms and now serves
      the automotive and financial sectors. I publish on human-in-the-loop AI and
      review submissions for international conferences.
    </p>
  </section>

  <section id="background">
    <h2 class="section-rule">Background</h2>
    <table class="edu-table">
      <thead><tr><th>Degree</th><th>Institution</th><th>Year</th></tr></thead>
      <tbody>
        <tr><td>Master of Business Administration (Systems)</td><td>Vinayaka Missions Research Foundation</td><td>2010</td></tr>
        <tr><td>Bachelor of Arts, Social Sciences</td><td>Madurai Kamaraj University</td><td>2003</td></tr>
        <tr><td>Post Graduate Diploma, Computer Engineering</td><td>PC Point, Pune</td><td>1998</td></tr>
        <tr><td>Technical Certification</td><td>Center for Electronics Design and Technology of India (CEDT)</td><td>1997</td></tr>
      </tbody>
    </table>
    <h3>Work history</h3>
    <table class="edu-table">
      <thead><tr><th>Role</th><th>Employer</th><th>Period</th></tr></thead>
      <tbody>
        <tr><td>Staff Software Engineer</td><td>Insight Global</td><td>October 2022 to present</td></tr>
        <tr><td>Senior Full Stack Developer</td><td>Amadeus</td><td>April 2021 to October 2022</td></tr>
        <tr><td>Senior Consultant</td><td>Capgemini</td><td>March 2008 to April 2021</td></tr>
        <tr><td>Consultant</td><td>Capgemini</td><td>May 2004 to March 2008</td></tr>
        <tr><td>Developer</td><td>CashTech Solutions</td><td>November 2003 to May 2004</td></tr>
        <tr><td>Programmer</td><td>Sunrise Systems</td><td>July 2000 to November 2003</td></tr>
        <tr><td>Junior Software Developer</td><td>Infolution Systems and Services</td><td>December 1999 to July 2000</td></tr>
      </tbody>
    </table>
    <p class="src-note">
      Dates follow the submitted application form where it states them. Where the form
      and the resume disagree, the form wins and the difference is recorded in the
      evidence register.
    </p>
    <p><a href="/career/">The full career record</a></p>
  </section>

  <div class="note">
    <strong>On what is not here.</strong> Where evidence is confidential to an employer,
    discloses commercial figures, or contains another person's personal data, it is
    supplied to the assessing body directly rather than published. Nothing here is a
    scanned certificate, because the awarding body's own register is the better source.
  </div>
</div>
""")

# ============================================================================
# MEMBERSHIPS
# ============================================================================
add("memberships/index.html",
    "Memberships and fellowships | Pravin Khandke",
    "Professional memberships and fellowship grades held by Pravin Khandke, with the "
    "conferring body and verification route for each.",
    """
<section class="hero">
  <div class="wrap">
    <p class="kicker">Memberships and fellowships</p>
    <h1>Grades held, and who conferred them</h1>
    <p class="lede">
      Membership evidence is only worth what the conferring body's own record says. Each
      entry below names the body, the grade, the date and, where the body publishes one,
      the verification route.
    </p>
  </div>
</section>

<div class="wrap">
  <section>
    <h2>IEEE Senior Member</h2>
    <ul class="claims">
""" + claim(
      "Elevated to Senior Member of the Institute of Electrical and Electronics Engineers "
      "in June 2026, member number 102303821. IEEE describes Senior Member as a grade "
      "awarded to those who have demonstrated significant performance over a sustained "
      "period, assessed by a panel of peers, and notes that it is held by a minority of "
      "the total membership.",
      [ext("https://www.ieee.org/membership/senior-members.html", "IEEE, Senior Member grade")]) + """
    </ul>

    <h2>The Scholars Academic and Scientific Society</h2>
    <ul class="claims">
""" + claim(
      "Eminent Fellow Member (SEFM), conferred in June 2026 as a lifetime honour. The "
      "Society states that its fellowships follow a nomination and recommendation process "
      "reviewed by its Eminent Fellows.",
      [ext(SAS_VERIFY, "Society membership verification page")]) + """
    </ul>

    <h2>Royal Statistical Society</h2>
    <ul class="claims">
""" + claim(
      "Fellow of the Royal Statistical Society, membership number 263939, since July 2026. "
      "The Society is the United Kingdom professional body for statistics, founded in 1834 "
      "and incorporated by Royal Charter. It styles its members Fellows, and welcomed me to "
      "Fellow membership in July 2026.",
      [ext("https://rss.org.uk/", "Royal Statistical Society")]) + """
    </ul>

    <h2>Soft Computing Research Society</h2>
    <ul class="claims">
""" + claim(
      "Fellow of the Soft Computing Research Society, Fellow Certificate number "
      "SCRS/Fellow/2360. The Society is an international professional society for "
      "researchers and practitioners in soft computing and its applications.",
      [ext("https://scrs.in/", "Soft Computing Research Society")]) + """
    </ul>

    <p class="src-note">
      Recognition is verified against the conferring body's own register rather than a
      scanned certificate.
    </p>

    <div class="note">
      <strong>On the grades.</strong> IEEE Senior Member and Eminent Fellow Member of the
      Society were conferred through assessment. Royal Statistical Society Fellowship is
      the Society's standard grade, open to those with a sustained interest in statistics.
    </div>
  </section>
</div>
""")


# ============================================================================
# BCS — INVENTION AND INNOVATION
# ============================================================================
CASE_RECON = case_study(
    "Remittance reconciliation pipeline",
    "Human-in-the-loop AI for financial controls",
    ["Reads remittance detail from four channels that share no common format.",
     "Matches payments to invoices, with a person at the decision point for every match the model is not sure of.",
     "Writes every validation and override to an audit trail."],
    ["human-in-the-loop", "financial controls"],
    [ext(IJCA, "IJCA, where the pattern is published")],
    art=figure("diagram-reconciliation.svg"))

CASE_BACKBONE = case_study(
    "Event-driven retail backbone",
    "Messaging between independently governed nodes",
    ["Moves multi-site retail data collection over an ActiveMQ Artemis backbone.",
     "Designed for high-throughput propagation between independently governed nodes.",
     "Presented at IEEE ICCBI in Dubai."],
    ["event-driven", "messaging"],
    [ext("https://iccbi.com/", "IEEE ICCBI")])

add("invention/index.html",
    "Invention and innovation | Pravin Khandke",
    "A human-in-the-loop pipeline that reconciles customer remittances arriving through "
    "four separate channels, and the peer-reviewed publication of the pattern behind it.",
    """
<section class="hero">
  <div class="wrap">
    <p class="kicker">Body of work</p>
    <h1>A human-in-the-loop pipeline for remittance reconciliation</h1>
    <p class="lede">
      Customer payments arrive through four channels, and no two channels speak the same
      language. I designed and delivered the pipeline that reads all four and matches them
      to invoices, and I published the pattern behind it so the approach reaches engineers
      beyond my employer.
    </p>
  </div>
</section>

<div class="wrap">
  <section>
    <h2>In brief</h2>
""" + CASE_RECON + CASE_BACKBONE + """
    <h2>The situation</h2>
    <p>
      Customer remittances reach a finance function through channels that each carry a
      different shape of data. Physical cheques arrive as lockbox scans that need reading.
      Electronic payments arrive as ACH files. Remittance advice arrives by email, in
      whatever format each customer chooses. A fourth stream sits inside vendor portals,
      and no two portals behave alike.
    </p>
    <p>
      Matching those payments to open invoices was a manual process. Payments without clear
      advice sat unresolved, and reporting fell behind. The consequence of an incorrect
      match is specific and serious. Cash is applied to the wrong customer, and the error
      surfaces later as a dispute.
    </p>

    <h2>What I set out to do</h2>
    <p>
      Build a system that reads remittance detail from all four channels and reconciles it
      automatically, without giving up accuracy to do it. Every payment had to land on the
      right customer and the right invoice, or stop and wait for a person to decide.
    </p>

    <h2>What I designed and built</h2>
    <ul class="claims">
""" + claim(
      "The pipeline rests on one rule. The model reads, and it never closes the books "
      "alone. That rule follows from the properties of the technology. Language models are "
      "not deterministic, and financial reconciliation demands accuracy, so the design "
      "places a person at the decision point rather than at the end of a queue.",
      [ext(IJCA, "IJCA, where the pattern is published")]) + "\n" + claim(
      "Every extracted field carries a confidence score, and handling is tiered by that "
      "score. High confidence assigns the match automatically. The middle band surfaces the "
      "closest candidates and a person chooses. Low confidence goes to manual review.",
      [ext(IJCA, "Published description of the confidence model")]) + "\n" + claim(
      "Customer identification runs as a cascade rather than a single rule. It falls "
      "through from name matching to bank account details to invoice numbers, so a payment "
      "can still be placed when the first signal is missing.",
      [ext(IJCA, "Published description of the matching cascade")]) + "\n" + claim(
      "A validation layer checks each proposed match against that customer's own history "
      "before it posts, and flags an unusual result with the reason attached. Every "
      "validation and every override is written to an audit trail that cannot be altered, "
      "which is what the financial reporting controls require.",
      [ext(IJCA, "Published description of the validation and audit layer")]) + """
    </ul>

    <h2>Why it reaches beyond one employer</h2>
    <p>
      The design rationale behind the system is published as peer-reviewed work, so the
      approach is available to any team building automation over financial data. The paper
      sets out what happens when generative models are put in front of remittance data, and
      why a confidence-based human review step is the part that makes the automation safe
      to deploy.
    </p>
    <ul class="claims">
""" + claim(
      "Designing Adaptive Human-in-the-Loop Interfaces for Enhanced Collaborative Incident "
      "Management, International Journal of Computer Applications, 2026. The human-in-the-"
      "loop pattern applied to operational workflows, including the confidence-tiered "
      "review model used in the reconciliation pipeline.",
      [ext(IJCA, "IJCA, 2026")]) + "\n" + claim(
      "Scalable Event-Driven Architectures for Distributed Retail Data Collection Using "
      "ActiveMQ Artemis, IEEE ICCBI. The messaging architecture that moves collected "
      "and reconciled data between systems.",
      [ext("https://iccbi.com/", "IEEE ICCBI")]) + """
    </ul>

    <div class="note">
      <strong>On the measured result.</strong> The system is in production. Its effect on
      matching accuracy, and the volume it handles, are stated in my fellowship
      application, because those are my employer's operational figures and they are not
      mine to publish. What is public is the pattern, and the publication that carries it.
    </div>
  </section>
</div>
""")

# ============================================================================
# BCS — CONSULTANCY
# ============================================================================
CASE_RETIRE = case_study(
    "Retiring a continental-scale platform",
    "Strangler fig migration with no downtime window",
    ["Advised retiring a legacy mainframe service by service.",
     "Old and new systems ran in parallel throughout.",
     "The programme completed with no interruption to live dealer operations."],
    ["strangler fig", "no downtime window"],
    [ext("https://martinfowler.com/bliki/StranglerFigApplication.html",
         "The strangler fig pattern, described by Martin Fowler"),
     "Client confirmation available through the named supporter"],
    dates="March 2020 to April 2021",
    art=figure("diagram-strangler.svg"))

CASE_MODEL = case_study(
    "A canonical data model that became the standard",
    "One integration hub for every downstream consumer",
    ["Recommended a canonical data model as the single integration hub.",
     "The client adopted it, and it remains the standard the organisation builds on."],
    ["canonical model", "integration hub"],
    ["Client confirmation available through the named supporter"])

add("consultancy/index.html",
    "Consultancy | Pravin Khandke",
    "Advisory work on retiring a continental-scale automotive data platform, where a "
    "recommended data model became the client organisation's standing integration standard.",
    """
<section class="hero">
  <div class="wrap">
    <p class="kicker">Body of work</p>
    <h1>Advising on the retirement of a continental-scale automotive data platform</h1>
    <p class="lede">
      A client ran its national dealer network on a legacy mainframe. A single replacement
      was impossible, because dealers depended on the platform every working day. My role
      was advisory, and the recommendations shaped how the organisation has worked since.
    </p>
  </div>
</section>

<div class="wrap">
  <section>
    <h2>In brief</h2>
""" + CASE_RETIRE + CASE_MODEL + """
    <h2>The situation</h2>
    <p>
      Cox Automotive, a global automotive technology and digital commerce business
      operating under Cox Enterprises, ran customer transmission data on a legacy AS/400
      mainframe. It processed millions of transaction records daily for a nationwide dealer
      network. The system was tightly coupled and expensive to maintain. It could not scale, and\n      any change carried risk across the whole estate.
    </p>
    <p>
      A replacement in one step was not available to the client. Dealers depended on the
      platform for daily operations, so an outage during a cutover would have stopped
      business across the network. I served the account from Capgemini's Pune delivery
      centre and moved to the client's side in Atlanta to lead the migration there.
    </p>

    <h2>What I was accountable for</h2>
    <p>
      Retiring the platform without interrupting live dealer operations. Designing the
      distributed replacement and sequencing a multi-year migration. Holding engineering
      quality across a distributed team of ten split between the United States and India. Keeping
      client stakeholders confident through every phase.
    </p>

    <h2>What I advised, and what the client adopted</h2>
    <ul class="claims">
""" + claim(
      "I advised the client to retire the platform service by service using a strangler fig "
      "pattern, replacing functions one at a time while old and new systems ran in "
      "parallel. The recommendation removed cutover risk, because there was never a moment "
      "when the whole estate changed at once.",
      [ext("https://martinfowler.com/bliki/StranglerFigApplication.html", "The strangler fig pattern, described by Martin Fowler")]) + "\n" + claim(
      "I recommended a canonical data model as the single integration hub for every "
      "downstream consumer. The client adopted it, and it became the standard the "
      "organisation still builds on. That is the part of this engagement with the longest "
      "life, because a data standard outlives the migration that produced it.",
      ["Client confirmation available through the named supporter"]) + "\n" + claim(
      "I recommended an automated change data capture approach to convert legacy batch "
      "feeds into real-time event streams, and worked through the operational trade-offs "
      "between batch and stream processing with the client's teams during the transition.",
      ["Client confirmation available through the named supporter"]) + "\n" + claim(
      "I counselled the adoption of consumer-driven contract testing, so that each "
      "independently migrating service could be verified on its own rather than through the "
      "whole estate. That held integration correctness across a phasing which ran for "
      "years.",
      ["Client confirmation available through the named supporter"]) + "\n" + claim(
      "I advised on the delivery through a distributed team of ten split between the United States "
      "and India, and the platform was handed to the client's own engineers at the end of "
      "the engagement. Handing over was the objective. The client runs it without us.",
      ["Client confirmation available through the named supporter"]) + "\n" + claim(
      "I recommended the Transaction Web Service as the backbone for the Manheim OVE and "
      "Manheim Express marketplaces, and directed the team that built it under "
      "zero-downtime requirements.",
      ["Client confirmation available through the named supporter"]) + "\n" + claim(
      "Cox Automotive operates in more than 30 countries.",
      ["Client confirmation available through the named supporter"]) + """
    </ul>

    <h2>Before Cox Automotive</h2>
    <ul class="claims">
""" + claim(
      "At Sunrise Systems, my first lead role, I led a team of five to move the fixed "
      "deposit system of Kirloskar Oil Engines Ltd from COBOL to a Java and Oracle web "
      "application. Performance tripled and the system became reachable from anywhere on the "
      "internet. The manual workload of five staff fell.",
      ["Client reference available through the application"]) + "\n" + claim(
      "For Zett Media, a Norwegian software group, I engineered a financial management "
      "platform that handled customers' credit information. It loaded in 2.5 seconds over "
      "56kbps connections and met strict security requirements.",
      [ext("https://www.domain-b.com/companies-organisations/firms-companies/zett-media-sets-up-indian-subsidiary", "Published article naming Sunrise Systems of Pune as the software provider")]) + """
    </ul>

    <h2>What changed</h2>
    <p>
      The programme completed with no disruption to live dealer operations, start to
      finish. The distributed platform took over the transaction load the mainframe had
      carried, and the data model and messaging patterns established during the work remain
      the foundation the organisation builds on. Colleagues who stayed on the account have
      confirmed that it still runs on the architecture set at the time.
    </p>
    <p class="claim-src">Source: Client confirmation available through the named supporter</p>

    <div class="note">
      <strong>On the client test.</strong> The consultancy criterion asks for
      collaboration with various clients. My record evidences this one client in depth
      rather than several in less depth. Whether that is enough is the assessor's call, and
      I have not stretched the record to make it look broader than it is.
    </div>

    <h2>Dates</h2>
    <p>
      I worked on the Cox Automotive account from 2004 to 2021, serving it from Capgemini's
      Pune delivery centre before relocating to Atlanta in 2013. I was senior consultant on
      the account from 2008, and from March 2020 to April 2021 I led the retirement of the
      mainframe without interrupting live dealer operations.
    </p>
  </section>
</div>
""")

# ============================================================================
# BCS — MENTORING AND COACHING
# ============================================================================
CASE_TEAMS = case_study(
    "Engineers developed inside the teams",
    "Pairing on production work",
    ["Junior engineers were paired on high-skill production work until they could own it without me.",
     "Development was a measured part of each project.",
     "The engineers now hold senior and lead positions."],
    ["pairing", "measured development"],
    ["Named mentees available for confirmation through the application"])

CASE_CAPSTONE = case_study(
    "A sponsored university capstone",
    "A full-semester project in a Department of Information Technology",
    ["Sponsored the capstone and authored its specification.",
     "Guided a team of eight students, four of them pursuing AI master's degrees, through KnowledgeBridge, a working retrieval-augmented generation platform.",
     "The specification called for hybrid search with source citations and token budgeting.",
     "It also required a feasibility study naming where human oversight remains essential."],
    ["capstone", "cost-aware AI"],
    ["Project documentation available through the application"],
    art=figure("mentoring-capstone.jpg"))

CASE_STANDARD = case_study(
    "Using AI at Home and School",
    "An open, age-banded guide to children's use of AI",
    ["Authored the guide so a parent or a school can adopt it.",
     "Extends the same commitment to the next generation of users."],
    ["open guide", "age-banded"],
    [ext(KIDS_REPO, "The repository, publicly available")])

add("mentoring/index.html",
    "Mentoring and coaching | Pravin Khandke",
    "Structured development of engineers inside my teams, a sponsored university capstone, "
    "and an open guide to children's use of AI.",
    """
<section class="hero">
  <div class="wrap">
    <p class="kicker">Professional impact</p>
    <h1>Developing engineers, inside my teams and before they enter the industry</h1>
    <p class="lede">
      Graduates leave university knowing how software is supposed to work. They do not\n      know how it behaves under production load or a tight budget. I have spent my career
      working on that gap, with the engineers on my teams and with students who have not
      joined a team yet.
    </p>
  </div>
</section>

<div class="wrap">
  <section>
    <h2>In brief</h2>
""" + CASE_TEAMS + CASE_CAPSTONE + CASE_STANDARD + """
    <h2>The situation</h2>
    <p>
      The IT profession has a persistent gap. University teaches the theory of software and
      AI. It does not teach how to ship a system that is secure and cost-aware, or how to\n      be honest about what that system cannot do. That gap widened as AI became central to enterprise work,
      because the failure modes are harder to see and easier to hide.
    </p>

    <h2>What I set out to do</h2>
    <p>
      Develop people through structured mentorship rather than occasional advice, and take
      that commitment beyond my own employers so it reaches people before they enter the
      industry.
    </p>

    <h2>What I did</h2>
    <ul class="claims">
""" + claim(
      "Inside my teams I mentored the junior engineers directly, pairing with them on "
      "high-skill production work until they could own it without me. I made their "
      "development a measured part of each project rather than something fitted around "
      "delivery.",
      ["Named mentees available for confirmation through the application"]) + "\n" + claim(
      "I sponsored a full-semester capstone in a university Department of Information "
      "Technology, guiding a student team of eight, four of them pursuing AI master's degrees, "
      "through the design and delivery of KnowledgeBridge, a working retrieval-augmented "
      "generation platform. I sponsored the work rather than merely advising on "
      "it, which meant the students had a route to it being built.",
      ["Project documentation available through the application"]) + "\n" + claim(
      "I authored the capstone specification so the students met the hard parts of real "
      "engineering rather than a sanitised exercise. It called for a working retrieval and "
      "generation system. Hybrid search had to carry source citations. Cost-aware architecture "
      "with token budgeting ran alongside data privacy controls. It also required a "
      "feasibility study documenting where AI succeeds and where human oversight remains "
      "essential. The last requirement matters "
      "most, because it teaches a limit rather than a feature.",
      ["Specification available through the application"]) + "\n" + claim(
      "I judge student work, most recently on the spring 2026 Computing Showcase panel at "
      "Kennesaw State University, assessing undergraduate projects and giving the teams "
      "direct feedback on them.",
      [ext("https://www.kennesaw.edu/", "Kennesaw State University"),
       ext("https://www.linkedin.com/in/pravin-khandke", "Announcement and certificate of appreciation, LinkedIn")]) + "\n" + claim(
      "I authored an open, age-banded guide called Using AI at Home and School, published as a "
      "public repository, so that a parent or a school can adopt it. It extends the "
      "same commitment beyond engineers to the next generation of users, who meet these "
      "systems with no training at all.",
      [ext(KIDS_REPO, "The repository, publicly available")]) + """
    </ul>

    <h2>What changed</h2>
    <p>
      Engineers I mentored on my teams now hold senior and lead positions, and the practices
      I taught them outlasted my time on those projects. Students who complete the capstone
      leave able to state what their system does and what it costs to run. They can also
      say where it should not be trusted. That last point is the outcome I care about, because it is the
      difference between a graduate who can build a demonstration and one who can be
      trusted with a production system.
    </p>

    <div class="note">
      <strong>What I have not claimed here.</strong> The rubric's top tier asks for
      documented career outcomes such as a mentee reaching an executive role. The engineers
      I developed hold senior and lead positions, and I have described them as such rather
      than reaching for a stronger claim. Named individuals and their current roles appear
      in the application, where the people concerned can verify them.
    </div>
  </section>
</div>
""")

# ============================================================================
# INSPIRING OTHERS
# ============================================================================
add("inspiring/index.html",
    "Inspiring others | Pravin Khandke",
    "How Pravin Khandke shares practical guidance on building AI systems, through coaching "
    "and mentoring and through public writing and speaking.",
    """
<section class="hero">
  <div class="wrap">
    <p class="kicker">Inspiring others</p>
    <h1>Sharing what works when AI systems reach production</h1>
    <p class="lede">
      Most advice on putting large language models into production comes from vendors. I have built systems where a wrong answer moves money, and I share what I learned in three ways. I coach teams inside the organisations I serve. I write and speak in public. I develop individual engineers one to one.
    </p>
  </div>
</section>

<div class="wrap">
  <section>
    <h2>The situation</h2>
    <p>
      Few people who have shipped these systems in regulated work say in public what goes wrong. Over 26 years I have built systems where a wrong answer moves money or stalls a dealer network. I have seen teams change how they build only when someone they trust shows them that the safer way works.
    </p>

    <h2>What I did</h2>
    <ul class="claims">
""" + claim(
      "At Cox Automotive I walked senior architects and technical leads through the reasoning behind major migration decisions until they owned the decisions themselves. I coached their teams through cloud adoption from 2010 to 2020.",
      ["Client confirmation available through the named supporter"]) + "\n" + claim(
      "Since 2025 I have built a custom agentic harness at Insight Global that keeps a person in charge and stops short of anything irreversible. I coach the engineers who now run it day to day.",
      ["Employer confirmation available through the application"]) + "\n" + claim(
      "I write for other engineers on feature flags and on messaging in the age of AI. Other articles cover code quality with Sonar and explainable AI.",
      [ext("/writing/", "Writing page, with a link to each article") if ARTICLES
       else ext("https://pravin-khandke.hashnode.dev/", "Hashnode profile")]) + "\n" + claim(
      "I gave the keynote at the IEEE 5th World Conference on Applied Intelligence and Computing in Jabalpur, and I presented event-driven architecture at IEEE ICCBI in Dubai.",
      [ext(AIC_LIST, "Keynote talk page on the conference site"),
       ext("https://iccbi.com/", "IEEE ICCBI")]) + "\n" + claim(
      "The human-in-the-loop pattern behind my reconciliation work is published in a peer-reviewed journal, so engineers beyond my own employer can use it.",
      [ext(IJCA, "International Journal of Computer Applications")]) + "\n" + claim(
      "I paired junior engineers on the difficult production work and stood behind them while they learned to lead.",
      ["Named mentees available for confirmation through the application"]) + "\n" + claim(
      "I am guiding an eight-student capstone team at Kennesaw State University, four of them pursuing AI master's degrees, through KnowledgeBridge, a working retrieval-augmented generation platform.",
      [ext("https://www.linkedin.com/in/pravin-khandke/details/honors/", "LinkedIn honors and awards"),
       "Project documentation available through the application"]) + """
    </ul>

    <h2>What changed</h2>
    <p>
      The practices outlasted my time on each project. Cox Automotive adopted the canonical data model as its integration standard and still builds on it. At Insight Global, low-confidence matches now stop for a person before they reach the ledger, and the teams I coached apply the same rule to agentic work. The two engineers I mentored longest now lead others. One is a Senior Solutions Architect and the other a Lead Software Engineer at Cox Automotive.
    </p>
    <p class="src-note">Source: client confirmation available through the named supporter, and employer confirmation available through the application.</p>
    <div class="note">
      <strong>On names.</strong> The people I mentored are named in my application, where they can confirm the account themselves.
    </div>
  </section>
</div>
""")

# ============================================================================
# CAREER
# ============================================================================
def skill_row(items):
    return '<div class="tag-row">' + "".join(f"<span>{html.escape(i)}</span>" for i in items) + "</div>"

add("career/index.html",
    "Career | Pravin Khandke",
    "Roles held by Pravin Khandke since 1999, with the work done in each and the skills used.",
    """
<section class="hero">
  <div class="wrap">
    <p class="kicker">Career</p>
    <h1>Twenty-six years of building systems that move money and data</h1>
    <p class="lede">
      This page lists each role in turn, newest first. The invention and consultancy pages hold the full account of the two pieces of work that matter most.
    </p>
  </div>
</section>

<div class="wrap">
  <section>
    <h2>Roles</h2>
""" + case_study(
      "Staff Software Engineer, Insight Global",
      "Financial data integration and transaction integrity",
      ["Designed the customer remittance reconciliation pipeline described on the invention page, which the finance function runs in production.",
       "Architected a canonical data model that unified several platforms with no shared API contract or data definition, and enabled event-driven synchronisation without changing any source system.",
       "Modelled the engagement lifecycle as a state machine in PostgreSQL, with an audit trail on every transition from onboarding to termination.",
       "Built a layered authorisation model that enforces permissions at the API gateway and again within each service.",
       "Established consumer-driven contract testing across independently deployable services.",
       "Since 2025, built a custom agentic harness that stops before any irreversible action, and coached the teams who use it."],
      ["financial services", "audit controls", "event-driven"],
      ["Employer confirmation available through the application"],
      dates="October 2022 to present") + case_study(
      "Senior Full Stack Developer, Amadeus",
      "Web data collection and retrieval",
      ["Led the engineering of a web data collection platform that supplied competitive rate intelligence to the company's pricing products.",
       "Scaled the platform to monitor more than 5,000 hotel booking sites continuously.",
       "Designed the resource isolation model that let many browser processes run on one host with predictable CPU and memory use.",
       "Optimised the retrieval layer so partial-match and prefix queries met a tight latency budget for live commercial traffic.",
       "Consolidated several data products into one customer-facing portal, and applied fault-tolerance patterns so an upstream failure did not take the portal down."],
      ["data collection", "travel technology"],
      ["Employer confirmation available through the application"],
      dates="April 2021 to October 2022") + case_study(
      "Senior Consultant and Consultant, Capgemini",
      "Cox Automotive dealer platforms, Pune and Atlanta",
      ["Built enterprise dealer management platforms for Cox Automotive on J2EE, first from the Pune delivery centre and then from Atlanta.",
       "Became senior consultant in March 2008, and led the retirement of the legacy mainframe from March 2020 to April 2021.",
       "Led a distributed delivery team across the United States and India, and mentored engineers as technical manager of the offshore team.",
       "The full account is on the consultancy page."],
      ["Java and J2EE", "legacy modernisation"],
      ["Client confirmation available through the named supporter"],
      dates="May 2004 to April 2021") + case_study(
      "Earlier roles",
      "Banking and enterprise software in Pune",
      ["Developer at CashTech Solutions, building core banking modules for payment processing and account management for regional banking clients, November 2003 to May 2004.",
       "Programmer at Sunrise Systems, delivering financial and fixed deposit systems in Java and J2EE, July 2000 to November 2003.",
       "Junior Software Developer at Infolution Systems and Services, developing software components for client projects, December 1999 to July 2000."],
      ["Java", "banking software"],
      ["Employment record available through the application"],
      dates="December 1999 to May 2004") + """
    <h2>Technical expertise</h2>
    <h3>Systems architecture</h3>
""" + skill_row(["distributed systems", "microservices", "event-driven design", "API integration", "legacy modernisation"]) + """
    <h3>Data</h3>
""" + skill_row(["PostgreSQL", "Couchbase", "MongoDB", "Elasticsearch", "Oracle", "DB2", "MySQL", "canonical data modelling"]) + """
    <h3>Infrastructure</h3>
""" + skill_row(["Kubernetes", "Docker", "AWS", "CI/CD", "Linux", "cgroups"]) + """
    <h3>Languages</h3>
""" + skill_row(["Java", "JavaScript", "SQL"]) + """
    <h3>Observability</h3>
""" + skill_row(["Splunk", "New Relic", "DataDog", "PagerDuty"]) + """

    <h2>Community service</h2>
    <ul class="claims">
""" + claim(
      "Volunteer at the Celebration 250 Community Recognition Event run by the Cobb County Sheriff's Office, August 2026.",
      ["Volunteer record available through the application"]) + """
    </ul>
  </section>
</div>
""")

# ============================================================================
# BCS — PUBLIC INFLUENCER
# ============================================================================
add("standing/index.html",
    "Public influencer | Pravin Khandke",
    "Keynotes at recognised events, technical programme committees at international "
    "conferences, a peer review record, and sustained written work on digital and IT topics.",
    """
<section class="hero">
  <div class="wrap">
    <p class="kicker">Standing in the community</p>
    <h1>Invited to speak, asked to judge, and read beyond my own organisation</h1>
    <p class="lede">
      Standing in a profession shows up as other people asking you to do something. The
      invitations on this page came from conference organisers and journal editors. Each
      one is listed with a public record where one exists.
    </p>
  </div>
</section>

<div class="wrap">
  <section>
    <h2>Keynote and conference speaking</h2>
    <ul class="claims">
""" + claim(
      "Keynote speaker at the IEEE 5th World Conference on Applied Intelligence and "
      "Computing, held in Jabalpur, India on 29 and 30 August. My talk was The Trust "
      "Gap: Architecting Autonomous AI Systems for Real-World Accountability, It covered how agent "
      "systems fail in production and how to verify them. It also argued that trust should "
      "include the sustainability cost of running them. The audience numbered 57.",
      [ext(AIC_LIST, "Keynote talk page on the conference site"),
       "Audience figure available through the application"]) + "\n" + claim(
      "Confirmed speaker at Extract Summit, held at Brazos Hall in Austin, Texas on 7 "
      "and 8 October. My session is The Naive AI Trap: Why Finance-Grade Extraction "
      "Needs Hybrid Agents, on the second day.",
      [ext("https://www.extractsummit.io/", "Extract Summit programme")]) + """
    </ul>

    <h2>Technical programme committees</h2>
    <p>
      I serve on the technical programme committees of three international venues, where the
      work is deciding which submitted research is accepted and presented. One of the three
      is an IEEE workshop rather than a full conference, and I describe it as such.
    </p>
    <ul class="venues">
      <li><img class="flag" src="/assets/flags/us.png" alt="United States" width="18" height="12"> AIIoT <span class="where">IEEE World AI IoT Congress, Seattle, United States</span></li>
      <li><img class="flag" src="/assets/flags/tn.png" alt="Tunisia" width="18" height="12"> SIME <span class="where">Sousse, Tunisia</span></li>
      <li><img class="flag" src="/assets/flags/pt.png" alt="Portugal" width="18" height="12"> NGSME <span class="where">IEEE workshop, Vilamoura, Portugal</span></li>
    </ul>

    <h2>Peer review</h2>
    <p>
      I review submitted papers for international conferences, across artificial\n      intelligence and distributed systems as well as the internet of things and cloud\n      computing. The venues are named on the
      <a href="/peer-review/">peer review record</a> rather
      than summarised as a number here, because a named venue can be checked and a total
      cannot.
    </p>

    <h2>Written work</h2>
    <ul class="claims">
""" + claim(
      "Three peer-reviewed publications. One is in the International Journal of Computer "
      "Applications and one was accepted and presented at IEEE ICCBI. The third is a "
      "co-authored paper for the IEEE International Workshop on Intelligent Systems on "
      "event-driven dynamic pricing. They cover human-in-the-loop interfaces and "
      "event-driven architectures.",
      [ext("/publications/", "Publications, with a link to each paper")]) + "\n" + claim(
      "Sustained technical writing for engineers, published on developer platforms and read "
      "outside my own organisation, The subjects are architecture and "
      "reliability, and the practical failure modes of AI systems in production. I have "
      "also published on HackerNoon, where one article has 888 reads.",
      [ext("https://dev.to/pravin-khandke", "Dev.to"),
       ext("https://pravin-khandke.hashnode.dev/", "Hashnode"),
       "HackerNoon reader count available through the application"]) + "\n" + claim(
      "Author of Using AI at Home and School, an open, age-banded guide to children's use "
      "of AI, published as a public repository.",
      [ext(KIDS_REPO, "The repository, publicly available")]) + "\n" + claim(
      "Interviewed by Authority Magazine for its C-Suite Perspectives series, on where to "
      "use AI and where to rely only on humans. This is third-party editorial coverage "
      "rather than writing of my own, which is why I list it separately.",
      [ext(
        "https://medium.com/authority-magazine/c-suite-perspectives-on-ai-pravin-khandke-on-where-to-use-ai-and-where-to-rely-only-on-humans-854b733e03a1",
        "Authority Magazine interview")]) + """
    </ul>

    <h2>Universities</h2>
    <ul class="claims">
""" + claim(
      "Judge at the Georgia Institute of Technology Capstone Design Expo.",
      [ext("https://www.linkedin.com/in/pravin-khandke/details/honors/", "LinkedIn honors and awards")]) + "\n" + claim(
      "Judge at Kennesaw State University, most recently on the spring 2026 Computing "
      "Showcase panel.",
      [ext("https://www.kennesaw.edu/", "Kennesaw State University"),
       ext("https://www.linkedin.com/in/pravin-khandke/details/honors/", "LinkedIn honors and awards")]) + "\n" + claim(
      "Guest speaker at Kennesaw State University on Building AI Responsibly, to 32 "
      "students.",
      [ext("https://www.linkedin.com/in/pravin-khandke/details/honors/", "LinkedIn honors and awards")]) + """
    </ul>

    <div class="note">
      <strong>Why everything here is linked.</strong> An assessing body asks for evidence
      of influence that is publicly available. A claim that cannot be checked is worth
      less than a
      smaller claim that can, so where an organiser publishes its own record of an
      invitation, that record is the source rather than my account of it.
    </div>
  </section>
</div>
""")

# ============================================================================
# PUBLICATIONS
# ============================================================================
SCHOLAR = "https://scholar.google.com/citations?user=e8zPvu8AAAAJ&hl=en"

PAPERS = [
    {"title": "Designing Adaptive Human-in-the-Loop Interfaces for Enhanced Collaborative Incident Management",
     "venue": "International Journal of Computer Applications", "year": "2026",
     "summary": "Examines interface architectures in which human operators and AI systems "
                "jointly manage complex incident workflows, with cognitive task allocation "
                "shifting according to the operator's state and the system's own confidence. "
                "It is the published statement of the human-in-the-loop pattern I apply to "
                "production systems.",
     "url": IJCA, "link": "International Journal of Computer Applications"},
    {"title": "Scalable Event-Driven Architectures for Distributed Retail Data Collection Using ActiveMQ Artemis",
     "venue": "IEEE ICCBI, the 5th International Conference on Computer Networks, Big Data and IoT",
     "year": None,
     "summary": "Examines high-throughput messaging topologies for multi-site data aggregation, "
                "using ActiveMQ Artemis as the backbone for event propagation across "
                "independently governed retail nodes. Presented in Dubai in June.",
     "url": "https://iccbi.com/", "link": "IEEE ICCBI"},
    {"title": "An Event-Driven Context-Aware Framework for Margin-Preserving Dynamic Pricing in High-Velocity Retail Commerce Systems",
     "venue": "IEEE International Workshop on Intelligent Systems (IWIS), accepted paper", "year": "2026",
     "summary": "Co-authored with Jayakumar Ramalingam and Jose Prabhu Michael Singarayan. "
                "Proposes a context-aware pricing framework that adjusts retail prices in "
                "real time from streaming demand and inventory signals while preserving "
                "margin targets.",
     "url": SCHOLAR, "link": "Google Scholar profile"},
]


def pub_entry(p) -> str:
    year = f", {html.escape(p['year'])}" if p["year"] else ""
    return (f'<article class="pub-entry"><h3 class="pub-title">{html.escape(p["title"])}</h3>'
            f'<p class="pub-venue"><em>{html.escape(p["venue"])}</em>{year}</p>'
            f'<p>{html.escape(p["summary"])}</p>'
            f'<p class="claim-src">Source: {ext(p["url"], p["link"])}</p></article>')


SEE_ALSO = ('<a href="/talks/">talks</a>'
            + (' and the <a href="/writing/">technical articles</a>' if ARTICLES else ""))

add("publications/index.html",
    "Publications | Pravin Khandke",
    "Peer-reviewed papers by Pravin Khandke, with a link to each published record.",
    """
<section class="hero">
  <div class="wrap">
    <p class="kicker">Publications</p>
    <h1>Peer-reviewed papers, with the record linked</h1>
    <p class="lede">
      Three papers have been through peer review. Each entry links to the published version or to the record of acceptance
      rather than quoting it. Talks and technical articles have their own pages.
    </p>
  </div>
</section>

<div class="wrap">
  <section>
    <h2>Peer-reviewed papers</h2>
""" + "\n".join(pub_entry(p) for p in PAPERS) + """
    <p>Google Scholar lists all three papers. """ + ext(SCHOLAR, "Google Scholar profile") + """</p>

    <h2>Open source</h2>
    <p>Two of the papers have a companion repository. The children's guide is the third public repository.</p>
    <ul class="claims">
""" + claim(
      "Reference implementation that accompanies the paper on adaptive human-in-the-loop interfaces "
      "for incident management. It is a Spring Boot application with a dashboard and an incident simulator.",
      [ext("https://github.com/pravin-khandke/hitl-manager", "hitl-manager repository")]) + "\n" + claim(
      "Companion implementation of the IEEE ICCBI paper on event-driven retail data collection with "
      "ActiveMQ Artemis. It simulates retail events from 50 virtual store locations.",
      [ext("https://github.com/pravin-khandke/scalable-event-driven-retail", "scalable-event-driven-retail repository")]) + "\n" + claim(
      "Using AI at Home and School, an open, age-banded guide to children's use of AI.",
      [ext(KIDS_REPO, "safe-ai-for-kids repository")]) + """
    </ul>

    <p>See also the """ + SEE_ALSO + """.</p>

    <div class="note">
      <strong>On the publication record.</strong> I list three peer-reviewed papers, which is
      the accurate count. I do not list work in draft, work under review, or a citation
      total, because a reader who follows a dead link or an empty profile learns more from
      the absence than from the claim.
    </div>
  </section>
</div>
""")

# ============================================================================
# TALKS
# ============================================================================
TALKS = [
    {"group": "Keynote",
     "event": "IEEE 5th World Conference on Applied Intelligence and Computing",
     "place": "Jabalpur, India", "when": "29 and 30 August",
     "title": "The Trust Gap: Architecting Autonomous AI Systems for Real-World Accountability",
     "summary": "How autonomous agent systems fail once they leave a demonstration, and how "
                "to verify them before they are trusted. The talk also argues that the "
                "sustainability cost of running them belongs in the same conversation as "
                "their accuracy.",
     "url": AIC_LIST, "link": "Keynote talk page on the conference site",
     "photo": "talk-aic-keynote.jpg"},
    {"group": "Conference sessions",
     "event": "Extract Summit",
     "place": "Brazos Hall, Austin, Texas", "when": "7 and 8 October",
     "title": "The Naive AI Trap: Why Finance-Grade Extraction Needs Hybrid Agents",
     "summary": "Why extraction that has to be correct, as opposed to merely plausible, needs "
                "hybrid agent designs rather than a single model in a loop. The session is "
                "on the second day.",
     "url": "https://www.extractsummit.io/", "link": "Extract Summit programme",
     "photo": "talk-extract-summit.jpg"},
    {"group": "Conference sessions",
     "event": "IEEE ICCBI, the 5th International Conference on Computer Networks, Big Data and IoT",
     "place": "Dubai", "when": "June",
     "title": "Scalable Event-Driven Architectures for Distributed Retail Data Collection",
     "summary": "Presented alongside the published paper.",
     "url": "https://iccbi.com/", "link": "IEEE ICCBI programme",
     "photo": "talk-iccbi.jpg"},
]


def talk_card(t) -> str:
    return (f'<article class="talk">{thumb(t["photo"])}<div class="talk-body">'
            f'<p class="talk-when">{html.escape(t["when"])}, {html.escape(t["place"])}</p>'
            f'<h3>{html.escape(t["title"])}</h3>'
            f'<p class="talk-event">{html.escape(t["event"])}</p>'
            f'<p>{html.escape(t["summary"])}</p>'
            f'<a class="linkbtn src" href="{html.escape(t["url"])}" rel="noopener">'
            f'{html.escape(t["link"])}<span class="ext" aria-hidden="true">&nbsp;&#8599;</span></a>'
            f'</div></article>')


def talk_groups_html() -> str:
    out = []
    for group in ("Keynote", "Conference sessions"):
        items = [t for t in TALKS if t["group"] == group]
        if items:
            out.append(f"    <h2>{group}</h2>\n" + "\n".join(talk_card(t) for t in items))
    return "\n".join(out)


add("talks/index.html",
    "Talks and keynotes | Pravin Khandke",
    "Keynote and conference speaking, with the organiser's own published record where it "
    "exists.",
    """
<section class="hero">
  <div class="wrap">
    <p class="kicker">Talks and keynotes</p>
    <h1>Speaking, and where the organiser lists it</h1>
    <p class="lede">
      Each entry names the event, the city and the session title. Where the organiser
      publishes a speaker list or programme, that page is the source, because an
      organiser's record is stronger evidence than a speaker's own account.
    </p>
  </div>
</section>

<div class="wrap">
  <section>
""" + talk_groups_html() + """

    <h2>University talks</h2>
    <p>
      I speak to students about cybersecurity and applied AI. These sessions are arranged
      directly with the institution rather than through a published programme, so the record
      is the letter the university sent afterwards rather than a programme page.
    </p>
    <article class="talk">
      <div class="talk-body">
        <p class="talk-when">17 September 2026, Kennesaw State University</p>
        <h3>Adversarial Resilience: Building AI Systems That Survive Hostile Environments</h3>
        <p class="talk-event">Invited external industry speaker, Center for Cybersecurity Education</p>
        <p>
          A hybrid session for the university community. Eight people attended in person and
          twenty four joined online, and a recording is kept in the university's own media
          library. The letter below is written for the record rather than for me.
        </p>
        <a class="linkbtn src" href="/assets/docs/ksu-cybersecurity-talk-letter-2026.pdf">The university letter on the session (PDF)</a>
      </div>
    </article>
  </section>
</div>
""")

# ============================================================================
# WRITING
# ============================================================================
def article_card(a) -> str:
    plat = html.escape(a["platform"])
    return (f'<a class="article" href="{html.escape(a["url"])}" rel="noopener">'
            f'<span class="article-thumb">{plat}</span>'
            f'<span class="article-body">'
            f'<span class="article-title">{html.escape(a["title"])}</span>'
            f'<span class="article-meta">{plat}</span>'
            f'<span class="more">Read on {plat}</span></span></a>')


if ARTICLES:
    add("writing/index.html",
        "Writing | Pravin Khandke",
        "Technical articles by Pravin Khandke for practising engineers, with a link to each "
        "published article.",
        """
<section class="hero">
  <div class="wrap">
    <p class="kicker">Writing</p>
    <h1>Technical articles, linked to where they were published</h1>
    <p class="lede">
      Alongside the peer-reviewed work I write about architecture and reliability, and about
      the practical failure modes of AI systems in production, for readers who build systems
      rather than study them.
    </p>
  </div>
</section>

<div class="wrap">
  <section>
    <h2>Technical articles</h2>
    <div class="articles">
""" + "\n".join(article_card(a) for a in ARTICLES) + """
    </div>

    <h2>Coverage</h2>
    <ul class="claims">
""" + claim(
          "Interviewed by Authority Magazine for its C-Suite Perspectives on AI series, on "
          "where to use AI and where to rely only on humans. This is editorial coverage "
          "written by a third party about my work, rather than something I wrote.",
          [ext(
        "https://medium.com/authority-magazine/c-suite-perspectives-on-ai-pravin-khandke-on-where-to-use-ai-and-where-to-rely-only-on-humans-854b733e03a1",
        "Authority Magazine interview")]) + """
    </ul>
  </section>
</div>
""")

# ============================================================================
# PEER REVIEW
# ============================================================================
add("peer-review/index.html",
    "Peer review record | Pravin Khandke",
    "The international conferences where Pravin Khandke has reviewed submitted papers or "
    "served on a programme committee, each linked to its public listing where one exists, "
    "with the reviewer certificate where the conference issued one.",
    """
<section class="hero">
  <div class="wrap">
    <p class="kicker">Peer review and programme committees</p>
    <h1>The venues, named</h1>
    <p class="lede">
      I review submitted papers and serve on technical programme committees across four
      continents. The venues are listed individually below, because a named venue can be
      checked against the conference's own committee page and a total cannot.
    </p>
  </div>
</section>

<div class="wrap">
  <section>
    <h2>Technical programme committees</h2>
    <p>
      Committee service means deciding which submitted research is accepted and presented.
      Three appointments, one of which is an IEEE workshop co-located with a larger
      conference rather than a stand-alone event.
    </p>
    <ul class="plain committee-list">
""" + committee_rows_html() + """
    </ul>

    <h2>Peer review for conferences</h2>
    <p>
      The venues below are where I have reviewed submitted papers. The subject matter
      spans artificial intelligence and machine learning. It also covers distributed
      systems and the internet of things, and cloud computing.
    </p>
    <p>
      The list opens with the two flagship conferences. IECON is the flagship annual
      conference of the IEEE Industrial Electronics Society. IEEE GLOBECOM is one of the
      two flagship conferences of the IEEE Communications Society.
    </p>
    <ul class="plain venue-list">
""" + venue_rows_html() + """
    </ul>
    <p class="src-note">
      28 review venues plus three committee appointments. Links verified on
      """ + VERIFIED_DATE + """. Eight venues have no live listing to link.
    </p>

    <div class="note">
      <strong>On the count.</strong> No total number of reviews appears on this page. A
      total is the one figure a reader cannot check for themselves, so the venues are named
      instead. The authoritative number is stated in my application, which holds the review
      record conference by conference.
    </div>

    <h2>Reviewer certificates</h2>
    <p>
      A conference that issues a certificate has put its own name to the review, which is
      why these links open the document itself rather than describe it. Each one is signed
      by the chair of the conference that sent it.
    </p>
    <ul class="plain venue-list">
""" + certificate_rows_html() + """
    </ul>
    <p class="src-note">
      Reproduced as received, with the file size reduced for the web and the wording left
      untouched. A conference that has not issued a certificate is listed above and is not
      listed here.
    </p>

    <h2>Review platforms</h2>
    <p>
      Reviews are submitted through the conference management systems the organisers use.
      Each venue sets its own form and rating scale, which is why the review record is held
      per conference rather than summarised.
    </p>
  </section>
</div>
""")

# ============================================================================
# 404
# ============================================================================
add("404.html",
    "Page not found | Pravin Khandke",
    "That page does not exist on this site. Some sections are still being written and will be published here soon.",
    """
<section class="hero">
  <div class="wrap">
    <p class="kicker">Not found</p>
    <h1>That page does not exist</h1>
    <p class="lede">
      The address you followed does not match anything on this site. The pages that do
      exist are listed in the navigation above, or you can start from the
      <a href="/">home page</a>.
    </p>
    <div class="cta-row">
      <a class="btn" href="/">Home</a>
      <a class="btn ghost" href="/publications/">Publications</a>
      <a class="btn ghost" href="/standing/">Standing</a>
    </div>
    <div class="note">
      <strong>On the pages still being written.</strong> Parts of this site are being
      rebuilt. Sections that are not published yet will appear here soon, and a link you
      were given will start working once they are. Nothing is linked before it is ready.
    </div>
  </div>
</section>
""")

# ============================================================================
# redirects from the pre-2026-09 addresses
# ============================================================================
# The criterion pages used to live under /bcs/. Old links, including any an
# assessor has already saved, keep working through these stubs. The IET page was
# withdrawn, so it points home.
REDIRECTS = [
    ("bcs/invention/index.html", "/invention/"),
    ("bcs/consultancy/index.html", "/consultancy/"),
    ("bcs/mentoring/index.html", "/mentoring/"),
    ("bcs/standing/index.html", "/standing/"),
    ("iet/index.html", "/"),
]

def emit_redirects():
    for old, new in REDIRECTS:
        doc = (
            "<!DOCTYPE html>\n"
            '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="robots" content="noindex, nofollow">\n'
            f'<meta http-equiv="refresh" content="0; url={new}">\n'
            f'<link rel="canonical" href="{SITE["base"]}{new}">\n'
            f"<title>Moved to {new}</title>\n</head>\n<body>\n"
            f'<p>This page has moved. Continue to <a href="{new}">{new}</a>.</p>\n'
            "</body>\n</html>\n"
        )
        target = OUT / old
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(doc, encoding="utf-8")

# ============================================================================
# robots
# ============================================================================
# Search engines are asked not to index this site. It exists so that an assessing
# body can check claims made in an application, and it is reached from the links
# in that application rather than from a search result.
ROBOTS = """User-agent: *
Disallow: /

# Crawlers that ignore this file are handled by the meta robots tag on every page.
"""


# ============================================================================
# emit
# ============================================================================
def emit_meta():
    # CNAME tells GitHub Pages which custom domain to serve
    (OUT / "CNAME").write_text("oversightengineering.com\n", encoding="utf-8")
    # skip Jekyll: no build step needed, and it would ignore nothing we want
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    # keep the site out of search results
    (OUT / "robots.txt").write_text(ROBOTS, encoding="utf-8")

if __name__ == "__main__":
    if not ARTICLES:
        shutil.rmtree(OUT / "writing", ignore_errors=True)
    emit_meta()
    emit_redirects()
    total = sum(n for _, n in BUILT)
    print(f"built {len(BUILT)} pages, {total:,} bytes")
    for path, n in BUILT:
        print(f"  {n:>7,}  {path}")
    print("\nwrote docs/CNAME, docs/.nojekyll and docs/robots.txt")
