# Site Rebuild and Evidence System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild oversightengineering.com as a scannable, linked, photo-bearing single-page front with four trimmed criterion pages, a private gitignored evidence store, and a refreshed actionable checklist.

**Architecture:** `build.py` stays the sole generator writing `docs/`. The home page becomes one scrolling document with anchor navigation; four criterion pages are trimmed and linked from it; folded pages become redirect stubs like `/bcs/*` already is. Evidence lives in an untracked `evidence/` tree. A committed link-probe script re-verifies every external URL on demand.

**Tech Stack:** Python 3 stdlib only (site has zero dependencies), plain HTML/CSS, macOS `sips` for the photo, headless browse (gstack) for verification.

**Spec:** `specs/2026-09-26-site-rebuild-design.md` — read it before any task. It carries the decisions this plan implements.

## Global Constraints

- No dependencies beyond Python 3 stdlib; `build.py` keeps running with `python3 build.py`
- `docs/` is machine-written: never hand-edit anything inside it
- Zero em dashes, zero en dashes, zero semicolons in any published prose
- No sentence with an inline comma list of three or more items
- No conclusory adjectives, no promotional language, every claim carries a source line
- No awarding body's name ("BCS", "IET") in any published file, any folder name, or any tracked file name — check with `grep -riwE "bcs|iet" docs/`
- No scanned certificates, no review confirmations, no employer documents published, ever
- No hero counter for the review count until the review-definition decision in the evidence register is made
- Home page paragraphs: three sentences maximum
- User memory rule: back up any file before patching (to `/tmp`, never into the repo tree)
- `.gitignore` must exist before any evidence lands; `git add -A` is never used
- Backup files go to `/tmp` or a path outside the repo, never `.bak` in the tree

## Review Focus

1. **Assessor with saved `/bcs/*` URLs** — the four URLs written in the submitted form must land on the right pages. Test: resolve each form URL and follow the redirect target (Task 9).
2. **Assessor printing the site** — print must show every link and every venue row, nothing behind interaction. Test: print stylesheet renders the full venue list with links (Task 6 verification).
3. **Phone-width visitor** — 375px, no horizontal scroll, hero photo scales. Test: browse at 375px (Tasks 4 and 7).
4. **Contest-fresh visitor** — counters must agree with the rows beside them: no review count, venues counter equals listed rows. Test: literal assertion comparing rendered counter to row count (Task 10).
5. **Public-repo visitor** — no personal data tracked anywhere. Test: `git status` clean of evidence paths, string check for body names (Tasks 1 and 13).

---

### Task 1: .gitignore and the private evidence skeleton

**Files:**
- Create: `.gitignore`
- Create: `evidence/README.md`
- Move (untrack): `EVIDENCE-CHECKLIST.md` → `evidence/EVIDENCE-CHECKLIST.md`
- Move (untrack): `EVIDENCE-TODO.md` → `evidence/EVIDENCE-TODO.md`
- Delete: `build.py.bak-20260926-125933` (move to `/tmp` first), `docs/assets/css/site.css.bak-20260926-125933` (delete outright, it is inside the publish root)

**Interfaces:**
- Produces: an untracked `evidence/` tree all later tasks write into; `.gitignore` patterns `evidence/`, `.superpowers/`, `.gstack/`, `.bak-*`, `.DS_Store`

- [ ] **Step 1: Back up the two stray .bak files to /tmp, then remove them from the tree**

```bash
cp build.py.bak-20260926-125933 /tmp/build.py.bak-20260926-125933
rm build.py.bak-20260926-125933 docs/assets/css/site.css.bak-20260926-125933
```

- [ ] **Step 2: Create .gitignore**

```gitignore
# private evidence store — never published, never tracked
evidence/

# scratch
.superpowers/
.gstack/
.bak-*
.DS_Store
```

- [ ] **Step 3: Create evidence/README.md**

```markdown
# Evidence store

Private working folder for the fellowship evidence record. Nothing here is
published. This folder is gitignored, so it exists only on this machine and
in any zip you make of it.

## What goes where

    criteria/
      01-invention-and-innovation/   publication, pipeline design material
      02-consultancy/                client work evidence, supporter confirmations
      03-mentoring-and-coaching/     mentoring records, capstone, children's AI standard
      04-community-standing/         talks, committee roles, reviews, writing, judging
    certificates/                    membership and role certificates
    reviews/                         review confirmations, documents, screenshots
    profile/                         photo, identity documents
    EVIDENCE-CHECKLIST.md            verification register (moved from repo root)
    EVIDENCE-TODO.md                 actionable gap list (moved from repo root)

The criteria layout mirrors the four criteria the applications use. The
folder names carry no awarding body's name, because the same evidence serves
any application and this machine syncs to a public host.
```

- [ ] **Step 4: Create the criteria/certificates/reviews/profile folders with .gitkeep-free empties**

```bash
mkdir -p evidence/criteria/01-invention-and-innovation \
         evidence/criteria/02-consultancy \
         evidence/criteria/03-mentoring-and-coaching \
         evidence/criteria/04-community-standing \
         evidence/certificates evidence/reviews evidence/profile
```

- [ ] **Step 5: Move the two tracked checklist files into evidence/ and untrack them**

```bash
git mv EVIDENCE-CHECKLIST.md evidence/EVIDENCE-CHECKLIST.md
git mv EVIDENCE-TODO.md evidence/EVIDENCE-TODO.md
git rm --cached -r evidence 2>/dev/null || git rm --cached evidence/EVIDENCE-CHECKLIST.md evidence/EVIDENCE-TODO.md
```

Expected: `git status` shows the files deleted from the index, and `evidence/` is ignored, not listed as untracked.

- [ ] **Step 6: Verify nothing private is tracked**

Run: `git status --porcelain` and `git check-ignore evidence && echo IGNORED`
Expected: no `evidence/` path appears as untracked, check-ignore prints `evidence`.

- [ ] **Step 7: Commit**

```bash
git add .gitignore
git add -u
git commit -m "chore: gitignore the evidence store and move the register private"
```

---

### Task 2: The link probe script

**Files:**
- Create: `probe_links.py` (repo root, beside build.py, not published)

**Interfaces:**
- Produces: `python3 probe_links.py` reads `docs/` as built, extracts every external `href`, probes each with a HEAD-then-GET fallback, prints one line per link (`200 url`) or the failure, and prints a `Verified on <date>` line. Task 10 stamps that date into the page. Exit code 0 only when every link is 200 or appears in the exceptions list inside the script.

- [ ] **Step 1: Write the script**

```python
#!/usr/bin/env python3
"""Probe every external link in docs/ so the check can be re-run at filing time.

Run:  python3 probe_links.py
Exit 0 when every link returns 200 or is a named exception. Print a
"Verified on" date line for the venue list to stamp.
"""
import pathlib, re, sys, urllib.request, datetime

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"
# Named exceptions: pages known dead or bot-blocked, named without a link there.
EXCEPTIONS = {
    "https://amity.edu/ICETM2026/Default.asp",   # 404
    "https://cicba2026.in/",                      # domain gone
    "https://pravin-khandke.hashnode.dev/",       # bot-blocked, verified manually
}

def links():
    text = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                     for p in OUT.rglob("*.html"))
    for href in re.findall(r'href="(https?://[^"]+)"', text):
        yield href

def probe(url):
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "Mozilla/5.0 linkcheck"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except Exception:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 linkcheck"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status
        except Exception as e:
            return str(e)

def main():
    urls = sorted(set(links()))
    bad = []
    for url in urls:
        status = probe(url)
        ok = (status == 200) or (url in EXCEPTIONS)
        print(("ok  " if ok else "FAIL") + f" {status}  {url}")
        if not ok:
            bad.append(url)
    print(f"\nprobed {len(urls)} links, {len(bad)} failing")
    print("Verified on " + datetime.date.today().strftime("%-d %B %Y"))
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it against the current site**

Run: `python3 probe_links.py`
Expected: the current site's links probe, most `ok 200`, the known exceptions accepted. Note any surprises in the commit message.

- [ ] **Step 3: Commit**

```bash
git add probe_links.py
git commit -m "feat: committed link probe for filing-time re-verification"
```

---

### Task 3: The photo

**Files:**
- Create: `docs/assets/img/profile.jpg` (via build step, see Task 8 wiring — the file itself is created here)

**Interfaces:**
- Produces: `/assets/img/profile.jpg`, EXIF stripped, exact pixel dimensions recorded in build.py's SITE dict as `"photo_w"` and `"photo_h"` in Task 5. The hero `<img>` uses these to reserve space.

- [ ] **Step 1: Copy and re-encode with sips (re-encoding strips EXIF)**

```bash
mkdir -p docs/assets/img
sips -s format jpeg \
  "/Users/pravinkhandke/Library/CloudStorage/GoogleDrive-pravin.khandke@ieee.org/My Drive/Pravin-Photo-website.jpeg" \
  --out docs/assets/img/profile.jpg
```

- [ ] **Step 2: Record the dimensions**

Run: `sips -g pixelWidth -g pixelHeight docs/assets/img/profile.jpg`
Expected: two integers, note them. The original is 944 wide by roughly 1200 tall. Downscale to a 480px-wide hero source so the page stays light:

```bash
sips -Z 480 docs/assets/img/profile.jpg
sips -g pixelWidth -g pixelHeight docs/assets/img/profile.jpg
ls -la docs/assets/img/profile.jpg
```

- [ ] **Step 3: Verify EXIF is gone**

Run: `sips -g all docs/assets/img/profile.jpg | grep -ci exif` (expect 0) and confirm the file size is under 100 KB.

- [ ] **Step 4: Do not commit yet**

`docs/` is fully regenerated by build.py in Task 8; commit everything together after the site builds.

---

### Task 4: The stylesheet

**Files:**
- Modify: `docs/assets/css/site.css` (back it up to `/tmp` first)

**Interfaces:**
- Produces: CSS classes the page tasks consume: `.hero-photo`, `.badge-chip`, `.stat`, `.stat-n`, `.stat-l`, `.connect-row`, `.section-rule`, `.work-card`, `.tag-row`, `.verify-grid`, `.verify-row`, `.pub-row`, `.edu-table`, plus the anchor-nav styles and an expanded print block.

- [ ] **Step 1: Back up**

```bash
cp docs/assets/css/site.css /tmp/site.css.pre-rebuild
```

- [ ] **Step 2: Rewrite the token block and add the new component styles**

Replace the `:root` palette with one accent system and append the new components. Keep every existing class the current pages use so nothing breaks mid-rebuild:

```css
:root {
  --bg: #ffffff;
  --ink: #111418;
  --muted: #5a6470;
  --accent: #14406b;      /* deep blue, evidence not marketing */
  --line: #e4e8ee;
  --soft: #f6f8fb;        /* soft section background */
}
```

New component styles to append (bodies trimmed to the essence, full rules written in the file):

- `.hero-photo img` — circular crop, fixed diameter with `aspect-ratio: 1`, `object-fit: cover`
- `.badge-chip` — 1px `--line` border, radius 999px, small sans text
- `.stat` — right-aligned stack, `.stat-n` large serif number, `.stat-l` letterspaced small label
- `.connect-row` — flex row of external links with the existing `.ext` arrow marker
- `.section-rule` — heading with a bottom rule line, matching the reference sites
- `.work-card` — white card, 1px border, radius 8px, `.tag-row` of small chips inside
- `.verify-row` — one recognition per row: name, grade detail, source link right-aligned
- `.pub-row` — one publication per row, title left, venue and link right
- `.edu-table` — compact two-column table for education and work history

- [ ] **Step 3: Extend the print stylesheet**

Print rules: expand any folded content (none exists by design), drop the hero photo background, force link URLs visible after links (`a[href^="http"]::after { content: " (" attr(href) ")"; font-size: 0.85em; }` scoped to `.claim-src` and `.verify-row` so the page does not drown in URLs), keep the venue list whole.

- [ ] **Step 4: Verify against the built site later** — Task 7 step 4 does the 375px and 1280px browse pass; do not close this task on visual judgement alone.

- [ ] **Step 5: Commit with the site build** — Task 8 commits the stylesheet together with the pages that use it, so no intermediate commit publishes a half-styled site.

---

### Task 5: build.py home page, top (hero and about)

**Files:**
- Modify: `build.py` — SITE dict (add `photo_w`, `photo_h`, new `updated` date), FOOTER (new links), `nav()` (anchor variant), the `index.html` `add()` call (lines 162 to ~230)

**Interfaces:**
- Consumes: `/assets/img/profile.jpg` (Task 3), `.hero-photo`, `.badge-chip`, `.stat`, `.connect-row` classes (Task 4)
- Produces: home page anchors `#about #invention #leadership #mentoring #standing #recognitions #publications #education` that Task 6 fills and Task 9's redirect targets use. `nav_home()` emits anchor links; the existing `nav()` stays for detail pages.

- [ ] **Step 1: Back up build.py**

```bash
cp build.py /tmp/build.py.pre-rebuild
```

- [ ] **Step 2: Update SITE, FOOTER and add nav_home()**

SITE gains: `"photo_w": <from Task 3>`, `"photo_h": <from Task 3>`, `"updated": "26 September 2026"`.
FOOTER links change from `/memberships/ /publications/ /peer-review/ /talks/` to home anchors `/#recognitions /#publications /#standing /#about`. The footer's "BCS fellowship application" phrase becomes "fellowship application".

```python
def nav_home():
    items = [
        ("#about", "About"),
        ("#invention", "Invention"),
        ("#leadership", "Leadership"),
        ("#mentoring", "Mentoring"),
        ("#standing", "Standing"),
        ("#recognitions", "Recognitions"),
        ("#publications", "Publications"),
        ("#education", "Education"),
    ]
    out = [f'      <li><a href="{href}">{label}</a></li>' for href, label in items]
    return '<ul class="nav-list">\n' + "\n".join(out) + "\n    </ul>"
```

- [ ] **Step 3: Rewrite the index.html body, hero and about**

New hero: photo right (circular, width/height from SITE so space is reserved), kicker "Fellowship evidence record", name with surname in accent, tagline row, three badge chips (IEEE Senior Member, RSS Fellow, SEFM Eminent Fellow), four counters each carrying a `data-counter` attribute (`years`, `venues`, `committees`, `publications` — Task 10 asserts the venues counter against the row count; the venues value is `len(VENUE_ROWS)`), connect row (Scholar `https://scholar.google.com/citations?hl=en&authuser=7&user=e8zPvu8AAAAJ`, ORCID, LinkedIn, email). About section: the existing three-sentence bio paragraph from the current about aside, kept verbatim, under `#about`. Meta description becomes "Public record of the work, recognition and professional service cited in Pravin Khandke's fellowship application."

- [ ] **Step 4: Build and smoke-test**

Run: `python3 build.py && python3 - <<'EOF'
import pathlib
t = pathlib.Path("docs/index.html").read_text()
assert "assets/img/profile.jpg" in t, "photo missing"
assert 'id="about"' in t, "about anchor missing"
assert "BCS" not in t, "body name leaked"
print("smoke ok")
EOF`
Expected: `smoke ok`.

---

### Task 6: build.py home page, body (invention, leadership, mentoring, standing)

**Files:**
- Modify: `build.py` — continue the index.html body after the about section

**Interfaces:**
- Consumes: anchors from Task 5, `.work-card`, `.tag-row` classes, `claim()` and `ext()` helpers
- Produces: full-record links to `/invention/`, `/consultancy/`, `/mentoring/`, `/standing/`; the standing section structure Task 10 fills with linked venue rows

- [ ] **Step 1: Write the four sections**

Each section: `section-rule` heading, two or three `.work-card` blocks with the tag row, one claim-style source line, and a full-record link. Copy is trimmed from the existing detail pages, three sentences per card maximum:

- `#invention` — card 1: the remittance reconciliation pipeline (human oversight at the centre, matches below threshold stop for a person, every validation logged for audit). Card 2: the ActiveMQ Artemis event-driven retail backbone. Source lines link IJCA and `https://iccbi.com/`.
- `#leadership` — card 1: the Cox Automotive platform retirement, service by service, no downtime window. Card 2: the canonical data model adopted as the client's standing integration standard. Card 3: the financial services reconciliation and engagement lifecycle work. Full-record link to `/consultancy/`.
- `#mentoring` — card 1: engineers developed inside the teams. Card 2: the sponsored university capstone. Card 3: the children's AI safety open standard, linking `https://github.com/pravin-khandke/safe-ai-for-kids`. Full-record link to `/mentoring/`.
- `#standing` — sub-headed rows, not tabs: Speaking (three rows: AIC 2026 keynote linking `https://scrs.in/conference/aic2026`, Extract Summit linking `https://www.extractsummit.io/speakers`, ICCBI linking `https://iccbi.com/`), Committees (four rows), Peer review (venue rows, filled by Task 10), Writing (five rows linking dev.to, hashnode, medium), Judging (Georgia Tech and KSU). Full-record link to `/standing/`.

- [ ] **Step 2: Build and smoke-test**

```bash
python3 build.py && python3 - <<'EOF'
import pathlib
t = pathlib.Path("docs/index.html").read_text()
for a in ("invention", "leadership", "mentoring", "standing"):
    assert f'id="{a}"' in t, a
for u in ("/invention/", "/consultancy/", "/mentoring/", "/standing/"):
    assert f'href="{u}"' in t, u
print("sections ok")
EOF`
```

---

### Task 7: build.py home page, tail (recognitions, publications, education)

**Files:**
- Modify: `build.py` — continue the index.html body, then the 404 page links

**Interfaces:**
- Consumes: `.verify-row`, `.pub-row`, `.edu-table` classes, `.verify-grid`
- Produces: the recognitions grid Task 10 may extend; the education table carrying the form-aligned dates from the pinned resume; 404 links updated to anchors

- [ ] **Step 1: Recognitions section**

`#recognitions`: a `.verify-row` per recognition, register links only, no scans:

- IEEE Senior Member, elevated June 2026, member 102303821
- Eminent Fellow Member (SEFM), conferred June 2026, linking `https://www.sassociety.com/membership-id-sas-sefm-770-2026/`
- RSS Fellow, July 2026, membership 263939
- AIC 2026 keynote, named on the organiser's speaker list, linking `https://scrs.in/conference/aic2026`

A source note under the grid: "Recognition is verified against the awarding body's own register rather than a scanned certificate."

- [ ] **Step 2: Publications section**

`#publications`: one `.pub-row` each for the two papers (IJCA article, ICCBI 2026 paper linking `https://iccbi.com/`) and the five technical articles with their dev.to, hashnode and medium URLs from the pinned resume.

- [ ] **Step 3: Education section**

`#education`: `.edu-table` with the four degrees from the pinned resume, and a four-role work history table (Insight Global Oct 2022 to present, Amadeus Apr 2021 to Oct 2022, Capgemini Senior Consultant Mar 2008 to Apr 2021, Capgemini Consultant May 2004 to Mar 2008) — these are the pinned resume dates. The register's item 21 records the site's account and migration dates as contested; the form extract in Task 12 is the reconciliation point, and if the form disagrees with any date in this table, the table flips to the form's dates and the checklist records the change. A source note names the resume as the source.

- [ ] **Step 4: Update the 404 page**

404 links change from `/publications/` and `/peer-review/` to `/#publications` and `/#standing`.

- [ ] **Step 5: Build and full-page browse check**

```bash
python3 build.py
B="$HOME/.claude/skills/gstack/browse/dist/browse"
$B goto file://$PWD/docs/index.html
$B viewport 375x812 && $B screenshot /tmp/home-375.png
$B viewport 1280x900 && $B screenshot /tmp/home-1280.png
$B js "document.documentElement.scrollWidth <= 375"   # true at 375px
```

Read both screenshots, fix what looks wrong, repeat. No horizontal scroll, photo crops cleanly, counters aligned.

---

### Task 8: Commit the rebuilt home site

**Files:**
- All of Tasks 3, 4, 5, 6, 7 land in this one commit so nothing publishes half-styled.

- [ ] **Step 1: Full verification of the built tree**

```bash
python3 build.py
python3 probe_links.py
grep -riwE "bcs|iet" docs/ && echo "LEAK" || echo "clean"
```

Expected: probe exits 0, string check prints clean (the `/bcs/` redirect stubs are exempt — they carry no prose; if grep hits them, the check is scoped to exclude the stub pattern).

- [ ] **Step 2: Screenshots to the user**

Show `/tmp/home-375.png` and `/tmp/home-1280.png` with the Read tool before committing.

- [ ] **Step 3: Commit**

```bash
git add build.py probe_links.py docs/
git commit -m "redesign: single-page evidence record with photo, counters and linked venues"
```

---

### Task 9: Folded pages become redirect stubs

**Files:**
- Modify: `build.py` — REDIRECTS list; delete the `add()` calls for memberships, publications, talks, peer-review; update README.md and DEPLOY.md

**Interfaces:**
- Consumes: home anchors from Task 5
- Produces: redirect stubs preserving every URL an assessor or the form may have saved

- [ ] **Step 1: Extend REDIRECTS and remove the folded pages**

```python
REDIRECTS = [
    ("bcs/invention/index.html", "/invention/"),
    ("bcs/consultancy/index.html", "/consultancy/"),
    ("bcs/mentoring/index.html", "/mentoring/"),
    ("bcs/standing/index.html", "/standing/"),
    ("iet/index.html", "/"),
    ("memberships/index.html", "/#recognitions"),
    ("publications/index.html", "/#publications"),
    ("talks/index.html", "/#standing"),
    ("peer-review/index.html", "/#standing"),
]
```

Delete the four `add()` calls and their page content from build.py. The `/bcs/*` and `/iet/` stubs stay exactly as they are: the four `http://oversightengineering.com/bcs/...` URLs written in the submitted form keep working, and the form is not edited. `docs/iet/index.html` as a stub already points home and keeps doing so.

- [ ] **Step 2: Verify the form URLs land correctly**

```bash
python3 build.py
B="$HOME/.claude/skills/gstack/browse/dist/browse"
for p in invention consultancy mentoring standing; do
  $B goto "file://$PWD/docs/bcs/$p/index.html"
  $B js "document.querySelector('meta[http-equiv=refresh]').content"
done
```

Expected: each prints `0; url=/invention/` (and consultancy, mentoring, standing).

- [ ] **Step 3: Update README.md and DEPLOY.md**

README layout section: evidence/ tree (with a "gitignored, private" note, not a path listing of its contents), the new page set, `probe_links.py`, the specs/ and plans/ folders. DEPLOY.md: unchanged pipeline, note the HTTPS action item and the probe re-run at filing time.

- [ ] **Step 4: Verify and commit**

```bash
python3 build.py && ls docs/ && grep -riwE "bcs|iet" docs/ | grep -v "bcs/.*/index.html" ; echo "check done"
git add build.py README.md DEPLOY.md docs/
git commit -m "refactor: fold memberships, publications, talks and peer-review into home stubs"
```

---

### Task 10: Every venue linked, counters reconciled

**Files:**
- Modify: `build.py` — the standing section's committees and peer-review rows; the venues counter constant

**Interfaces:**
- Consumes: the pinned resume `~/Documents/BCS/BCS_Final/Resume-Pravin-Khandke.md`, the 13 September audit verdicts in `evidence/EVIDENCE-CHECKLIST.md`, probe script from Task 2
- Produces: `VENUE_ROWS` list in build.py; the counter for venues equals `len(VENUE_ROWS)`, asserted in the smoke test

- [ ] **Step 1: Encode the per-venue table in build.py**

```python
# name, url (None = no link, with reason in the row), role
VENUE_ROWS = [
    ("IECON 2026", "https://www.iecon2026.org/", "review"),
    ("IEEE GLOBECOM 2026", "https://globecom2026.ieee-globecom.org/", "review"),
    ("ICCUBEA 2026", "https://iccubea.pccoepune.com/iccubea.php", "review"),
    ("ICETCI 2026", "http://www.ietcint.com/", "review"),
    ("ICDCECE 2026", "https://icdcece.in/", "review"),
    ("AMLDS 2026", "https://amlds.site/", "review"),
    ("NGSME 2026", "https://sites.google.com/view/ngmse2026/home", "review"),
    ("CAISAIS 2026", "https://caisais26.ajman.ac.ae", "review"),
    ("AIIoT 2026", "https://worldaiiotcongress.org/technical-committee/", "review"),
    ("CEECT 2026", "https://www.ceect.org/", "review"),
    ("MeditCom 2026", "https://meditcom2026.ieee-meditcom.org/", "review"),
    ("ICoIAS 2026", "https://www.icias.org/index.html", "review"),
    ("iSemantic 2026", "https://isemantic.dinus.ac.id/2026/", "review"),
    ("INCOSST 2026", "https://incosst.polteksci.ac.id/", "review"),
    ("INTCEC 2026", "https://intcec.org/", "review"),
    ("ICTMOD 2026", "https://ictmod-conference.com/", "review"),
    ("ETECOM 2026", "https://ieee-etecom.org/", "review"),
    ("SIME 2026", "https://sime-conf.org/committees/", "review"),
    ("ICETM 2026", None, "review"),        # venue site returns 404
    ("CICBA 2026", None, "review"),        # venue domain no longer resolves
    ("TEMSMET 2026", None, "review"),      # no public listing in any record
    ("ARIIA 2026", None, "review"),
    ("ICNSBT 2026", None, "review"),
    ("CICA 2026", None, "review"),
    ("ICAITech 2026", None, "review"),
    ("PlatCon 2026", None, "review"),
]
COMMITTEE_ROWS = [
    ("NGSME 2026 Workshop", "https://sites.google.com/view/ngmse2026/home"),
    ("AIIoT 2026", "https://worldaiiotcongress.org/technical-committee/"),
    ("SIME 2026", "https://sime-conf.org/committees/"),
    ("BDAA 2026", "https://bdaa-conference.com/"),
]
```

Committee venues link to the committee page where it names Pravin (AIIoT, SIME verified; NGSME homepage serves as its listing; BDAA homepage). Rows without a URL carry the reason as plain text: "no public listing" or "venue site offline". Under the list: "Links verified on <date from probe_links.py output>. Eight venues have no live listing to link."

- [ ] **Step 2: Re-run the probe, stamp the date**

Run: `python3 probe_links.py`, take the Verified-on date, put it in the source note. Fix or annotate anything that fails.

- [ ] **Step 3: Assert the counters agree with the rows**

```bash
python3 build.py && python3 - <<'EOF'
import pathlib, re
t = pathlib.Path("docs/index.html").read_text()
rows = len(re.findall(r'class="venue-row"', t))
n = re.search(r'data-counter="venues">(\d+)', t)
assert n and int(n.group(1)) == rows, f"counter {n and n.group(1)} != rows {rows}"
assert "73" not in re.sub(r'<[^>]+>', '', t), "contested review count leaked"
print(f"venues counter == {rows} rows")
EOF`
```

(If the venue-row markup differs, adjust the two selectors together, never one alone.)

- [ ] **Step 4: Commit**

```bash
git add build.py docs/
git commit -m "feat: link every venue, reconcile the counters with the rows"
```

---

### Task 11: The evidence copy

**Files:**
- Create: `evidence/eb1a_evidence/` (full tree), `evidence/reviews/` (Drive Peerreview files), `evidence/EVIDENCE-CHECKLIST.md` (mapping and gap log appended)

**Interfaces:**
- Consumes: `~/Documents/EB1A/EB1A_Evidence` (complete copy), the Google Drive Peerreview folder (path located in step 1)
- Produces: a complete local evidence tree with originals untouched, a mapping table and gap log in the checklist

- [ ] **Step 1: Locate the Drive Peerreview folder**

```bash
find "/Users/pravinkhandke/Library/CloudStorage/GoogleDrive-pravin.khandke@ieee.org/My Drive" \
  -maxdepth 2 -iname "*peerreview*" -o -maxdepth 2 -iname "*peer review*" 2>/dev/null
```

Note the exact path; if absent, search one level deeper or by the review-file names already known (IECON, iSemantic confirmations). Record the path in the checklist.

- [ ] **Step 2: Full copy, originals untouched**

```bash
rsync -a "$HOME/Documents/EB1A/EB1A_Evidence/" "$HOME/Documents/GitHub/oversightengineering/evidence/eb1a_evidence/"
du -sh evidence/eb1a_evidence
```

- [ ] **Step 3: Copy the review files**

```bash
rsync -a "<drive peerreview path>/" "$HOME/Documents/GitHub/oversightengineering/evidence/reviews/"
find evidence/reviews -type f | wc -l
```

Expected count: roughly the 73 files the register counts (36 confirmations, 27 review documents, 9 screenshots), plus whatever the Drive folder holds beyond them.

- [ ] **Step 4: Verify nothing from evidence/ is tracked**

Run: `git status --porcelain | grep evidence` — expect no output. `git check-ignore evidence` — expect a hit.

- [ ] **Step 5: Append the mapping and gap log to evidence/EVIDENCE-CHECKLIST.md**

A table mapping each EB1A source folder (`00_Profile_Snapshot`, `01_Authorship_Scholarly_Articles`, `02_Original_Contributions`, `03_Judging_Activities`, `03_Published_Material`, `04_Memberships_Awards`, `05_Awards`, `05_Leading_or_Critical_Role`, `06_Media_Coverage`, `07_High_Remuneration`, `08_Speaking_Engagements`, `09_Other_Supporting`, `10_Recommendation_Letters`, `11_Petition_Assembly`, `12_RFE_Response`, `Research_Papers`) to the criteria folder or certificate/review/profile folder it feeds, and the gap log: SIME, TEMSMET, ARIIA, ICNSBT have no evidence folder, CICA and ICTMOD have empty ones.

- [ ] **Step 6: No commit** — `evidence/` is untracked by design. Verify with `git status` that the working tree is clean apart from intended changes.

---

### Task 12: The checklist refresh

**Files:**
- Modify: `evidence/EVIDENCE-CHECKLIST.md`, `evidence/EVIDENCE-TODO.md`

**Interfaces:**
- Consumes: the pinned form `~/Documents/BCS/BCS_Final/bcs-fellow-application-form-pravin-khandke.docx`, the pinned resume, the Task 11 copy
- Produces: the reconciled register and the actionable missing-items list

- [ ] **Step 1: Extract the form text (stdlib, no deps)**

```bash
python3 - <<'EOF'
import zipfile, re, pathlib
z = zipfile.ZipFile("/Users/pravinkhandke/Documents/BCS/BCS_Final/bcs-fellow-application-form-pravin-khandke.docx")
xml = z.read("word/document.xml").decode("utf-8")
text = re.sub(r"<[^>]+>", " ", xml)
text = re.sub(r"\s+", " ", text)
pathlib.Path("/tmp/form-extract.txt").write_text(text)
print(len(text), "chars")
EOF`
```

Read `/tmp/form-extract.txt` for: the claimed figures (review count and definition, venue count), the four site URLs, the Capgemini and Cox dates, and every claim naming the site.

- [ ] **Step 2: Reconcile the register**

Against the form text and the resume, update the checklist's per-claim table: mark closed what Tasks 1 to 10 closed (venue links, stubs, photo, unindexed confirmations), recompute the open counts, and resolve the site-vs-resume date conflicts by listing the form as source of truth once its dates are confirmed.

- [ ] **Step 3: Refresh the TODO**

Each open item keeps the `[site]`/`[file]` marker and the Me/You owner, gains a one-line what-and-where, and the list is ordered by what unlocks the most. Add the user action items:

- HTTPS: certificate is null and enforcement is off twelve days after cutover. Re-save the custom domain under Settings, Pages, or open a GitHub support thread. Until fixed, assessors land on Not secure.
- The review-definition decision (66 strict vs 73 loose) before any review count is published anywhere.
- A Web of Science Researcher Profile.
- The supporter confirmation for the consultancy claims.

- [ ] **Step 4: Verify the counts**

Every count stated in either file must be recomputed from `find evidence -type f` and the probe output, not carried over. State the computation next to each count.

- [ ] **Step 5: No commit** — both files are untracked. Show the user the new TODO top section.

---

### Task 13: Final verification pass

- [ ] **Step 1: Build and probe**

```bash
python3 build.py && python3 probe_links.py
```

- [ ] **Step 2: docs/ contents check**

`find docs -type f | sort` — every file is one the generator wrote, plus `CNAME`, `.nojekyll`, `robots.txt`, `assets/img/profile.jpg`. Nothing else.

- [ ] **Step 3: Form URL check**

For each of the four `http://oversightengineering.com/bcs/...` URLs from the form extract: `curl -sI` returns 200 and a meta refresh is present. Also `curl -sI https://oversightengineering.com/` — if HTTPS still fails, the checklist action item stays open and says so.

- [ ] **Step 4: String check**

`grep -riwE "bcs|iet" docs/ | grep -v "docs/bcs/" | grep -v "docs/iet/"` — expect no hits (stub stubs are prose-free).

- [ ] **Step 5: Browse pass**

Home and all four detail pages at 375px and 1280px: screenshots read, no horizontal scroll, print preview (`$B pdf /tmp/print-check.pdf --print-background`) renders every venue link as a URL.

- [ ] **Step 6: Commit anything remaining, report status to the user with the screenshots and the new TODO top section**