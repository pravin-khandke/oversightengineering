"""Checks for the built site.

Run:  python3 -m unittest discover -s tests -v

setUpModule builds the site into docs/, so every test reads the real output.
"""
import html
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

NAV = [
    ("/", "Home"),
    ("/career/", "Career"),
    ("/invention/", "Work"),
    ("/mentoring/", "Mentoring"),
    ("/standing/", "Community"),
    ("/publications/", "Papers and talks"),
    ("/peer-review/", "Peer review"),
    ("/writing/", "Writing"),
]
CURRENT = {
    "index.html": "Home",
    "invention/index.html": "Work",
    "consultancy/index.html": "Work",
    "mentoring/index.html": "Mentoring",
    "inspiring/index.html": "Mentoring",
    "career/index.html": "Career",
    "standing/index.html": "Community",
    "memberships/index.html": "Community",
    "publications/index.html": "Papers and talks",
    "talks/index.html": "Papers and talks",
    "peer-review/index.html": "Peer review",
    "writing/index.html": "Writing",
}
TOPIC_PAGES = [
    "invention/index.html", "consultancy/index.html", "mentoring/index.html",
    "standing/index.html", "memberships/index.html", "publications/index.html",
    "talks/index.html", "peer-review/index.html",
    "inspiring/index.html", "career/index.html",
]
STUBS = {
    "bcs/invention/index.html": "/invention/",
    "bcs/consultancy/index.html": "/consultancy/",
    "bcs/mentoring/index.html": "/mentoring/",
    "bcs/standing/index.html": "/standing/",
    "iet/index.html": "/",
}
SIBLINGS = [
    ("invention/", "consultancy/"),
    ("standing/", "memberships/"),
    ("publications/", "talks/"),
    ("mentoring/", "inspiring/"),
]


def build(out=None, **env):
    e = dict(os.environ)
    if out:
        e["SITE_OUT"] = str(out)
    e.update(env)
    subprocess.run([sys.executable, str(ROOT / "build.py")],
                   check=True, capture_output=True, env=e)


def setUpModule():
    build()


def read(rel):
    return (DOCS / rel).read_text(encoding="utf-8")


def all_html():
    return sorted(DOCS.rglob("*.html"))


def is_stub(path):
    return 'http-equiv="refresh"' in path.read_text(encoding="utf-8")


def real_pages():
    return [p for p in all_html() if not is_stub(p)]


def visible_text(raw):
    raw = re.sub(r"<(head|style|script)\b.*?</\1>", " ", raw, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", raw))


def nav_items(raw):
    block = re.search(r'<nav class="site-nav".*?</nav>', raw, re.S).group(0)
    return re.findall(r'<a href="([^"]+)"( aria-current="page")?>([^<]+)</a>', block)


def expected_nav():
    items = list(NAV)
    if not (DOCS / "writing" / "index.html").exists():
        items = [i for i in items if i[0] != "/writing/"]
    return items


class Structure(unittest.TestCase):
    def test_topic_pages_are_real_pages(self):
        for rel in TOPIC_PAGES:
            with self.subTest(rel=rel):
                self.assertTrue((DOCS / rel).exists(), f"{rel} is missing")
                self.assertFalse(is_stub(DOCS / rel), f"{rel} is still a redirect stub")

    def test_redirect_stubs_keep_resolving(self):
        for rel, target in STUBS.items():
            with self.subTest(rel=rel):
                self.assertIn(f'url={target}"', read(rel))

    def test_every_page_is_noindex(self):
        for p in all_html():
            with self.subTest(page=p.relative_to(DOCS).as_posix()):
                self.assertIn('<meta name="robots" content="noindex', p.read_text(encoding="utf-8"))
        self.assertIn("Disallow: /", (DOCS / "robots.txt").read_text())

    def test_topic_pages_have_a_sidebar(self):
        for rel in TOPIC_PAGES:
            with self.subTest(rel=rel):
                raw = read(rel)
                self.assertIn('<aside class="side"', raw)
                self.assertIn("On this page", raw)


class Navigation(unittest.TestCase):
    def test_same_items_on_every_real_page(self):
        for p in real_pages():
            with self.subTest(page=p.relative_to(DOCS).as_posix()):
                items = [(h, l) for h, _, l in nav_items(p.read_text(encoding="utf-8"))]
                self.assertEqual(items, expected_nav())

    def test_current_item_matches_the_page(self):
        for rel, label in CURRENT.items():
            if not (DOCS / rel).exists() or is_stub(DOCS / rel):
                continue
            with self.subTest(rel=rel):
                current = [l for _, c, l in nav_items(read(rel)) if c]
                self.assertEqual(current, [label])

    def test_sibling_pages_share_a_tab_strip(self):
        for group in SIBLINGS:
            for rel in group:
                with self.subTest(rel=rel):
                    strip = re.search(r'<nav class="subtabs".*?</nav>',
                                      read(rel + "index.html"), re.S)
                    self.assertIsNotNone(strip, f"{rel} has no tab strip")
                    for other in group:
                        self.assertIn(f'href="/{other}"', strip.group(0))


class Rules(unittest.TestCase):
    def test_no_dashes_or_semicolons_in_prose(self):
        for p in real_pages():
            text = visible_text(p.read_text(encoding="utf-8"))
            for bad, name in (("\u2014", "em dash"), ("\u2013", "en dash"), (";", "semicolon")):
                with self.subTest(page=p.relative_to(DOCS).as_posix(), bad=name):
                    self.assertNotIn(bad, text)

    def test_no_employer_commercial_figures(self):
        pats = ["8 million", "40,000", "nine billion", "29 per cent", "78 per cent",
                "500 customers", "5,000 invoice"]
        for p in real_pages():
            text = visible_text(p.read_text(encoding="utf-8"))
            for pat in pats:
                with self.subTest(page=p.relative_to(DOCS).as_posix(), pattern=pat):
                    self.assertIsNone(re.search(pat, text, re.I))

    def test_cases_and_claims_carry_a_source(self):
        for p in real_pages():
            raw = p.read_text(encoding="utf-8")
            blocks = re.findall(r'<article class="case">.*?</article>', raw, re.S)
            for ul in re.findall(r'<ul class="claims">(.*?)</ul>', raw, re.S):
                blocks += re.findall(r"<li\b.*?</li>", ul, re.S)
            for b in blocks:
                with self.subTest(page=p.relative_to(DOCS).as_posix(), item=visible_text(b).strip()[:60]):
                    self.assertTrue("Source:" in b or "claim-src" in b, "no source line")

    def test_no_awarding_body_names(self):
        pattern = re.compile(r"\b(bcs|iet)\b", re.I)
        for p in all_html():
            rel = p.relative_to(DOCS).as_posix()
            if rel.startswith(("bcs/", "iet/")):
                continue
            with self.subTest(page=rel):
                self.assertIsNone(pattern.search(p.read_text(encoding="utf-8")))

    def test_counters_agree_everywhere(self):
        got = dict(re.findall(r'data-counter="(\w+)">(\d+)<', read("index.html")))
        self.assertEqual(got, {"years": "26", "venues": "28",
                               "committees": "3", "publications": "3"})
        review = read("peer-review/index.html")
        self.assertEqual(review.count('class="venue-row"'), 28)
        self.assertEqual(review.count('class="committee-row"'), 3)
        self.assertEqual(read("publications/index.html").count('class="pub-entry"'), 3)

    def test_no_review_totals(self):
        pattern = re.compile(r"\d+\s+(papers|reviews)\s+(reviewed|completed)|reviews completed", re.I)
        for p in real_pages():
            with self.subTest(page=p.relative_to(DOCS).as_posix()):
                self.assertIsNone(pattern.search(visible_text(p.read_text(encoding="utf-8"))))

    def test_connect_row_is_orcid_linkedin_email_only(self):
        row = re.search(r'<div class="connect-row">(.*?)</div>', read("index.html"), re.S).group(1)
        hrefs = re.findall(r'href="([^"]+)"', row)
        self.assertEqual(len(hrefs), 3)
        self.assertTrue(hrefs[0].startswith("https://orcid.org/"))
        self.assertTrue(hrefs[1].startswith("https://www.linkedin.com/"))
        self.assertTrue(hrefs[2].startswith("mailto:"))

    def test_canonical_urls_are_clean(self):
        for p in real_pages():
            raw = p.read_text(encoding="utf-8")
            with self.subTest(page=p.relative_to(DOCS).as_posix()):
                canon = re.search(r'<link rel="canonical" href="([^"]+)"', raw).group(1)
                self.assertNotIn("index.html", canon)
                self.assertTrue(canon.startswith("https://oversightengineering.com/"))
                self.assertIn(f'<meta property="og:url" content="{canon}">', raw)

    def test_every_page_links_a_favicon_that_exists(self):
        self.assertTrue((DOCS / "favicon.svg").exists())
        for p in real_pages():
            with self.subTest(page=p.relative_to(DOCS).as_posix()):
                self.assertIn('<link rel="icon" href="/favicon.svg"', p.read_text(encoding="utf-8"))

    def test_publications_page_links_scholar_and_three_open_source_repos(self):
        raw = read("publications/index.html")
        self.assertIn("scholar.google.com/citations?user=e8zPvu8AAAAJ", raw)
        section = raw.split('<h2 id="open-source">')[1]
        for repo in ("hitl-manager", "scalable-event-driven-retail", "safe-ai-for-kids"):
            self.assertIn(f"github.com/pravin-khandke/{repo}", section)

    def test_no_phone_links(self):
        for p in all_html():
            with self.subTest(page=p.relative_to(DOCS).as_posix()):
                self.assertNotIn("tel:", p.read_text(encoding="utf-8"))


IMG = re.compile(r"<img\b[^>]*>")


def attr(tag, name):
    m = re.search(rf'\b{name}="([^"]*)"', tag)
    return m.group(1) if m else None


class Images(unittest.TestCase):
    def test_every_image_exists_and_has_alt_text(self):
        for p in real_pages():
            rel = p.relative_to(DOCS).as_posix()
            for tag in IMG.findall(p.read_text(encoding="utf-8")):
                with self.subTest(page=rel, tag=tag):
                    src, alt = attr(tag, "src"), attr(tag, "alt")
                    self.assertIsNotNone(alt, "image has no alt attribute")
                    if src.startswith("/"):
                        self.assertTrue((DOCS / src.lstrip("/")).exists(), f"{src} is missing")
                    if alt == "":
                        self.assertTrue(src.startswith("/assets/img/card-"),
                                        "only decorative card art may have empty alt text")

    def test_diagrams_are_placed_on_their_pages(self):
        self.assertIn("/assets/img/diagram-reconciliation.svg", read("invention/index.html"))
        self.assertIn("/assets/img/diagram-strangler.svg", read("consultancy/index.html"))

    def test_alt_text_is_unique_per_image(self):
        seen = {}
        for p in real_pages():
            for tag in IMG.findall(p.read_text(encoding="utf-8")):
                src, alt = attr(tag, "src"), attr(tag, "alt")
                if not alt:
                    continue
                with self.subTest(alt=alt):
                    self.assertEqual(seen.setdefault(alt, src), src,
                                     "two different images share one alt text")


class Links(unittest.TestCase):
    def test_internal_links_and_anchors_resolve(self):
        for p in real_pages():
            rel = p.relative_to(DOCS).as_posix()
            raw = p.read_text(encoding="utf-8")
            for href in re.findall(r'href="([^"]+)"', raw):
                if href.startswith(("http", "mailto:", "//")):
                    continue
                with self.subTest(page=rel, href=href):
                    path, _, frag = href.partition("#")
                    if path == "":
                        target = raw
                    else:
                        f = DOCS / path.lstrip("/")
                        if f.is_dir():
                            f = f / "index.html"
                        self.assertTrue(f.exists(), f"{href} does not resolve")
                        target = f.read_text(encoding="utf-8", errors="ignore") if f.suffix == ".html" else ""
                    if frag:
                        self.assertIn(f'id="{frag}"', target, f"no anchor #{frag}")


class Home(unittest.TestCase):
    def test_card_grid_links_every_topic(self):
        grid = re.search(r'<div class="grid">(.*?)\n    </div>\n  </section>', read("index.html"), re.S)
        self.assertIsNotNone(grid, "home page has no card grid")
        hrefs = re.findall(r'<a class="card" href="([^"]+)"', grid.group(1))
        for want in ("/invention/", "/mentoring/", "/standing/", "/publications/", "/peer-review/"):
            self.assertIn(want, hrefs)

    def test_highlights_are_dated_and_sourced(self):
        items = re.findall(r'<li class="tl-item">(.*?)</li>', read("index.html"), re.S)
        self.assertTrue(5 <= len(items) <= 8, f"{len(items)} highlights")
        for item in items:
            with self.subTest(item=item[:40]):
                self.assertIn("Source:", item)
                self.assertRegex(item, r"(January|February|March|April|May|June|July|August|September|October|November|December) 20\d\d")


class WritingPage(unittest.TestCase):
    def test_page_and_nav_exist_when_there_are_articles(self):
        self.assertTrue((DOCS / "writing" / "index.html").exists())
        self.assertFalse(is_stub(DOCS / "writing" / "index.html"))
        self.assertIn("/writing/", [h for h, _, _ in nav_items(read("index.html"))])

    def test_hidden_when_there_are_no_articles(self):
        with tempfile.TemporaryDirectory() as tmp:
            build(out=tmp, SITE_ARTICLES="none")
            out = pathlib.Path(tmp)
            self.assertFalse((out / "writing" / "index.html").exists())
            for page in out.rglob("*.html"):
                with self.subTest(page=page.relative_to(out).as_posix()):
                    self.assertNotIn("/writing/", page.read_text(encoding="utf-8"))
            self.assertEqual(len(nav_items((out / "index.html").read_text(encoding="utf-8"))), 7)

    def test_photo_without_alt_text_stops_the_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            img = pathlib.Path(tmp) / "assets" / "img"
            img.mkdir(parents=True)
            (img / "talk-aic-keynote.jpg").write_bytes(b"x")
            run = subprocess.run([sys.executable, str(ROOT / "build.py")],
                                 capture_output=True, text=True,
                                 env={**os.environ, "SITE_OUT": tmp})
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("IMAGES", run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
