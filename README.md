# oversightingengineering.com

Source for `https://oversightengineering.com`, the public record of the work cited in
Pravin Khandke's BCS and IET fellowship applications.

## Layout

    build.py                  site generator. Page content lives here, one add(...) per page
    docs/                     PUBLISHED. GitHub Pages serves this folder and nothing else
      index.html              overview and evidence map
      memberships/            grades held, conferring body, verification route
      bcs/invention/          BCS: Body of work, Invention and innovation
      bcs/consultancy/        BCS: Body of work, Consultancy
      bcs/mentoring/          BCS: Professional impact, Mentoring and coaching
      bcs/standing/           BCS: Standing in the community, Public influencer
      publications/           papers, presentations, technical writing
      talks/                  keynotes and conference sessions
      peer-review/            review venues and committee appointments
      iet/                    IET criteria in preparation
      assets/css/site.css     styles, including a print stylesheet for assessors
      CNAME                   the custom domain
      .nojekyll               stop GitHub Pages running Jekyll
    EVIDENCE-CHECKLIST.md     what is backed, what is withheld, what is still missing
    DEPLOY.md                 GitHub Pages and GoDaddy DNS, step by step

## Build

    python3 build.py

No dependencies. Rewrites `docs/` in place. Do not hand-edit `docs/`.

## Editing

Page content is in `build.py` near the bottom, one `add(path, title, description, body)`
call per page. Each claim is written with the `claim(text, sources)` helper, which renders
the source line underneath it. External links use `ext(url, label)`, which adds the outward
arrow marker.

Adding a page means adding one `add(...)` call. The navigation is generated from the
`nav()` function, so a new page needs an entry there as well.

## Writing rules

The prose follows the same constraints as every other document in this project, because an
assessor reads this site alongside the form.

- Zero em dashes and zero en dashes
- Zero semicolons
- No sentence carrying an inline comma list of three or more items
- No conclusory adjectives, no promotional language
- Every checkable claim carries a source line

`EVIDENCE-CHECKLIST.md` records the verification state of each URL.

## Adding an image

Put it under `docs/assets/img/` and reference it with an absolute path,
`/assets/img/name.png`, so it resolves from every page. Add descriptive `alt` text. Keep
anything containing personal or commercial data out of `docs/`, since everything there is
public.
