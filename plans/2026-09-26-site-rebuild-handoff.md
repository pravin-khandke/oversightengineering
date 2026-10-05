# Site rebuild — handoff for the remaining work

Written 26 September 2026, after the push. Read this together with
`plans/2026-09-26-site-rebuild.md` (the plan) and
`specs/2026-09-26-site-rebuild-design.md` (the spec). The execution ledger,
with every ruling, is at `.superpowers/sdd/2026-09-26-site-rebuild/progress.md`.

## Where things stand

Pushed to origin/main and live. Three commits:

- `0d4be69` — rebuilt home page. Single scrolling record: hero with photo
  (`docs/assets/img/profile.jpg`, 370x480, EXIF stripped), grade chips, the
  four counters (26 years, 26 venues, 4 committees, 2 publications), connect
  row (ORCID, LinkedIn, email only), sections through education. Deep blue on
  white stylesheet with a print block that reveals link addresses.
- `8bb0b81` — memberships, publications, talks and peer-review folded into
  meta-refresh stubs, README and DEPLOY updated.
- `f30dc77` — detail pages and 404 regenerated with the current template
  (og:image, Standing nav label, folded footer, wording strips).

Live checks that passed on 26 September: all 13 URLs answer 200 over http,
the four form URLs (`/bcs/...`) redirect correctly, the photo serves, the
counters read 26/26/4/2 on the live page. HTTPS still fails (certificate
null), which is the known user action item.

The private evidence checklist and TODO were refreshed in `evidence/`
(gitignored, never pushed): TODO went from 38 open items to 27, the
venue-to-folder mapping table is in `evidence/EVIDENCE-CHECKLIST.md`.

## The mid-flight decision that changed the plan

After seeing the rebuilt site live, you said the single-page structure is not
what you selected in the brainstorming, and you chose **"Restore the four
pages"**: memberships, publications, talks and peer-review come back as real
standalone pages. The spec's folding decision is overridden by this
instruction. That reversal is the first item of remaining work and nothing
below depends on it being done any particular way.

## Remaining work, in order

### 1. Restore the four pages (memberships, publications, talks, peer-review)

The old page definitions were deleted from `build.py` by the fold commit.
Recover them from git history:

    git show 45dfc89:build.py > /tmp/old-build.py
    # the four add(".../index.html", ...) calls sit near the bottom,
    # each ending at a closing """) at column 0

Re-insert all four `add(...)` calls into the current `build.py`, after the
standing detail page call and before `REDIRECTS`. Then:

- Remove the four entries from `REDIRECTS` (lines 1000-1003) so the real
  pages win. Keep the five `bcs/*` and `iet` stubs, which the submitted form
  depends on.
- Give the four pages a nav so they are not orphaned. The detail pages use
  `nav("bcs")` with four links. Either extend that list or link them from the
  home sections and footer. They must be reachable.
- Strip every awarding body name from the four pages. The detail pages had
  kickers and notes with the name; the old pages carry it too. Run the check:

      grep -riwE "bcs|iet" docs/ | grep -v "docs/bcs/" | grep -v "docs/iet/"

- On the restored peer-review page, replace its unlinked venue list with the
  linked rows the home page uses: `venue_rows_html()` and
  `committee_rows_html()` already exist in `build.py` and render the 26
  venues (18 linked, 8 marked no live listing) and 4 committees. The home
  page's src-note wording can be reused.
- Check the writing rules on the restored text: no em dashes, no semicolons,
  no inline comma list of three or more items, no conclusory adjectives.

### 2. Update README.md

The layout section currently says the four directories are redirect stubs.
Restore their descriptions (the old wording is in `git show 45dfc89:README.md`)
with the new note that each page's claims stay consistent with the home page.

### 3. Rebuild and verify

    python3 build.py
    python3 probe_links.py          # expect 0 failing
    grep -riwE "bcs|iet" docs/ | grep -v "docs/bcs/" | grep -v "docs/iet/"
    # browse at 375px and 1280px, all 9 pages, no horizontal overflow
    # check the restored pages carry the noindex meta tag

Commit, push, then re-verify live with the curl loop from the session
(the 13 URLs over http, plus each restored page's content).

### 4. Evidence copy (Task 12) — still not done

Blocked repeatedly by a tool outage. The script is ready:

    zsh .superpowers/sdd/2026-09-26-site-rebuild/copy_evidence.sh

It rsyncs `~/Documents/EB1A/EB1A_Evidence/` into `evidence/eb1a_evidence/`
and the Drive Peerreview folder (`My Drive/Pravin /Peerreview`, 229 files,
96 MB) into `evidence/reviews/`, then confirms `evidence/` stays untracked.
No commit — the folder is gitignored.

### 5. Finish the checklist (Task 13 residue)

After the copy, recompute `find evidence -type f | wc -l` and add the total
to the mapping table in `evidence/EVIDENCE-CHECKLIST.md`. Counts per venue
are already in the table; only the grand total needs the copy first.

### 6. Final review

One fresh-context review of the whole branch, per the executing-plans skill,
then fix anything Critical or Important in one pass. The review should check
that the restored pages and the home page tell the same story (the four
counters, the venue list, the recognitions rows) — that consistency is the
main risk the reversal introduced.

## Constraints that still bind

- `evidence/` never tracked, never published. Repo is public.
- No awarding body's name in anything under `docs/` or in folder names.
- Writing rules: no em dashes, no semicolons, no 3+-item inline comma lists,
  no conclusory adjectives, every checkable claim carries a source line.
- Hero counters stay exactly 26 years, the venue count the page totals
  (26), 4 committees, 2 publications. No review count anywhere.
- Connect row is ORCID, LinkedIn, email only. No Google Scholar.
- No scanned certificates on the site. Recognition links to registers.
- Every page carries the noindex robots meta; robots.txt disallows all.
  Search Console Removals is the remedy for anything indexed before
  13 September.

## Loose ends

- A localhost:8734 server serving `docs/` may still be running in the
  background from the browse checks. Kill it if you see it:
  `lsof -ti :8734 | xargs kill`.
- The visual companion server from the brainstorming may also be running:
  `bash .superpowers/brainstorm/4349-1790447655/scripts/stop-server.sh`.
- After the final review passes, delete
  `.superpowers/sdd/2026-09-26-site-rebuild/` — the git history is the
  record then, but copy anything you need out of the ledger first.
