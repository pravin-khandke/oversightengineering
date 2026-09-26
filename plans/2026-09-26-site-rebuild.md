# Site Rebuild and Evidence System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild oversightengineering.com as a scannable, linked, photo-bearing single-page front with four trimmed criterion pages, a private gitignored evidence store, and a refreshed actionable checklist.

**Architecture:** `build.py` stays the sole generator writing `docs/`. The home page becomes one scrolling document with anchor navigation; four criterion pages are trimmed and linked from it; folded pages become redirect stubs like `/bcs/*` already is. Evidence lives in an untracked `evidence/` tree. A committed link-probe script re-verifies every external URL on demand. The application form is extracted to text before any date or figure is published.

**Tech Stack:** Python 3 stdlib only (site has zero dependencies), plain HTML/CSS, macOS `sips` for the photo, headless browse (gstack) for verification.

**Spec:** `specs/2026-09-26-site-rebuild-design.md` — read it before any task. It carries the decisions this plan implements, including the scope of the no-body-name rule and the counter set.

## Global Constraints

- No dependencies beyond Python 3 stdlib; `build.py` keeps running with `python3 build.py`
- `docs/` HTML is machine-written by build.py: never hand-edit generated pages. Two exceptions are hand-maintained and survive rebuilds because build.py only writes in place: `docs/assets/css/site.css` and `docs/assets/img/`
- Zero em dashes, zero en dashes, zero semicolons in any published prose
- No sentence with an inline comma list of three or more items
- No conclusory adjectives, no promotional language, every claim carries a source line
- No awarding body's name ("BCS", "IET") in anything under `docs/` or in any folder name — check with `grep -riwE "bcs|iet" docs/`. `specs/` and `plans/` are exempt working documents (spec decision)
- No scanned certificates, no review confirmations, no employer documents published, ever
- Hero counters are exactly: 26 years, the venue count the page totals, 4 committees, 2 publications. No review counter until the review-definition decision in the evidence register is made
- The connect row is ORCID, LinkedIn, email. Google Scholar stays off the site (register ruling)
- Home page paragraphs: three sentences maximum
- User memory rule: back up any file before patching (to `/tmp`, never into the repo tree)
- `.gitignore` exists from Task 1; `git add -A` is never used

## Review Focus

1. **Assessor with saved `/bcs/*` URLs** — the four URLs written in the submitted form must land on the right pages. Test: resolve each form URL and follow the redirect target (Task 10).
2. **Assessor printing the site** — print must show every link and every venue row, nothing behind interaction. Test: print stylesheet renders the full venue list with link URLs (Task 14).
3. **Phone-width visitor** — 375px, no horizontal scroll, hero photo scales. Test: browse at 375px (Tasks 5 and 8).
4. **Contest-fresh visitor** — counters agree with the rows beside them: no review count, venues counter equals the review rows listed and the page states the committee count separately. Test: literal assertion (Task 11).
5. **Public-repo visitor** — no personal data tracked anywhere. Test: `git status` clean of evidence paths, string check for body names (Tasks 1 and 14).

---

### Task 1: .gitignore and the private evidence skeleton

**Files:**
- Create: `.gitignore`
- Create: `evidence/README.md`
- Move (untrack): `EVIDENCE-CHECKLIST.md` → `evidence/EVIDENCE-CHECKLIST.md`
- Move (untrack): `EVIDENCE-TODO.md` → `evidence/EVIDENCE-TODO.md`
- Delete: `build.py.bak-20260926-125933` (to `/tmp` first), `docs/assets/css/site.css.bak-20260926-125933` (delete outright, it is inside the publish root)

**Interfaces:**
- Produces: an untracked `evidence/` tree all later tasks write into; ignore patterns `evidence/`, `.superpowers/`, `.gstack/`, `.bak-*`, `.DS_Store`

- [ ] **Step 1: Back up the stray .bak files, then remove them from the tree**

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
    form-extract.txt                 text pulled from the application form (Task 4)

The criteria layout mirrors the four criteria the applications use. The
folder names carry no awarding body's name, because the same evidence serves
any application and this machine syncs to a public host.
```

- [ ] **Step 4: Create the folder skeleton**

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
git rm --cached evidence/EVIDENCE-CHECKLIST.md evidence/EVIDENCE-TODO.md
```

Expected: `git status --porcelain` shows no `evidence/` path at all once the moves are staged and the ignore rule is in place.

- [ ] **Step 6: Verify nothing private is tracked**

Run: `git check-ignore evidence && echo IGNORED` — expect `evidence IGNORED`. Run: `git status --porcelain` — expect no untracked `evidence/` line.

- [ ] **Step 7: Commit, path-limited so the modified spec does not ride along**

```bash
git add .gitignore
git commit -m "chore: gitignore the evidence store and move the register private"
```

`git mv` already staged the moves, so nothing else is swept in.

---

### Task 2: The link probe script

**Files:**
- Create: `probe_links.py` (repo root, beside build.py, not published)

**Interfaces:**
- Produces: `python3 probe_links.py` extracts every external `href` from `docs/`, probes each HEAD-then-GET, prints one line per link, then prints `Verified on <date>`. Task 11 stamps that date into the page. Exit 0 only when every link is 200 or appears in the script's exceptions set.

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
# Named exceptions: known dead or bot-blocked targets, named without a link there.
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
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method,
                                     headers={"User-Agent": "Mozilla/5.0 linkcheck"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status
        except Exception:
            continue
    return "unreachable"

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
Expected: the current site's links probe, most `ok 200`, known exceptions accepted. Note any surprises in the commit message.

- [ ] **Step 3: Commit**

```bash
git add probe_links.py
git commit -m "feat: committed link probe for filing-time re-verification"
```

---

### Task 3: The photo

**Files:**
- Create: `docs/assets/img/profile.jpg` (hand-maintained asset, survives rebuilds)

**Interfaces:**
- Produces: `/assets/img/profile.jpg`, EXIF stripped, exact pixel dimensions recorded in build.py's SITE dict as `photo_w` and `photo_h` in Task 6 so the hero reserves space

- [ ] **Step 1: Copy and re-encode with sips (re-encoding strips EXIF)**

```bash
mkdir -p docs/assets/img
sips -s format jpeg \
  "/Users/pravinkhandke/Library/CloudStorage/GoogleDrive-pravin.khandke@ieee.org/My Drive/Pravin-Photo-website.jpeg" \
  --out docs/assets/img/profile.jpg
```

- [ ] **Step 2: Downscale to a hero-sized source and record dimensions**

```bash
sips -Z 480 docs/assets/img/profile.jpg
sips -g pixelWidth -g pixelHeight docs/assets/img/profile.jpg
ls -la docs/assets/img/profile.jpg
```

Expected: two integers to carry into Task 6, file under 100 KB.

- [ ] **Step 3: Verify EXIF is gone**

Run: `sips -g all docs/assets/img/profile.jpg | grep -ci exif` — expect `0`.

- [ ] **Step 4: Do not commit yet** — Task 9 commits everything together after the site builds.

---

### Task 4: Extract the application form (before any date is published)

**Files:**
- Create: `evidence/form-extract.txt` (untracked)

**Interfaces:**
- Produces: the form's full text at `evidence/form-extract.txt`. Task 8's education table reads its dates from here. Task 13 reconciles its figures from here.

- [ ] **Step 1: Extract with stdlib only**

```bash
python3 - <<'EOF'
import zipfile, re, pathlib
src = "/Users/pravinkhandke/Documents/BCS/BCS_Final/bcs-fellow-application-form-pravin-khandke.docx"
z = zipfile.ZipFile(src)
xml = z.read("word/document.xml").decode("utf-8")
text = re.sub(r"<[^>]+>", " ", xml)
text = re.sub(r"\s+", " ", text)
out = pathlib.Path("/Users/pravinkhandke/Documents/GitHub/oversightengineering/evidence/form-extract.txt")
out.write_text(text, encoding="utf-8")
print(len(text), "chars")
EOF
```

- [ ] **Step 2: Read it for the figures this plan depends on**

Grep the extract for: the review count and its definition, the venue count, the four `http://oversightengineering.com/bcs/...` URLs (pin their exact strings into Task 10's verification), and the Capgemini and Cox dates. Record the four URLs and the dates at the top of `evidence/EVIDENCE-CHECKLIST.md` under a new "Pinned from the form" heading.

- [ ] **Step 3: Verify nothing private is tracked**

Run: `git status --porcelain | grep -c evidence` — expect `0`.

---

### Task 5: The stylesheet

**Files:**
- Modify: `docs/assets/css/site.css` (back it up to `/tmp` first)

**Interfaces:**
- Produces: CSS classes the page tasks consume: `.hero-photo`, `.badge-chip`, `.stat`, `.stat-n`, `.stat-l`, `.connect-row`, `.section-rule`, `.work-card`, `.tag-row`, `.verify-grid`, `.verify-row`, `.pub-row`, `.edu-table`, plus anchor-nav styles and an expanded print block

- [ ] **Step 1: Back up**

```bash
cp docs/assets/css/site.css /tmp/site.css.pre-rebuild
```

- [ ] **Step 2: Rewrite the token block and append the new components**

Replace the `:root` palette:

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

Append the new components, keeping every existing class the current pages use so nothing breaks mid-rebuild:

- `.hero-photo img` — circular crop, `aspect-ratio: 1`, `object-fit: cover`
- `.badge-chip` — 1px `--line` border, radius 999px, small sans text
- `.stat` — right-aligned stack, `.stat-n` large serif number, `.stat-l` letterspaced small label
- `.connect-row` — flex row of external links with the existing `.ext` arrow marker
- `.section-rule` — heading with a bottom rule line
- `.work-card` — white card, 1px border, radius 8px, `.tag-row` of small chips inside
- `.verify-row` — one recognition per row: name, grade detail, source link right-aligned
- `.pub-row` — one publication per row, title left, venue and link right
- `.edu-table` — compact two-column table for education and work history

- [ ] **Step 3: Extend the print stylesheet**

Print rules: force the target URL visible after external links, scoped so the page does not drown (`a[href^="http"]::after { content: " (" attr(href) ")"; font-size: 0.85em; }` applied within `.claim-src`, `.verify-row` and the venue list), drop decorative backgrounds, keep the venue list whole.

- [ ] **Step 4: Visual verification happens with the built site** — Tasks 8 and 14 do the 375px and 1280px browse passes.

- [ ] **Step 5: Commit with the site build** — Task 9 commits the stylesheet together with the pages that use it, so no intermediate commit publishes a half-styled site.

---

### Task 6: build.py home page, top (hero and about)

**Files:**
- Modify: `build.py` — SITE dict (add `photo_w`, `photo_h`, `updated`), BASE template (og:image), FOOTER (new links), `nav_home()` added, the `index.html` `add()` call

**Interfaces:**
- Consumes: `/assets/img/profile.jpg` (Task 3), `.hero-photo`, `.badge-chip`, `.stat`, `.connect-row` classes (Task 5)
- Produces: home anchors `#about #invention #leadership #mentoring #standing #recognitions #publications #education` that Task 7 fills and Task 10's redirect targets use. `nav_home()` emits anchor links; the existing `nav()` stays for detail pages.

- [ ] **Step 1: Back up build.py**

```bash
cp build.py /tmp/build.py.pre-rebuild
```

- [ ] **Step 2: Update SITE, BASE and FOOTER, add nav_home()**

SITE gains: `"photo_w": <from Task 3>`, `"photo_h": <from Task 3>`, `"updated": "26 September 2026"`. BASE gains two lines in the head:

```html
<meta property="og:image" content="https://oversightengineering.com/assets/img/profile.jpg">
<meta property="og:image:alt" content="Pravin Khandke, headshot">
```

FOOTER links change from `/memberships/ /publications/ /peer-review/ /talks/` to `/#recognitions /#publications /#standing /#about`. The footer's "BCS fellowship application" phrase becomes "fellowship application".

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

Hero: photo right (circular, width and height attributes from SITE so space is reserved), kicker "Fellowship evidence record", name with surname in accent, tagline row, three badge chips (IEEE Senior Member, RSS Fellow, SEFM Eminent Fellow), four counters each carrying a `data-counter` attribute (`years` = 26, `venues` = filled by Task 11 from `len(VENUE_ROWS)`, `committees` = 4, `publications` = 2), connect row of exactly ORCID, LinkedIn, email (no Scholar, per the register ruling). About: the existing three-sentence bio paragraph from the current about aside, kept verbatim, under `#about`. Meta description becomes "Public record of the work, recognition and professional service cited in Pravin Khandke's fellowship application."

- [ ] **Step 4: Build and smoke-test**

```bash
python3 build.py && python3 - <<'EOF'
import pathlib
t = pathlib.Path("docs/index.html").read_text()
assert "assets/img/profile.jpg" in t, "photo missing"
assert 'id="about"' in t, "about anchor missing"
assert "og:image" in t, "og:image missing"
assert "BCS" not in t, "body name leaked"
assert "scholar.google" not in t, "scholar link leaked"
print("smoke ok")
EOF
```

Expected: `smoke ok`.

---

### Task 7: build.py home page, body (invention, leadership, mentoring, standing)

**Files:**
- Modify: `build.py` — continue the index.html body after the about section

**Interfaces:**
- Consumes: anchors from Task 6, `.work-card`, `.tag-row`, `claim()` and `ext()` helpers
- Produces: full-record links to `/invention/`, `/consultancy/`, `/mentoring/`, `/standing/`; the standing section structure Task 11 fills with linked venue rows

- [ ] **Step 1: Write the four sections**

Each section: `section-rule` heading, two or three `.work-card` blocks with the tag row, one claim-style source line, and a full-record link. Copy is trimmed from the existing detail pages, three sentences per card maximum:

- `#invention` — card 1: the remittance reconciliation pipeline (human oversight at the centre, matches below threshold stop for a person, every validation logged for audit). Card 2: the ActiveMQ Artemis event-driven retail backbone. Source lines link IJCA and `https://iccbi.com/`.
- `#leadership` — card 1: the Cox Automotive platform retirement, service by service, no downtime window. Card 2: the canonical data model adopted as the client's standing integration standard. Card 3: the financial services reconciliation and engagement lifecycle work. Full-record link to `/consultancy/`.
- `#mentoring` — card 1: engineers developed inside the teams. Card 2: the sponsored university capstone. Card 3: the children's AI safety open standard, linking `https://github.com/pravin-khandke/safe-ai-for-kids`. Full-record link to `/mentoring/`.
- `#standing` — sub-headed rows, not tabs: Speaking, Committees, Peer review, Writing, Judging. Full-record link to `/standing/`. Speaking rows: AIC 2026 keynote linking `https://scrs.in/conference/aic2026`, Extract Summit linking `https://www.extractsummit.io/speakers`, ICCBI linking `https://iccbi.com/`. The AIC row is labelled "Keynote, AIC 2026, Jabalpur" and claims nothing about an organiser speaker list, because the register records that the list page is not held. Writing rows carry the five dev.to, hashnode and medium URLs from the pinned resume. Judging: Georgia Tech and Kennesaw State.

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
EOF
```

---

### Task 8: build.py home page, tail (recognitions, publications, education)

**Files:**
- Modify: `build.py` — continue the index.html body, then the 404 page links

**Interfaces:**
- Consumes: `.verify-row`, `.pub-row`, `.edu-table` classes, `.verify-grid`; form dates from `evidence/form-extract.txt` (Task 4)
- Produces: the education table carrying form-aligned dates; 404 links updated to anchors

- [ ] **Step 1: Recognitions section**

`#recognitions`: a `.verify-row` per recognition, register links only, no scans:

- IEEE Senior Member, elevated June 2026, member 102303821
- Eminent Fellow Member (SEFM), conferred June 2026, linking `https://www.sassociety.com/membership-id-sas-sefm-770-2026/`
- RSS Fellow, July 2026, membership 263939
- AIC 2026 keynote, Jabalpur, linking `https://scrs.in/conference/aic2026` (no speaker-list claim)

Source note under the grid: "Recognition is verified against the awarding body's own register rather than a scanned certificate."

- [ ] **Step 2: Publications section**

`#publications`: one `.pub-row` each for the two papers (IJCA article, ICCBI 2026 paper linking `https://iccbi.com/`) and the five technical articles with their dev.to, hashnode and medium URLs from the pinned resume.

- [ ] **Step 3: Education section with form-aligned dates**

`#education`: `.edu-table` with the four degrees from the pinned resume, and a four-role work history table. Where the dates in `evidence/form-extract.txt` agree with the resume, publish them. Where they disagree, the form wins, the table flips, and the flip is recorded in `evidence/EVIDENCE-CHECKLIST.md`. If the form extract holds no explicit dates for a role, publish the resume dates and add the conflict to the checklist as an open item. A source note names the form or the resume, whichever was used per role.

- [ ] **Step 4: Update the 404 page**

404 links change from `/publications/` and `/peer-review/` to `/#publications` and `/#standing`.

- [ ] **Step 5: Build and full-page browse check**

```bash
python3 build.py
B="$HOME/.claude/skills/gstack/browse/dist/browse"
$B goto file://$PWD/docs/index.html
$B viewport 375x812 && $B screenshot /tmp/home-375.png
$B viewport 1280x900 && $B screenshot /tmp/home-1280.png
$B js "document.documentElement.scrollWidth <= 375"
```

Read both screenshots, fix what looks wrong, repeat. No horizontal scroll, photo crops cleanly, counters aligned.

---

### Task 9: Commit the rebuilt home site

**Files:**
- All of Tasks 3, 5, 6, 7, 8 land in this one commit so nothing publishes half-styled.

- [ ] **Step 1: Full verification of the built tree**

```bash
python3 build.py
python3 probe_links.py
grep -riwE "bcs|iet" docs/ | grep -v "docs/bcs/" | grep -v "docs/iet/" && echo "LEAK" || echo "clean"
```

Expected: probe exits 0, string check prints clean (the redirect stubs are prose-free and exempt).

- [ ] **Step 2: Screenshots to the user**

Show `/tmp/home-375.png` and `/tmp/home-1280.png` with the Read tool before committing.

- [ ] **Step 3: Commit**

```bash
git add build.py probe_links.py docs/
git commit -m "redesign: single-page evidence record with photo, counters and linked venues"
```

---

### Task 10: Folded pages become redirect stubs

**Files:**
- Modify: `build.py` — REDIRECTS list; delete the `add()` calls for memberships, publications, talks, peer-review; update README.md and DEPLOY.md

**Interfaces:**
- Consumes: home anchors from Task 6
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

Delete the four `add()` calls and their page content from build.py. The `/bcs/*` and `/iet/` stubs stay: the four `http://oversightengineering.com/bcs/...` URLs written in the submitted form (exact strings pinned in Task 4) keep working, and the form is not edited.

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

README layout section: the evidence/ tree with a "gitignored, private" note (not a contents listing), the new page set, `probe_links.py`, the specs/ and plans/ folders, and the hand-maintained exceptions (`docs/assets/css/site.css`, `docs/assets/img/`). DEPLOY.md: unchanged pipeline, note the HTTPS action item and the probe re-run at filing time.

- [ ] **Step 4: Verify and commit**

```bash
python3 build.py && grep -riwE "bcs|iet" docs/ | grep -v "docs/bcs/" | grep -v "docs/iet/" ; echo "check done"
git add build.py README.md DEPLOY.md docs/
git commit -m "refactor: fold memberships, publications, talks and peer-review into home stubs"
```

---

### Task 11: Every venue linked, counters reconciled

**Files:**
- Modify: `build.py` — the standing section's committees and peer-review rows; the venues counter

**Interfaces:**
- Consumes: the pinned resume `~/Documents/BCS/BCS_Final/Resume-Pravin-Khandke.md`, the audit verdicts in `evidence/EVIDENCE-CHECKLIST.md`, the probe script from Task 2
- Produces: `VENUE_ROWS` and `COMMITTEE_ROWS` lists in build.py; the venues counter equals the review-row count, asserted in the smoke test

- [ ] **Step 1: Encode the per-venue table in build.py**

```python
# name, url (None = no link, reason stated in the row), role
VENUE_ROWS = [
    ("IECON 2026", "https://www.iecon2026.org/"),
    ("IEEE GLOBECOM 2026", "https://globecom2026.ieee-globecom.org/"),
    ("ICCUBEA 2026", "https://iccubea.pccoepune.com/iccubea.php"),
    ("ICETCI 2026", "http://www.ietcint.com/"),
    ("ICDCECE 2026", "https://icdcece.in/"),
    ("AMLDS 2026", "https://amlds.site/"),
    ("NGSME 2026", "https://sites.google.com/view/ngmse2026/home"),
    ("CAISAIS 2026", "https://caisais26.ajman.ac.ae"),
    ("AIIoT 2026", "https://worldaiiotcongress.org/technical-committee/"),
    ("CEECT 2026", "https://www.ceect.org/"),
    ("MeditCom 2026", "https://meditcom2026.ieee-meditcom.org/"),
    ("ICoIAS 2026", "https://www.icias.org/index.html"),
    ("iSemantic 2026", "https://isemantic.dinus.ac.id/2026/"),
    ("INCOSST 2026", "https://incosst.polteksci.ac.id/"),
    ("INTCEC 2026", "https://intcec.org/"),
    ("ICTMOD 2026", "https://ictmod-conference.com/"),
    ("ETECOM 2026", "https://ieee-etecom.org/"),
    ("SIME 2026", "https://sime-conf.org/committees/"),
    ("ICETM 2026", None),        # venue site returns 404
    ("CICBA 2026", None),        # venue domain no longer resolves
    ("TEMSMET 2026", None),      # no public listing in any record
    ("ARIIA 2026", None),
    ("ICNSBT 2026", None),
    ("CICA 2026", None),
    ("ICAITech 2026", None),
    ("PlatCon 2026", None),
]
COMMITTEE_ROWS = [
    ("NGSME 2026 Workshop", "https://sites.google.com/view/ngmse2026/home"),
    ("AIIoT 2026", "https://worldaiiotcongress.org/technical-committee/"),
    ("SIME 2026", "https://sime-conf.org/committees/"),
    ("BDAA 2026", "https://bdaa-conference.com/"),
]
```

Rows without a URL carry the reason as plain text: "no public listing" or "venue site offline". Under the peer-review list the page states: "26 review venues plus four committee appointments." Under the list: "Links verified on <date from probe_links.py output>. Eight venues have no live listing to link."

- [ ] **Step 2: Re-run the probe, stamp the date**

Run: `python3 probe_links.py`, take the Verified-on date, put it in the source note. Fix or annotate anything that fails.

- [ ] **Step 3: Assert the counters agree with the rows**

```bash
python3 build.py && python3 - <<'EOF'
import pathlib, re
t = pathlib.Path("docs/index.html").read_text()
review_rows = len(re.findall(r'class="venue-row"', t))
n = re.search(r'data-counter="venues">(\d+)', t)
assert n and int(n.group(1)) == review_rows, f"counter {n and n.group(1)} != rows {review_rows}"
c = re.search(r'data-counter="committees">(\d+)', t)
assert c and int(c.group(1)) == len(re.findall(r'class="committee-row"', t)), "committee counter mismatch"
assert "73" not in re.sub(r'<[^>]+>', '', t), "contested review count leaked"
print(f"venues counter == {review_rows} review rows, committees == {c.group(1)}")
EOF
```

(If the row markup differs, adjust the two selectors together, never one alone.)

- [ ] **Step 4: Commit**

```bash
git add build.py docs/
git commit -m "feat: link every venue, reconcile the counters with the rows"
```

---

### Task 12: The evidence copy

**Files:**
- Create: `evidence/eb1a_evidence/` (full tree), `evidence/reviews/` (Drive Peerreview files), `evidence/EVIDENCE-CHECKLIST.md` (mapping and gap log appended)

**Interfaces:**
- Consumes: `~/Documents/EB1A/EB1A_Evidence` (complete copy per the user's instruction of 26 September, which amends the spec's original selective-copy wording), the Google Drive Peerreview folder (path located in step 1)
- Produces: a complete local evidence tree with originals untouched, a mapping table and gap log in the checklist

- [ ] **Step 1: Locate the Drive Peerreview folder**

```bash
find "/Users/pravinkhandke/Library/CloudStorage/GoogleDrive-pravin.khandke@ieee.org/My Drive" \
  -maxdepth 3 \( -iname "*peerreview*" -o -iname "*peer review*" \) 2>/dev/null
```

Note the exact path; if absent, search one level deeper or by the review-file names already known (IECON, iSemantic confirmations). Record the path in the checklist.

- [ ] **Step 2: Full copy, originals untouched**

```bash
rsync -a "$HOME/Documents/EB1A/EB1A_Evidence/" \
      "$HOME/Documents/GitHub/oversightengineering/evidence/eb1a_evidence/"
du -sh evidence/eb1a_evidence
find evidence/eb1a_evidence -type f | wc -l
```

The per-item source-and-destination log the register asks for is recorded at folder granularity (the mapping table in step 4) rather than per file, because this is a complete-tree copy.

- [ ] **Step 3: Copy the review files**

```bash
rsync -a "<drive peerreview path>/" \
      "$HOME/Documents/GitHub/oversightengineering/evidence/reviews/"
find evidence/reviews -type f | wc -l
```

Expected count: roughly the 73 files the register counts (36 confirmations, 27 review documents, 9 screenshots), plus whatever the Drive folder holds beyond them.

- [ ] **Step 4: Verify nothing from evidence/ is tracked, then append the mapping and gap log**

```bash
git status --porcelain | grep evidence ; echo "exit $?"
git check-ignore evidence
```

Expect: the grep finds nothing (exit 1), check-ignore hits. Then append to `evidence/EVIDENCE-CHECKLIST.md`: the table mapping each EB1A source folder (`00_Profile_Snapshot`, `01_Authorship_Scholarly_Articles`, `02_Original_Contributions`, `03_Judging_Activities`, `03_Published_Material`, `04_Memberships_Awards`, `05_Awards`, `05_Leading_or_Critical_Role`, `06_Media_Coverage`, `07_High_Remuneration`, `08_Speaking_Engagements`, `09_Other_Supporting`, `10_Recommendation_Letters`, `11_Petition_Assembly`, `12_RFE_Response`, `Research_Papers`) to the criteria or certificate/review/profile folder it feeds, and the gap log: SIME, TEMSMET, ARIIA, ICNSBT have no evidence folder, CICA and ICTMOD have empty ones.

- [ ] **Step 5: No commit** — `evidence/` is untracked by design. `git status` stays clean apart from intended changes.

---

### Task 13: The checklist refresh

**Files:**
- Modify: `evidence/EVIDENCE-CHECKLIST.md`, `evidence/EVIDENCE-TODO.md`

**Interfaces:**
- Consumes: `evidence/form-extract.txt` (Task 4), the pinned resume, the Task 12 copy
- Produces: the reconciled register and the actionable missing-items list

- [ ] **Step 1: Reconcile the register against the form extract**

Update the checklist's per-claim table from the already-extracted form text: mark closed what Tasks 1 to 12 closed (venue links, stubs, photo, unindexed confirmations), recompute the open counts, and resolve the site-versus-resume date conflicts using the form as source of truth, recording any flip Task 8 made.

- [ ] **Step 2: Refresh the TODO**

Each open item keeps the `[site]`/`[file]` marker and the Me/You owner, gains a one-line what-and-where, and the list is ordered by what unlocks the most. Add the user action items:

- HTTPS: certificate is null and enforcement is off twelve days after cutover. Re-save the custom domain under Settings, Pages, or open a GitHub support thread. Until fixed, assessors land on Not secure.
- The review-definition decision (66 strict versus 73 loose) before any review count is published anywhere.
- A Web of Science Researcher Profile.
- The supporter confirmation for the consultancy claims.

- [ ] **Step 3: Verify the counts**

Every count stated in either file must be recomputed from `find evidence -type f` and the probe output, not carried over. State the computation next to each count.

- [ ] **Step 4: No commit** — both files are untracked. Show the user the new TODO top section.

---

### Task 14: Final verification pass

- [ ] **Step 1: Build and probe**

```bash
python3 build.py && python3 probe_links.py
```

- [ ] **Step 2: docs/ contents check**

`find docs -type f | sort` — every file is one the generator wrote, plus `CNAME`, `.nojekyll`, `robots.txt`, `assets/img/profile.jpg`, and the hand-maintained `assets/css/site.css`. Nothing else.

- [ ] **Step 3: Form URL check**

For each of the four `http://oversightengineering.com/bcs/...` URLs pinned in Task 4: `curl -sI` returns 200 and the page carries a meta refresh. Also `curl -sI https://oversightengineering.com/` — if HTTPS still fails, the checklist action item stays open and says so.

- [ ] **Step 4: String check**

`grep -riwE "bcs|iet" docs/ | grep -v "docs/bcs/" | grep -v "docs/iet/"` — expect no hits.

- [ ] **Step 5: Browse pass**

Home and all four detail pages at 375px and 1280px: screenshots read, no horizontal scroll. Print check: `$B pdf /tmp/print-check.pdf --print-background` renders every venue link as a URL.

- [ ] **Step 6: Commit anything remaining, report status to the user with the screenshots and the new TODO top section**