# oversightengineering.com

Source for `https://oversightengineering.com`, the public record of the work cited in
Pravin Khandke's fellowship application.

## Layout

    build.py                  site generator. Page content lives here, one add(...) per page
    probe_links.py            probes every external link in docs/, prints a Verified-on date
    docs/                     PUBLISHED. GitHub Pages serves this folder and nothing else
      index.html              one scrolling evidence record: hero, about, invention,
                              leadership, mentoring, standing, recognitions, publications,
                              education
      invention/              full record, body of work, invention and innovation
      consultancy/            full record, body of work, consultancy
      mentoring/              full record, professional impact, mentoring and coaching
      standing/               full record, standing in the community
      bcs/                    redirect stubs. The submitted form carries /bcs/ URLs, so
                              they keep resolving
      iet/                    redirect stub to home, for a once-published address
      memberships/, publications/, talks/, peer-review/
                              redirect stubs into the home page sections they folded into
      assets/css/site.css     styles, hand-maintained, including a print stylesheet
      assets/img/             images, hand-maintained. profile.jpg is the hero photo
      CNAME                   the custom domain
      .nojekyll               stop GitHub Pages running Jekyll
    specs/                    design specs, tracked working documents
    plans/                    implementation plans, tracked working documents
    evidence/                 PRIVATE, gitignored, never published. See evidence/README.md

## Build

    python3 build.py

No dependencies. Rewrites `docs/` in place. The HTML under `docs/` is machine-written and
must not be hand-edited. Two exceptions are hand-maintained and survive rebuilds because
the generator only writes in place: `docs/assets/css/site.css` and `docs/assets/img/`.

## Link checks

    python3 probe_links.py

Extracts every external href from `docs/` and probes each one. Exit 0 means every link
returned 200 or is a named exception in the script. The venue list on the home page stamps
the "verified on" date this script prints. Re-run it at filing time.

## Editing

Page content is in `build.py`, one `add(path, title, description, body)` call per page.
The home page is assembled from the VENUE_ROWS and COMMITTEE_ROWS lists plus the section
markup in its one `add(...)` call. Claims use the `claim(text, sources)` helper, external
links use `ext(url, label)`. Navigation is generated: `nav_home()` for the home page's
anchors, `nav()` for the detail pages.

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

Put it under `docs/assets/img/` and reference it with an absolute path,
`/assets/img/name.png`, so it resolves from every page. Add descriptive `alt` text. Keep
anything containing personal or commercial data out of `docs/`, since everything there is
public.
