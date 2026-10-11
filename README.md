# oversightengineering.com

Source for `https://oversightengineering.com`, the public record of the work cited in
Pravin Khandke's fellowship application.

## Layout

    build.py                  site generator. Page content lives here, one add(...) per page
    probe_links.py            probes every external link in docs/, prints a Verified-on date
    docs/                     PUBLISHED. GitHub Pages serves this folder and nothing else
      index.html              home: banner, counters, highlights, topic cards, background
      invention/, consultancy/
                              work pages, with case-study blocks and a diagram each
      mentoring/              mentoring and coaching, with case-study blocks
      inspiring/              inspiring others: coaching, writing, speaking, mentoring
      career/                 roles and skills
      standing/, memberships/ standing in the community and the grades held
      publications/, talks/   the three peer-reviewed papers, and the talks given
      peer-review/            28 venues and 3 committees, each linked where a listing exists
      writing/                technical articles. Built only while ARTICLES in build.py has entries
      bcs/                    redirect stubs. The submitted form carries /bcs/ URLs, so
                              they keep resolving
      iet/                    redirect stub to home, for a once-published address
      assets/css/site.css     styles, hand-maintained, including dark and print rules
      assets/img/             images, hand-maintained. profile.jpg is the hero photo
      CNAME                   the custom domain
      .nojekyll               stop GitHub Pages running Jekyll
    tests/test_site.py        builds the site and checks the structural and content rules (navigation, links, images, counters, dashes, awarding-body names, noindex)
    specs/                    design specs, tracked working documents
    plans/                    implementation plans, tracked working documents
    evidence/                 PRIVATE, gitignored, never published. See evidence/README.md

## Build

    python3 build.py
    python3 -m unittest discover -s tests -v    run the site checks

build.py needs Python 3.12 or later. No dependencies. Rewrites `docs/` in place. The HTML under `docs/` is machine-written and
must not be hand-edited. Two exceptions are hand-maintained and survive rebuilds because
the generator only writes in place: `docs/assets/css/site.css` and `docs/assets/img/`.

## Link checks

    python3 probe_links.py

Extracts every external href from `docs/` and probes each one. No link is skipped.
Exit 0 means every link answered 2xx. Exit 2 means the only open items are links on the
`BOT_BLOCKED` list (Hashnode, Medium and LinkedIn answer scripts and headless browsers with a
challenge or login wall). The script prints those on every run, and a person must open each
one and confirm it loads the right page. Exit 1 means a link failed, including a listed link
that has gone dead. The venue list on the peer-review page stamps the "verified on" date this
script prints. Re-run it at filing time and do the manual check.

## Editing

Page content is in `build.py`, one `add(path, title, description, body)` call per page.
Content lists sit beside the pages that use them: `HIGHLIGHTS` (home), `HOME_CARDS`
(home), `PAPERS` (publications), `TALKS` (talks), `ARTICLES` (writing), `VENUE_ROWS` and
`COMMITTEE_ROWS` (peer review). Claims use `claim(text, sources)`, external links use
`ext(url, label)`, case-study blocks use `case_study(...)`. Navigation comes from the one
`NAV_GROUPS` table. Each topic page gets its sidebar and sub-tab strip automatically.

## Writing rules

The prose follows the same constraints as every other document in this project, because an
assessor reads this site alongside the form.

- Zero em dashes and zero en dashes
- Zero semicolons
- No sentence carrying an inline comma list of three or more items
- No conclusory adjectives, no promotional language
- Every checkable claim carries a source line
- No awarding body's name appears in anything under `docs/`. Check with
  `grep -riwE "bcs|iet" docs/ | grep -v "docs/bcs/" | grep -v "docs/iet/"`

The evidence register lives at `evidence/EVIDENCE-CHECKLIST.md`, outside the published
tree and untracked.

## Adding an image

Put the file under `docs/assets/img/` and add its alt text and caption to the `IMAGES`
table in `build.py`. An image the pages reference (through `figure` or `thumb`) with no
`IMAGES` entry stops the build, so nothing publishes without alt text. An unreferenced file is
ignored. Check the alt text against the picture. Strip EXIF data
and keep each file near 200 KB or less.

Expected photo names, all optional. A missing file renders nothing.

    talk-aic-keynote.jpg, talk-extract-summit.jpg, talk-iccbi.jpg    talk thumbnails
    mentoring-capstone.jpg                                           mentoring page figure
    card-work.jpg, card-mentoring.jpg, card-community.jpg,
    card-papers.jpg, card-review.jpg, card-writing.jpg               home card art, decorative

Card art needs no `IMAGES` entry, because its alt text is empty by design. Keep anything
containing personal or commercial data, and any photo of a minor, out of `docs/`. Everything
there is public.

To publish an article, add a line to `ARTICLES`. To add a dated highlight, add a line to
`HIGHLIGHTS` with its source.
