#!/usr/bin/env python3
"""
Static site generator for oversightingengineering.com

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

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"

SITE = {
    "domain": "oversightengineering.com",
    "base": "https://oversightengineering.com",
    "name": "Pravin Khandke",
    "tagline": "Applied researcher and systems architect",
    "field": "Human-in-the-Loop AI and Autonomous Agent Systems for Collaborative Workflows",
    "email": "pravin.khandke@ieee.org",
    "orcid": "https://orcid.org/0009-0004-9693-9334",
    "orcid_id": "0009-0004-9693-9334",
    "updated": "13 September 2026",
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
    <p class="foot-line">{name} &middot; {field}</p>
    <p class="foot-line small">
      <a href="/memberships/">Memberships</a> &middot;
      <a href="/publications/">Publications</a> &middot;
      <a href="/peer-review/">Peer review</a> &middot;
      <a href="/talks/">Talks</a> &middot;
      <a href="mailto:{email}">{email}</a>
    </p>
    <p class="foot-line small muted">
      This site is the public record of the work cited in my fellowship applications.
      It was last reviewed on {updated}. Where a claim rests on a document held by a
      third party, that document is linked rather than reproduced.
    </p>
  </div>
</footer>
"""

def nav(current: str) -> str:
    items = [
        ("", "Home"),
        ("memberships/", "Memberships"),
        ("bcs/invention/", "Invention and innovation"),
        ("bcs/consultancy/", "Consultancy"),
        ("bcs/mentoring/", "Mentoring and coaching"),
        ("bcs/standing/", "Public influencer"),
        ("publications/", "Publications"),
        ("talks/", "Talks"),
        ("peer-review/", "Peer review"),
        ("iet/", "IET"),
    ]
    out = []
    for href, label in items:
        cur = ' aria-current="page"' if href == current else ""
        out.append(f'      <li><a href="/{href}"{cur}>{label}</a></li>')
    return '<ul class="nav-list">\n' + "\n".join(out) + "\n    </ul>"


BASE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="{name}">
<link rel="canonical" href="{base}/{path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{base}/{path}">
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

def page(path, title, desc, body):
    navkey = path[:-len("index.html")] if path.endswith("index.html") else path
    doc = BASE.format(
        title=title, desc=desc, name=SITE["name"], base=SITE["base"],
        tagline=SITE["tagline"], path=path, nav=nav(navkey),
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
AIC_LIST = "https://scrs.in/conference/aic2026"
KIDS_REPO = "https://github.com/pravin-khandke/safe-ai-for-kids"
ORCID = "https://orcid.org/0009-0004-9693-9334"

# ============================================================================
# HOME
# ============================================================================
add("index.html",
    "Pravin Khandke | Fellowship evidence record",
    "Public record of the work, recognition and professional service cited in "
    "Pravin Khandke's BCS and IET fellowship applications.",
    """
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">Fellowship evidence record</p>
    <h1>Every claim I make to an assessing body, checkable</h1>
    <p class="lede">
      I am an applied researcher and systems architect working on human-in-the-loop AI and
      autonomous agent systems for collaborative workflows. This site exists so that an
      assessor, or anyone validating a statement, can follow each claim back to the source
      it rests on.
    </p>
    <ul class="creds">
      <li>
        <span class="grade">IEEE Senior Member</span>
        <span class="body-name">Institute of Electrical and Electronics Engineers</span>
        <span class="num">Elevated June 2026 &middot; member 102303821</span>
      </li>
      <li>
        <span class="grade">Eminent Fellow Member (SEFM)</span>
        <span class="body-name">The Scholars Academic and Scientific Society</span>
        <span class="num">Conferred June 2026 &middot; lifetime honour</span>
      </li>
      <li>
        <span class="grade">Member</span>
        <span class="body-name">Royal Statistical Society</span>
        <span class="num">July 2026 &middot; member 263939</span>
      </li>
    </ul>
    <div class="cta-row">
      <a class="btn" href="/publications/">Publications</a>
      <a class="btn ghost" href="/peer-review/">Peer review record</a>
    </div>
  </div>
</section>

<div class="wrap">
  <section>
    <h2>What this site holds</h2>
    <p>
      The four sections below are the ones I have evidenced for BCS Fellowship. Each page sets
      out the situation and the work I did, then what changed. The supporting source sits
      beside the claim.
    </p>
    <div class="grid two">
      <div class="card">
        <span class="kicker">Body of work</span>
        <h3><a class="card-link" href="/bcs/invention/">Invention and innovation</a></h3>
        <p>A human-in-the-loop pipeline that reconciles customer remittances arriving
        through four separate channels, and the peer-reviewed publication of the pattern
        behind it.</p>
      </div>
      <div class="card">
        <span class="kicker">Body of work</span>
        <h3><a class="card-link" href="/bcs/consultancy/">Consultancy</a></h3>
        <p>Advisory work on retiring a continental-scale automotive data platform, where a
        recommended data model became the client organisation's standing integration
        standard.</p>
      </div>
      <div class="card">
        <span class="kicker">Professional impact</span>
        <h3><a class="card-link" href="/bcs/mentoring/">Mentoring and coaching</a></h3>
        <p>Structured development of engineers inside my teams, a sponsored university
        capstone, and an open standard for children's use of AI.</p>
      </div>
      <div class="card">
        <span class="kicker">Standing in the community</span>
        <h3><a class="card-link" href="/bcs/standing/">Public influencer</a></h3>
        <p>Keynotes at recognised external events. Technical programme committees at
        international conferences. A peer review record and sustained written work on
        digital and IT topics.</p>
      </div>
    </div>

    <h2>Supporting records</h2>
    <div class="grid three">
      <div class="card">
        <h3><a class="card-link" href="/memberships/">Memberships</a></h3>
        <p>Grades held, the body that conferred each, and a verification link where one
        exists.</p>
      </div>
      <div class="card">
        <h3><a class="card-link" href="/publications/">Publications</a></h3>
        <p>Peer-reviewed papers and technical writing, with links to the published
        record.</p>
      </div>
      <div class="card">
        <h3><a class="card-link" href="/talks/">Talks</a></h3>
        Keynotes and invited talks, with the organiser's own listing where it is public.
        listing where it is public.</p>
      </div>
      <div class="card">
        <h3><a class="card-link" href="/peer-review/">Peer review</a></h3>
        <p>The international venues where I have reviewed submissions, named rather than
        counted.</p>
      </div>
      <div class="card">
        <h3><a class="card-link" href="/iet/">IET</a></h3>
        <p>The criteria I am preparing for IET Fellowship, and how that application differs
        from the BCS one.</p>
      </div>
      <div class="card">
        <span class="kicker">Identifiers</span>
        <h3>Where to verify me</h3>
        <p><a href="https://orcid.org/0009-0004-9693-9334">ORCID 0009-0004-9693-9334</a></p>
        <p><a href="https://www.linkedin.com/in/pravin-khandke">linkedin.com/in/pravin-khandke</a></p>
      </div>
    </div>

    <div class="note">
      <strong>On what is not here.</strong> Where evidence is confidential to an employer,
      discloses commercial figures, or contains another person's personal data, it is
      supplied to the assessing body directly rather than published. Internal performance
      data appears in the application, not on this site. Nothing here is a scanned
      certificate, because the awarding body's own register is the better source.
    </div>

    <h2>Contact and identifiers</h2>
""" + IDENTIFIERS + """
  </section>
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
    <p class="eyebrow">Memberships and fellowships</p>
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
      "Member of the Royal Statistical Society, membership number 263939, since July 2026. "
      "The Society is the United Kingdom professional body for statistics, founded in 1834 "
      "and incorporated by Royal Charter. Its members are styled Fellows, and Fellowship "
      "is the Society's standard grade rather than a grade confined to high achievement. I "
      "list it here as an affiliation of record and not as a selective honour, and I record "
      "it separately from the two graded memberships above for that reason.",
      [ext("https://rss.org.uk/", "Royal Statistical Society")]) + """
    </ul>

    <div class="note">
      <strong>Why the distinction is stated.</strong> The two graded memberships above were
      conferred through assessment. Royal Statistical Society Fellowship is open to anyone
      with an interest in statistics. Presenting them as equivalent would misrepresent the
      record, so the difference is set out here rather than left for a reader to discover.
    </div>
  </section>
</div>
""")

# ============================================================================
# BCS — INVENTION AND INNOVATION
# ============================================================================
add("bcs/invention/index.html",
    "Invention and innovation | Pravin Khandke",
    "A human-in-the-loop pipeline that reconciles customer remittances arriving through "
    "four separate channels, and the peer-reviewed publication of the pattern behind it.",
    """
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">BCS Fellowship &middot; Body of work</p>
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
      [ext(IJCA, "IJCA 2026, where the pattern is published")]) + "\n" + claim(
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
      "ActiveMQ Artemis, IEEE ICCBI 2026. The messaging architecture that moves collected "
      "and reconciled data between systems.",
      [ext("https://iccbi.com/", "IEEE ICCBI 2026")]) + """
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
add("bcs/consultancy/index.html",
    "Consultancy | Pravin Khandke",
    "Advisory work on retiring a continental-scale automotive data platform, where a "
    "recommended data model became the client organisation's standing integration standard.",
    """
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">BCS Fellowship &middot; Body of work</p>
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
      quality across a distributed team split between the United States and India. Keeping
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
      "I advised on the delivery through a distributed team split between the United States "
      "and India, and the platform was handed to the client's own engineers at the end of "
      "the engagement. Handing over was the objective. The client runs it without us.",
      ["Client confirmation available through the named supporter"]) + """
    </ul>

    <h2>What changed</h2>
    <p>
      The programme completed with no disruption to live dealer operations, start to
      finish. The distributed platform took over the transaction load the mainframe had
      carried, and the data model and messaging patterns established during the work remain
      the foundation the organisation builds on. Colleagues who stayed on the account have
      confirmed that it still runs on the architecture set at the time.
    </p>

    <div class="note">
      <strong>On the client test.</strong> The BCS Consultancy criterion asks for
      collaboration with various clients. My record evidences this one client in depth
      rather than several in less depth. Whether that is enough is the assessor's call, and
      I have not stretched the record to make it look broader than it is.
    </div>

    <h2>Dates</h2>
    <p>
      I worked on the Cox Automotive account from 2004 to 2022, serving it from Capgemini's
      Pune delivery centre before relocating to Atlanta. The mainframe migration itself ran
      from 2013 to 2022.
    </p>
  </section>
</div>
""")

# ============================================================================
# BCS — MENTORING AND COACHING
# ============================================================================
add("bcs/mentoring/index.html",
    "Mentoring and coaching | Pravin Khandke",
    "Structured development of engineers inside my teams, a sponsored university capstone, "
    "and an open standard for children's use of AI.",
    """
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">BCS Fellowship &middot; Professional impact</p>
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
      "Technology, guiding an undergraduate team through the design and delivery of an AI "
      "knowledge management platform. I sponsored the work rather than merely advising on "
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
      "I authored an open, age-banded standard for children's use of AI, published as a "
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
      <strong>What I have not claimed here.</strong> The BCS rubric's top tier asks for
      documented career outcomes such as a mentee reaching an executive role. The engineers
      I developed hold senior and lead positions, and I have described them as such rather
      than reaching for a stronger claim. Named individuals and their current roles appear
      in the application, where the people concerned can verify them.
    </div>
  </section>
</div>
""")

# ============================================================================
# BCS — PUBLIC INFLUENCER
# ============================================================================
add("bcs/standing/index.html",
    "Public influencer | Pravin Khandke",
    "Keynotes at recognised events, technical programme committees at international "
    "conferences, a peer review record, and sustained written work on digital and IT topics.",
    """
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">BCS Fellowship &middot; Standing in the community</p>
    <h1>Invited to speak, asked to judge, and read beyond my own organisation</h1>
    <p class="lede">
      Standing in a profession shows up as other people asking you to do something. The
      invitations on this page came from conference organisers and journal editors. Each
      one is listed with the organiser's own public record where one exists.
    </p>
  </div>
</section>

<div class="wrap">
  <section>
    <h2>Keynote and conference speaking</h2>
    <ul class="claims">
""" + claim(
      "Keynote speaker at the 2026 IEEE 5th World Conference on Applied Intelligence and "
      "Computing, held in Jabalpur, India on 29 and 30 August 2026. My talk was The Trust "
      "Gap: Architecting Autonomous AI Systems for Real-World Accountability, It covered how agent "
      "systems fail in production and how to verify them. It also argued that trust should "
      "include the sustainability cost of running them.",
      [ext(AIC_LIST, "Conference programme, where the keynote list is published")]) + "\n" + claim(
      "Confirmed speaker at Extract Summit 2026, held at Brazos Hall in Austin, Texas on 7 "
      "and 8 October 2026. My session is The Naive AI Trap: Why Finance-Grade Extraction "
      "Needs Hybrid Agents, on the second day.",
      [ext("https://www.extractsummit.io/", "Extract Summit programme")]) + """
    </ul>

    <h2>Technical programme committees</h2>
    <p>
      I serve on the technical programme committees of four international venues, where the
      work is deciding which submitted research is accepted and presented. One of the four
      is an IEEE workshop rather than a full conference, and I describe it as such.
    </p>
    <ul class="venues">
      <li>AIIoT 2026 <span class="where">IEEE World AI IoT Congress, Seattle, United States</span></li>
      <li>BDAA 2026 <span class="where">2nd International Conference on Big Data Analytics and Applications, Las Palmas de Gran Canaria, Spain</span></li>
      <li>SIME 2026 <span class="where">Sousse, Tunisia</span></li>
      <li>NGSME 2026 <span class="where">IEEE workshop, Vilamoura, Portugal</span></li>
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
      "Two peer-reviewed publications, one in the International Journal of Computer "
      "Applications and one in the proceedings of an IEEE-sponsored conference, covering "
      "human-in-the-loop interfaces and event-driven architectures.",
      [ext("/publications/", "Publications, with a link to each paper")]) + "\n" + claim(
      "Sustained technical writing for engineers, published on developer platforms and read "
      "outside my own organisation, The subjects are architecture and "
      "reliability, and the practical failure modes of AI systems in production.",
      [ext("https://dev.to/pravin-khandke", "Dev.to"),
       ext("https://pravin-khandke.hashnode.dev/", "Hashnode")]) + "\n" + claim(
      "Interviewed by Authority Magazine for its C-Suite Perspectives series, on where to "
      "use AI and where to rely only on humans. This is third-party editorial coverage "
      "rather than writing of my own, which is why I list it separately.",
      [ext("https://medium.com/authority-magazine", "Authority Magazine")]) + """
    </ul>

    <h2>Universities</h2>
    <p>
      I have judged student computing projects at Kennesaw State University, most recently
      on the spring 2026 Computing Showcase panel. That sits with the rest of the development
      work on the <a href="/bcs/mentoring/">mentoring page</a>
      rather than being counted twice.
    </p>

    <div class="note">
      <strong>Why everything here is linked.</strong> BCS asks for evidence of influence
      that is publicly available. A claim that cannot be checked is worth less than a
      smaller claim that can, so where an organiser publishes its own record of an
      invitation, that record is the source rather than my account of it.
    </div>
  </section>
</div>
""")

# ============================================================================
# PUBLICATIONS
# ============================================================================
add("publications/index.html",
    "Publications | Pravin Khandke",
    "Peer-reviewed papers, conference presentations and technical writing, with a link to "
    "each published record.",
    """
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">Publications and writing</p>
    <h1>Published work, with the record linked</h1>
    <p class="lede">
      Peer-reviewed papers come first. Conference presentations follow, then writing for
      practising engineers. Each entry links to the published version rather than
      quoting it.
    </p>
  </div>
</section>

<div class="wrap">
  <section>
    <h2>Peer-reviewed papers</h2>
    <ul class="claims">
""" + claim(
      "<strong>Designing Adaptive Human-in-the-Loop Interfaces for Enhanced Collaborative "
      "Incident Management.</strong> International Journal of Computer Applications, 2026. "
      "Examines interface architectures in which human operators and AI systems jointly "
      "manage complex incident workflows, with cognitive task allocation shifting according "
      "to the operator's state and the system's own confidence. It is the published "
      "statement of the human-in-the-loop pattern I apply to production systems.",
      [ext(IJCA, "International Journal of Computer Applications")]) + "\n" + claim(
      "<strong>Scalable Event-Driven Architectures for Distributed Retail Data Collection "
      "Using ActiveMQ Artemis.</strong> IEEE ICCBI 2026, the 5th International Conference "
      "on Computer Networks, Big Data and IoT. Examines high-throughput messaging "
      "topologies for multi-site data aggregation, using ActiveMQ Artemis as the backbone "
      "for event propagation across independently governed retail nodes. Presented in "
      "Dubai in June 2026.",
      [ext("https://iccbi.com/", "IEEE ICCBI 2026")]) + """
    </ul>

    <h2>Conference presentations</h2>
    <ul class="claims">
""" + claim(
      "Presented Scalable Event-Driven Architectures for Distributed Retail Data Collection "
      "Using ActiveMQ Artemis at IEEE ICCBI 2026, Dubai, June 2026.",
      [ext("https://iccbi.com/", "Conference programme")]) + "\n" + claim(
      "Keynote, The Trust Gap: Architecting Autonomous AI Systems for Real-World "
      "Accountability, at the 2026 IEEE 5th World Conference on Applied Intelligence and "
      "Computing, Jabalpur, India, August 2026.",
      [ext(AIC_LIST, "Conference programme, keynote list")]) + "\n" + claim(
      "The Naive AI Trap: Why Finance-Grade Extraction Needs Hybrid Agents, Extract Summit "
      "2026, Austin, Texas, October 2026. Accepted session title, as it appears in the "
      "programme.",
      [ext("https://www.extractsummit.io/", "Extract Summit programme")]) + """
    </ul>

    <h2>Writing for practising engineers</h2>
    <p>
      Alongside the peer-reviewed work I write about architecture and reliability, and\n      about the practical failure modes of AI systems in production, for readers who build\n      systems rather than study them.
    </p>
    <ul class="claims">
""" + claim(
      "Feature Flags That Actually Ship: Lessons from the Trenches. Dev.to.",
      [ext("https://dev.to/pravin-khandke/feature-flags-that-actually-ship-lessons-from-the-trenches-b7a", "Dev.to")]) + "\n" + claim(
      "Messaging in the Age of AI. Dev.to.",
      [ext("https://dev.to/pravin-khandke/messaging-in-the-age-of-ai-26h7", "Dev.to")]) + "\n" + claim(
      "Clean Code at Scale: How Sonar Became Our Silent Reviewer. Hashnode.",
      [ext("https://pravin-khandke.hashnode.dev/clean-code-at-scale-how-sonar-became-our-silent-reviewer", "Hashnode")]) + "\n" + claim(
      "The Emergence of Explainable AI in Deep Learning. Hashnode.",
      [ext("https://pravin-khandke.hashnode.dev/", "Hashnode")]) + "\n" + claim(
      "Backend Architecture in the Age of AI. Medium.",
      [ext("https://medium.com/@Pravin-Khandke/backend-architecture-in-the-age-of-ai-e73cc8bbf599", "Medium")]) + """
    </ul>

    <h2>Third-party coverage</h2>
    <ul class="claims">
""" + claim(
      "Interviewed by Authority Magazine for its C-Suite Perspectives on AI series, on where "
      "to use AI and where to rely only on humans. This is editorial coverage written by a "
      "third party about my work, rather than something I wrote.",
      [ext("https://medium.com/authority-magazine", "Authority Magazine")]) + """
    </ul>

    <div class="note">
      <strong>On the publication record.</strong> I list two peer-reviewed papers, which is
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
add("talks/index.html",
    "Talks and keynotes | Pravin Khandke",
    "Keynote and conference speaking, with the organiser's own published record where it "
    "exists.",
    """
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">Talks and keynotes</p>
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
    <h2>Keynote</h2>
    <ul class="claims">
""" + claim(
      "<strong>The Trust Gap: Architecting Autonomous AI Systems for Real-World "
      "Accountability.</strong> Keynote at the 2026 IEEE 5th World Conference on Applied "
      "Intelligence and Computing, Jabalpur, India, 29 and 30 August 2026. The talk covers how "
      "autonomous agent systems fail once they leave a demonstration, and how to verify them "
      "before they are trusted. It also argues that the sustainability cost of running them "
      "belongs in the same conversation as their accuracy.",
      [ext(AIC_LIST, "Conference programme and keynote list")]) + """
    </ul>

    <h2>Conference sessions</h2>
    <ul class="claims">
""" + claim(
      "<strong>The Naive AI Trap: Why Finance-Grade Extraction Needs Hybrid Agents.</strong> "
      "Extract Summit 2026, Brazos Hall, Austin, Texas, 7 and 8 October 2026, on the second "
      "day. The session covers why extraction that has to be correct, as opposed to merely "
      "plausible, needs hybrid agent designs rather than a single model in a loop.",
      [ext("https://www.extractsummit.io/", "Extract Summit programme")]) + "\n" + claim(
      "<strong>Scalable Event-Driven Architectures for Distributed Retail Data "
      "Collection.</strong> Presented at IEEE ICCBI 2026, Dubai, June 2026, alongside the "
      "published paper.",
      [ext("https://iccbi.com/", "IEEE ICCBI 2026 programme")]) + """
    </ul>

    <h2>University talks</h2>
    <p>
      I speak to students about cybersecurity and applied AI. These sessions are arranged
      directly with the institutions rather than through a published programme, so details
      are provided in my application rather than claimed here as public events.
    </p>
  </section>
</div>
""")

# ============================================================================
# PEER REVIEW
# ============================================================================
add("peer-review/index.html",
    "Peer review record | Pravin Khandke",
    "The international conferences and journals where Pravin Khandke has reviewed submitted "
    "papers, named rather than counted.",
    """
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">Peer review and technical programme committees</p>
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
      Four appointments, one of which is an IEEE workshop co-located with a larger
      conference rather than a stand-alone event.
    </p>
    <ul class="venues">
      <li>AIIoT 2026 <span class="where">IEEE World AI IoT Congress, Seattle, United States</span></li>
      <li>BDAA 2026 <span class="where">2nd International Conference on Big Data Analytics and Applications, Las Palmas de Gran Canaria, Spain</span></li>
      <li>SIME 2026 <span class="where">Sousse, Tunisia</span></li>
      <li>NGSME 2026 <span class="where">IEEE workshop on next-generation multimedia services at the edge, Vilamoura, Portugal</span></li>
    </ul>

    <h2>Peer review for conferences</h2>
    <p>
      Reviews completed for the venues below. The subject matter spans artificial
      intelligence and machine learning. It also covers distributed systems and the
      internet of things, and cloud computing.
    </p>
    <ul class="venues">
      <li>IECON 2026 <span class="where">IEEE Industrial Electronics Society annual conference, Doha, Qatar</span></li>
      <li>IEEE GLOBECOM 2026 <span class="where">IEEE Global Communications Conference</span></li>
      <li>IEEE MeditCom 2026 <span class="where">IEEE Mediterranean Conference on Communications and Networking, Cagliari, Italy</span></li>
      <li>ICCUBEA 2026 <span class="where">IEEE International Conference on Computing, Communication, Control and Automation, Pune, India</span></li>
      <li>ICETM 2026 <span class="where">International Conference on Engineering, Technology and Management, New Jersey, United States</span></li>
      <li>AMLDS 2026 <span class="where">International Conference on Advanced Machine Learning and Data Science, Osaka, Japan</span></li>
      <li>ICDCECE 2026 <span class="where">International Conference on Distributed Computing and Electrical-Electronic Circuits, Karnataka, India</span></li>
      <li>ICETCI 2026 <span class="where">International Conference on Emerging Techniques in Computational Intelligence, Hyderabad, India</span></li>
      <li>ICoIAS 2026 <span class="where">International Conference on Intelligent Autonomous Systems, Qinhuangdao, China</span></li>
      <li>CAISAIS 2026 <span class="where">International Conference on Advances in Artificial Intelligence, Security and Information Systems, Ajman, United Arab Emirates</span></li>
      <li>CEECT 2026 <span class="where">International Conference on Advances in Computer Science, Electrical, Electronics and Communication Technologies, Bangkok, Thailand</span></li>
      <li>NGSME 2026 <span class="where">IEEE workshop, Vilamoura, Portugal</span></li>
      <li>iSemantic 2026 <span class="where">International Seminar on Application for Technology of Information and Communication, Semarang, Indonesia</span></li>
      <li>CICBA 2026 <span class="where">International Conference on Computational Intelligence and Big Data Analytics, Malda, India</span></li>
      <li>INCOSST 2026 <span class="where">International Conference on Smart Science and Technology, Cirebon, Indonesia</span></li>
      <li>INTCEC 2026 <span class="where">Interdisciplinary Conference on Electrics and Computer</span></li>
    </ul>

    <div class="note">
      <strong>On the count.</strong> I have deliberately not put a total number of reviews
      on this page. My written records reconcile to a documented count, and where a venue
      has more papers assigned than completed reviews on file, the lower figure is the true
      one. The authoritative number, with the documents behind it, is stated in my
      application. Listing the venues is the part that can be independently checked.
    </div>

    <h2>Review platforms</h2>
    <p>
      Reviews are submitted through the conference management systems the organisers\n      use. These include EDAS, CMT and EasyChair. The IEEE Industrial Electronics Society\n      runs its own portal. Each venue sets its own form and rating scale, which is why the
      review record is held per conference rather than summarised.
    </p>
  </section>
</div>
""")

# ============================================================================
# IET (in preparation)
# ============================================================================
add("iet/index.html",
    "IET Fellowship preparation | Pravin Khandke",
    "The criteria being prepared for IET Fellowship, and how that application differs from "
    "the BCS one.",
    """
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">In preparation</p>
    <h1>IET Fellowship, and how it differs from BCS</h1>
    <p class="lede">
      IET Fellowship is a separate application to a separate body, with different rules and
      a different bar. This page records the criteria I am preparing and what each one needs.
      It is a plan rather than a submission.
    </p>
  </div>
</section>

<div class="wrap">
  <section>
    <h2>What IET requires</h2>
    <table>
      <caption>Requirements that differ from the BCS application</caption>
      <thead>
        <tr><th scope="col">Requirement</th><th scope="col">What it means for me</th></tr>
      </thead>
      <tbody>
        <tr><td>Two to three criteria, from a list of nine</td><td>Narrower than BCS. I am preparing Repute and Insight and Experience.</td></tr>
        <tr><td>Sustained at a high level for five or more years, usually within the last ten</td><td>Requires a continuity timeline before any narrative is written, not after.</td></tr>
        <tr><td>A CV is not accepted</td><td>The CV content has to be turned into criterion statements. It cannot be attached or repackaged.</td></tr>
        <tr><td>An organisational chart is mandatory for Leadership and Responsibility</td><td>Neither of those criteria is among the two I am preparing, which is part of why they were not chosen.</td></tr>
        <tr><td>Two supporters</td><td>One more than BCS requires.</td></tr>
        <tr><td>Five hundred words per criterion</td><td>More room per criterion than BCS allows, on fewer criteria.</td></tr>
        <tr><td>Do not send certificates, publication lists, or courses attended</td><td>The IET does not want an evidence dump. Links exist only to validate key evidence.</td></tr>
      </tbody>
    </table>

    <h2>Criterion 1: Repute</h2>
    <p class="pill">In preparation</p>
    <p>
      Public recognition at national or international level. The record I am assembling
      covers IEEE Senior Member and the society fellowship. It also covers service on
      international conference committees and the invited keynote. The question this criterion turns on is not
      whether the recognition exists, but whether it is recognised outside my own
      organisation and outside my own country, which the committee appointments and the
      keynote answer.
    </p>

    <h2>Criterion 2: Insight and Experience</h2>
    <p class="pill">In preparation</p>
    <p>
      Recognition as a consultant, technical specialist and subject expert. The material
      here overlaps the BCS Consultancy section but is written for a different test. The
      IET asks for sustained achievement at a high level, so the emphasis falls on the
      continuity of the advisory work and on the decisions taken within it, rather than on
      a single engagement.
    </p>

    <h2>What is not decided yet</h2>
    <ul class="plain">
      <li>Whether a third criterion is worth adding, and if so which one.</li>
      <li>Which two supporters to approach, and whether either should be an IET Fellow.</li>
      <li>Whether the five-year continuity test is met by the current record across the full window, or only across part of it.</li>
    </ul>

    <div class="note">
      <strong>On publishing this page.</strong> The IET explicitly discourages sending
      publication lists and certificates. This page is therefore a statement of which
      criteria I am preparing and what each requires, not a collection of documents. The
      evidence itself goes to the IET through its own form.
    </div>
  </section>
</div>
""")

# ============================================================================
# 404
# ============================================================================
add("404.html",
    "Page not found | Pravin Khandke",
    "That page does not exist on this site.",
    """
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">Not found</p>
    <h1>That page does not exist</h1>
    <p class="lede">
      The address you followed does not match anything on this site. The pages that do
      exist are listed in the navigation above, or you can start from the
      <a href="/">home page</a>.
    </p>
    <div class="cta-row">
      <a class="btn" href="/">Home</a>
      <a class="btn ghost" href="/publications/">Publications</a>
      <a class="btn ghost" href="/peer-review/">Peer review</a>
    </div>
  </div>
</section>
""")

# ============================================================================
# emit
# ============================================================================
def emit_meta():
    # CNAME tells GitHub Pages which custom domain to serve
    (OUT / "CNAME").write_text("oversightengineering.com\n", encoding="utf-8")
    # skip Jekyll: no build step needed, and it would ignore nothing we want
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

if __name__ == "__main__":
    emit_meta()
    total = sum(n for _, n in BUILT)
    print(f"built {len(BUILT)} pages, {total:,} bytes")
    for path, n in BUILT:
        print(f"  {n:>7,}  {path}")
    print("\nwrote docs/CNAME and docs/.nojekyll")
