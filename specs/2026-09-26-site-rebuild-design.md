# Site rebuild and evidence system, oversightengineering.com

Date: 26 September 2026
Status: approved in conversation with a 19-point review incorporated
Inputs: brainstorming session 26 September 2026, reference sites
bala-kumaran.com, balajithadagamkandavel.com, seshakiran.netlify.app
(vocabulary only, not cloned), Resume-Pravin-Khandke.md,
bcs-fellow-application-form-pravin-khandke.docx, EB1A_Evidence folder,
EVIDENCE-CHECKLIST.md register rulings.

## Purpose

oversightengineering.com is the public record of the work cited in Pravin
Khandke's fellowship applications. Today it is eight text-dense pages with
almost no links and no photo. The rebuild makes it scannable, links every
venue, shows the person, and adds a private evidence store plus an
actionable checklist. The reference sites were shown by the user as
examples; the judgement call is what a professional evidence record needs,
and nothing more.

## Decisions fixed by the user

1. Visual direction C, clean portfolio. Bright, airy, minimal, large photo.
2. Photo source (see Photo handling).
3. An evidence folder at repo root, never published.
4. Do not copy the reference sites wholesale. Take the professional
   pattern, drop the clutter.
5. Every conference on the site gets a link where a live URL exists.
6. Thumbnails: no scanned certificates on the site. This supersedes the
   thumbnail request from the brainstorming session. See Recognitions.
7. No awarding body's name in any folder or file name, and no fellowship
   strategy in the public repo.

## Decisions taken from the review (recorded here as made)

1. `.gitignore` is created in the first commit of the rebuild, before any
   evidence lands, ignoring `evidence/`, `.bak-*`, `.DS_Store`,
   `.superpowers/`, `.gstack/`. The checklist stops instructing
   `git add -A`. The two stray `.bak` files currently in the tree are
   removed once ignored copies exist. User memory still requires a backup
   before patching, so backups live outside the repo (`/tmp` or a sibling
   folder), not in the tree.
2. `EVIDENCE-CHECKLIST.md` and `EVIDENCE-TODO.md` move under `evidence/`
   and become untracked. They contain fellowship strategy and withheld-item
   rulings, which contradict a public repo. `README.md` points to their new
   location without copying content into a public page.
3. Scanned certificates stay withheld. The register ruling stands: the
   awarding body's own register is the better source, and a document dump
   is not wanted. Recognitions therefore publishes register and organiser
   links only, no scans, no certificate PDFs, no thumbnails of certificate
   documents. What the user asked for as thumbnails becomes a linked
   verification grid: one row per recognition, each row linking to the
   body's register or the organiser's own listing of Pravin.
4. Hero counters show only uncontested figures: 26 years, the number of
   venue rows actually listed on the site, 4 committees, 2 publications.
   The review count stays unshown, matching the standing decision on
   `/peer-review/`, until the review-definition decision in the evidence
   register is made. When it is made, one counter is added with the chosen
   figure and its definition stated in the source line.
5. Venue links use a per-venue table with a fallback rule and a stamped
   check date. The resume carries URLs for 20 of the venues. Eight have
   none: TEMSMET, ARIIA, ICNSBT, CICA, ICAITech, PlatCon (no URL in any
   record) and ICETM (404), CICBA (domain gone). Those eight are named
   without a link. Committee venues link to the committee page where one
   is held and verified, else the venue homepage, else no link. A
   link-probe script is committed to the repo so the check can be re-run
   at filing time, and the venue list carries a "verified on" date.
6. Work-history dates take the BCS form as source of truth once reconciled.
   Where the form disagrees with the resume or LinkedIn, the checklist
   records the conflict and the site waits for the resolution. The site's
   consultancy claims additionally rest on a supporter confirmation not yet
   in hand, which the checklist flags as a precondition.
7. The site stays unindexed: robots.txt Disallow and the noindex meta tag
   remain. Public by URL, not advertised to search engines.
8. The four `http://oversightengineering.com/bcs/...` URLs written in the
   submitted form keep working. `docs/bcs/` stays as meta-refresh stubs,
   each redirecting to the corresponding new generic page. The four pages
   the rebuild folds (memberships, publications, talks, peer-review) get
   the same treatment, stubs redirecting to their home sections, because
   saved links and the register both point at them.
9. The form's URLs stay as submitted and are not rewritten to https. The
   exact strings are pinned in the implementation plan. The `/iet/` stub
   keeps pointing home, since that address was once published. HTTPS itself
   is broken (certificate null, enforcement off) and is a user action item,
   recorded in the checklist: re-save the custom domain under Settings,
   Pages, or open a support thread. Assessors currently land on Not secure.
10. Review evidence comes from two sources: the Google Drive Peerreview
    folder (canonical for the 73 files) and `~/Documents/EB1A/EB1A_Evidence`
    for everything else. The exact Drive path is resolved during
    implementation and pinned in the checklist.
11. The evidence scan logs gaps rather than skipping silently: the six
    venues with no evidence folder and the two with empty folders appear in
    the checklist as missing items. A mapping table from the EB1A folder
    names to the new criteria folders is part of the scan output.
12. The no-body-name rule gets a literal-string check across `docs/` in the
    verification pass, covering the meta descriptions, straplines and intro
    that carry it today.
13. No tabs anywhere. Tabs hide links from print and need scripting the
    site deliberately avoids. The influencer section uses sub-headings and
    cards, which print expands naturally.
14. Home sections map onto detail pages completely: invention to
    `/invention/`, leadership and consulting to `/consultancy/`, mentoring
    to `/mentoring/`, community standing to `/standing/`.
15. Photo handling strips EXIF, records final width and height, and the
    hero reserves space so layout does not shift.
16. The verification pass adds: a contents check that only intended files
    sit in `docs/`, a resolve check for the four form URLs with scheme and
    trailing slash, and a re-check cadence tied to the committed probe
    script.
17. Input paths are pinned: the resume lives at
    `~/Documents/BCS/BCS_Final/Resume-Pravin-Khandke.md` (canonical; the
    copy at `~/Documents/EB1A/EB1A_Evidence/00_Profile_Snapshot/CV/` is
    truncated and stale). The form lives at
    `~/Documents/BCS/BCS_Final/bcs-fellow-application-form-pravin-khandke.docx`.
18. `README.md` and `DEPLOY.md` are updated to describe the new structure.

## Scope of the no-body-name rule and repo visibility

The rule scopes to everything published (`docs/`) and to folder names
everywhere. `specs/` and `plans/` are tracked working documents and may name
the bodies. Git history retains the registers' earlier tracked versions
under their old names; that is accepted, because assessors are pointed at
the site, never at the repository. The connect row carries ORCID, LinkedIn
and email. Google Scholar stays off the site, per the register's withheld
ruling that an empty profile invites the wrong comparison.

## Site architecture

Single scrolling home page as the browsable front, generated by `build.py`.
The four criterion detail pages remain, trimmed, each linked from its home
section with a full-record link.

Home page sections, in order:

| Anchor | Links to | Content |
|---|---|---|
| hero | | Photo, name, tagline row, badge chips, counters, connect row |
| about | | Three paragraphs maximum, retail to automotive to financial arc |
| invention | /invention/ | Two cards: remittance reconciliation, event-driven retail backbone |
| leadership | /consultancy/ | Three cards: Cox retirement, canonical data model, financial services integration |
| mentoring | /mentoring/ | Three cards: engineers developed, sponsored capstone, children's AI standard |
| standing | /standing/ | Sub-headed rows: Speaking, TPC, Peer review, Writing, Judging |
| recognitions | | Verification grid, register links, no scans |
| publications | | Rows: two papers, five articles, one line each with link |
| education | | Compact degree list, four-role work history table |

`build.py` stays the single generator. Navigation is generated. The print
stylesheet for assessors is kept and updated, and it expands every section
by construction because nothing is hidden behind interaction.

## Visual design

- Palette: near-white background, ink text, one deep blue accent. Evidence,
  not marketing.
- Type: the existing Archivo and Spectral pairing, fewer weights, not a
  family swap.
- Hero: circular photo, name set large with the surname in the accent
  colour, bordered badge chips, right-aligned counters. The counters are
  fixed as 26 years, the venue count the page itself totals, 4 committees,
  and 2 publications. No review counter appears until the review-definition
  decision in the evidence register is made.
- Sections: heading with rule line, cards with a tag row, lists as rows.
- Responsive at phone width, no horizontal scroll, 16px gutter minimum.
- Print stylesheet kept.

## Content rules

Unchanged from the README: zero em dashes and en dashes, zero semicolons,
no inline comma list of three or more, no conclusory adjectives, every
checkable claim carries a source line. No paragraph on the home page longer
than three sentences. Detail pages keep their claims but lose preamble.

## Conference links

Built from the pinned resume plus the 13 September audit, per-venue table
with fallback rule and check date as decided above. The probe script is
committed and re-runnable; the page stamps the check date.

## Photo handling

Source: `~/Library/CloudStorage/GoogleDrive-pravin.khandke@ieee.org/My
Drive/Pravin-Photo-website.jpeg` (76,614 bytes at time of writing). Copy to
`docs/assets/img/profile.jpg`, strip EXIF, keep it small, record final
dimensions. Circular crop in hero, rectangular in About, alt text "Pravin
Khandke, headshot", absolute path so it resolves on every page.

## Evidence system

`evidence/` at repo root, gitignored in the first rebuild commit, never
published. Structure:

    evidence/
      README.md                 what this folder is, what goes where
      criteria/
        01-invention-and-innovation/
        02-consultancy/
        03-mentoring-and-coaching/
        04-community-standing/
      certificates/             membership and role certificates
      reviews/                  confirmations and review documents
      profile/                  photo, identity documents
      EVIDENCE-CHECKLIST.md     moved here from the repo root
      EVIDENCE-TODO.md          moved here from the repo root

The evidence scan copies the complete `~/Documents/EB1A/EB1A_Evidence` tree
into `evidence/`, preserving its internal folder names, alongside the
criterion folders used by the application files. Review evidence additionally
comes from the Google Drive Peerreview folder, the canonical home of the 73
review files. The scan maps the EB1A folder names to the criteria folders,
logs the gaps (the six venues with no evidence folder, the two with empty
ones), records every copy with source and destination, and never moves
originals. The checklist refresh reconciles against the pinned form and
resume, folds in the register's open items, marks what the rebuild closes,
adds the user action items (HTTPS re-provisioning, the review-definition
decision), and produces the missing-items list tagged site, file, or who
produces it.

## Error handling and verification

`python3 build.py` must pass with no hand edits in `docs/`. Before commit:

1. Home page and four detail pages browsed at 375px and 1280px, no
   horizontal scroll.
2. Every external link probed by the committed script, target 200 or a
   named exception, date stamped on the page.
3. Every image present with alt text.
4. Print stylesheet renders the home page legibly, links visible.
5. Only intended files sit in `docs/`, and no awarding body's name appears
   in any published file, checked by literal-string search.
6. The four form URLs resolve with their scheme and trailing slash.
7. Screenshots to the user before anything is committed.

## Out of scope

- Writing the fellowship application itself
- Producing the missing reviews or any new evidence
- Publishing review confirmations, employer documents or certificate scans
- Fixing the HTTPS certificate, which is a registrar or Pages settings
  action recorded as a user action item
- Any change to `docs/CNAME` or DNS