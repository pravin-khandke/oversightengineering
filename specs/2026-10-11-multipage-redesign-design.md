# Multi-page redesign with theme C and images

Date: 11 October 2026
Status: draft for review
Supersedes: the single-page structure in `2026-09-26-site-rebuild-design.md`

## Intent

The site is a public evidence record read by fellowship assessors. The owner finds the
current single scrolling page boring and wants it to read well, with images, as a real
multi-page site. The readers and the constraints stay the same. Only the look and the
structure change.

What the owner said:
- The page is boring and should be more interesting to read.
- Add a few images.
- It should not be a one-page application.
- Change the theme.

Decisions made in brainstorming:
- Audience: assessors, with a warmer look.
- Images: a mix of real photos and generated diagrams.
- Theme: C, bright and airy (white background, deep green accent, photo banner, image cards).
- Structure: topic pages.
- Build: keep `build.py`, rewrite templates and CSS.

## Constraints that still bind

- Every page carries the noindex robots meta tag. `robots.txt` disallows all.
- No awarding body name anywhere under `docs/` or in folder names, except inside the
  redirect stub directories `docs/bcs/` and `docs/iet/`.
- The `/bcs/*` and `/iet` URLs keep resolving, because the submitted form carries them.
- Writing rules: no em dashes, no en dashes, no semicolons, no inline comma list of three
  or more items, no conclusory or promotional adjectives. Every checkable claim carries a
  source line.
- Counters stay exactly 26 years, 26 venues, 4 committees, 2 publications. No review count.
- Connect row is ORCID, LinkedIn and email only.
- No scanned certificates. Recognition links to public registers.
- `evidence/` is never tracked and never published.
- No personal or commercial data in public images. Photos are checked for minors and private
  details before publishing, and EXIF data is stripped.

## Site map

Top navigation has seven items (six when `ARTICLES` is empty). The brand name links home.

| Nav item | URL | Contents |
|---|---|---|
| Home | `/` | Photo banner, grade chips, four counters, card grid with one image card per topic page |
| Work | `/invention/` and `/consultancy/` | Existing pages, restyled. Each links to its sibling. |
| Mentoring | `/mentoring/` | Mentoring and coaching record, with photos |
| Community | `/standing/` and `/memberships/` | Standing in the community and memberships |
| Papers and talks | `/publications/` and `/talks/` | Two restored pages |
| Peer review | `/peer-review/` | Restored page with 26 linked venues and 4 committees |

A seventh item, Writing at `/writing/`, is driven by an `ARTICLES` list in `build.py`. The
nav item, the page, the home card and the related links are generated only when the list has
at least one entry with a public URL. The list is seeded with the five articles the home page
already links on Dev.to, Hashnode and Medium, so the tab is live. Each entry renders as a card
with a platform tile, title and a "Read on <platform>" link. The Authority Magazine interview
sits on the same page under a Coverage heading. No entry is invented.

Redirect stubs `docs/bcs/*` and `docs/iet/` stay unchanged. The four `REDIRECTS` entries for
memberships, publications, talks and peer-review are removed so the real pages are served.

The home page stops being the long scrolling record. Its sections move onto the topic pages.
Counters and claims on topic pages must agree with the home page.

## Page patterns

Borrowed from rahvis.github.io, bala-kumaran.com and balajithadagamkandavel.com after
reviewing every tab of each. Adapted to the constraints above.

- Home hero: two buttons next to the grade chips. "Read the record" and "Peer review".
- Home Highlights: a reverse-chronological list of 5 to 8 dated items under the counters.
  Each item is one sentence with a source link. The owner confirms the items. Stored as a
  `HIGHLIGHTS` list in `build.py`.
- Work pages: case-study blocks with a date range, one tag line, bullets, tag chips, a
  source link and a captioned diagram. A case study carries a date range only where a source
  states one, and in this build only the retirement case study has one. A metric badge appears only when its source line
  exists. No metric is shown without a stated basis.
- Papers and talks: talks are cards with an optional photo, event name, talk title and a link
  button, grouped by type (Keynote, Conference sessions) because the sources give dates
  without a year for one event. Publications list the two peer-reviewed papers with the title
  in bold, the venue in italics, the year where known and a source link. Technical articles
  move to the Writing page so nothing is listed twice.
- Mentoring: stacked sections, one per program, each with a photo and a short claim.
  Numbers appear only with a source line.
- Peer review and Community: text badges such as "Technical Program Committee" beside the
  linked rows.
- Recognitions: image cards using event photos, logos and links to public registers. No
  scanned certificates.
- Image hygiene: one file per image and unique descriptive alt text on each. No reused
  files and no copied labels.
- Contact: ORCID, LinkedIn and email only. No phone number.

## Visual system

- Colors: white background, deep green accent near `#2f6b4f`, pale green tints for cards and
  chips, dark green-black text. Contrast meets WCAG AA.
- Type: sans for navigation and headings (Archivo), serif for body text (Spectral). Both stay
  on Google Fonts as today.
- Layout: full-width banner on every page (tall on home, short on topic pages). Card grid of
  three columns, one column on phones. Reading column of about 70 characters. Topic pages
  have a right sidebar with "On this page" and "Related" that collapses below the content on
  phones.
- Components: page layout (nav, banner, footer), card, claim block with source line, figure
  with caption and alt text.
- Print: the print stylesheet that reveals link addresses is kept.

The approved mockup is saved at
`.superpowers/brainstorm/28010-1791749033/content/theme-c-pages.html` (local only).

## Images

- Real photos: the existing `profile.jpg` on home. Owner-supplied photos of talks, mentoring
  and community events on the matching pages. Placed by the owner or sent to the assistant.
- Diagrams: generated architecture and timeline graphics for Work and the home banner. No
  people.
- Until photos arrive, home cards render a green gradient tile in the image slot. Body
  figures and talk thumbnails render nothing when their file is missing, so no page shows an
  empty box or a broken image. A photo appears once its file is in `docs/assets/img/` and its
  alt text and caption are in the `IMAGES` table in `build.py`.
- Diagrams are hand-written SVG files in `docs/assets/img/`, drawn only from facts already on
  the site. They carry no figures that are not already sourced.
- The banner is a CSS gradient on every page. Only the home banner carries a photo.
- Files live in `docs/assets/img/`, are referenced as `/assets/img/name.ext`, carry
  descriptive alt text, are compressed to roughly 200 KB or less, and use `loading="lazy"`
  below the fold.

## Build changes

All inside `build.py` and `docs/assets/css/site.css`.

1. Add shared layout, card, claim and figure helpers. Keep `claim()` and `ext()`.
2. Move home page sections onto their topic pages.
3. Restore the memberships, publications, talks and peer-review `add(...)` calls from git
   history (`git show 45dfc89:build.py`). Strip any awarding body names. Replace the
   peer-review page's unlinked venue list with `venue_rows_html()` and
   `committee_rows_html()`.
4. Replace `nav_home()` and `nav()` with one nav built from a single group table that marks
   the current page, adds a sub-tab strip inside the Work, Community and Papers and talks
   groups, and adds the Writing item when `ARTICLES` has entries.
5. Add `tests/test_site.py`, run with `python3 -m unittest discover -s tests`. It builds the
   site and checks the verification rules below, so each rule is enforced rather than
   remembered. `build.py` reads `SITE_OUT` so a test can build to a temporary folder.
6. Rewrite `site.css` for theme C, including responsive and print rules.
7. Update `README.md` layout and editing sections to match.

## Verification

Run before anything is pushed:

- `python3 build.py` completes without error.
- `python3 probe_links.py` reports 0 failing links.
- `grep -riwE "bcs|iet" docs/ | grep -v "docs/bcs/" | grep -v "docs/iet/"` returns nothing.
- A scan of `docs/` for em dashes, en dashes and semicolons in prose returns nothing.
- Every page has the noindex meta tag. All four counters match across home and topic pages.
- Browser check of every page at 375px and 1280px: no horizontal overflow, nav usable, print
  view readable.
- The `/bcs/*` and `/iet` redirects still resolve.

## Rollout

Work on a branch with small commits. Nothing is pushed until the owner has reviewed the local
build and approved. The site is live on GitHub Pages, so pushing is the owner's call. Photos
may arrive after the first push, and the gradient slots cover the gap.

## Out of scope

- Copying evidence into `evidence/`.
- The HTTPS certificate issue.
- Private checklist and TODO work from the 26 September handoff.
- Any change to claims or counters.

## Open items

- The owner confirms the Highlights items and their source links. They are seeded from facts
  already on the site (IEEE Senior Member, SEFM, RSS Fellow, the AIC 2026 keynote and the
  Extract Summit session).
- The owner confirms the Writing page should show the five existing articles. The earlier
  answer about publishing on X was ambiguous.
- Two home sections have no home of their own and move as follows: Recognitions folds into
  Highlights and the Memberships page, and Education and work history stay on the home page
  under a short Background section.
- The owner supplies the photos. Which events and which pages get a photo is decided when the
  photos arrive.
