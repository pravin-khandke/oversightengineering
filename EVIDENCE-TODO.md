# Evidence TODO

Generated 13 September 2026 from the evidence register in `EVIDENCE-CHECKLIST.md`.
Open count: **38**. The three under Start here repeat items further down, so there are 41
boxes and 38 distinct jobs. Nothing here is finished until its box is ticked.

Markers

- `[site]` goes on a public page
- `[file]` goes in the application and the evidence folder, not the public site
- **Me** / **You** is who can actually produce it

---

## Start here — three items that unlock the most

- [ ] **Add the eighteen verified venue links to `/peer-review/`** `[site]` **Me**
      Verified today, all returned 200, already in the resume. Closes the largest gap on the
      site, because thirty venues are currently named and none is linked.

- [ ] **Find the IJCA article URL or DOI** `[site]` **You**
      Four claims on the invention page rest on that paper and all four point at the journal,
      which proves the journal exists and not that the paper does. Highest value single link.

- [ ] **Create a Web of Science Researcher Profile** **You**
      Not created. The one item that changes the character of the review evidence rather than
      adding to it, because claimed reviews become a third party record instead of a number
      on your own page. Free, claimed venue by venue.

---

## Peer review and technical programme committees

- [ ] **Add the eighteen verified venue links** `[site]` **Me**
      Two cannot be reused as they stand: ICETM returns 404 and the CICBA domain no longer
      resolves. For the four committee venues the committee page is the correct target rather
      than the homepage, since the committee page is what names you. AIIoT and SIME are held.
      BDAA and NGSME are not.

- [ ] **Create a Web of Science Researcher Profile** **You**
      See Start here.

- [ ] **Check each venue for a published reviewer acknowledgement page** `[site]` **You**
      A link naming you on somebody else's site is the cheapest proof available and cannot be
      accused of self reporting. Pass the URLs to me and I will verify each one.

- [ ] **Add console screenshots as page evidence** `[site]` **Me**
      Nine are on file, seven from IECON and two from iSemantic. One screenshot of a completed
      review on the conference's own portal outperforms any sentence about it.

- [ ] **Produce the thirteen missing reviews** `[file]` **You**
      CICBA 3, ETECOM 2, ICTMOD 2, ICAITech 1, PlatCon 1, and four of INTCEC's five.
      Corrected from eleven after two earlier audits in the same folder were found. ICTMOD's
      two papers sit loose in the conference folder root, and the first scan only looked inside
      `Papers/` so it missed them and understated the gap.

- [ ] **Decide which review definition the application rests on** **You**
      The 29 August audit counts only dedicated per-paper review documents and finds 66 papers
      covered with a 20 paper gap. The 5 September audit also counts confirmation emails and
      console screenshots and finds 73 covered with a 12 paper gap. The published figure is 73,
      true under the looser definition and overstated under the stricter one.

- [ ] **Open evidence folders for the six venues that have none** `[file]` **You**
      SIME, TEMSMET, ARIIA and ICNSBT have no folder. CICA and ICTMOD have empty ones. Largest
      single gap in the record.

- [ ] **Export the reviews that exist only as confirmations** `[file]` **You**
      Of the 73 files in the Reviews folders, 36 are confirmations and receipts, 27 are review
      documents, 9 are console screenshots. A confirmation proves a review happened, it does
      not carry it.

- [ ] **Request certificates and thank you letters for the roles that lack them** `[file]` **You**
      Certificates are on file for AIIoT, ICCUBEA, ICDCECE, ICoIAS, MeditCom and NGSME only.
      I can draft the requests.

---

## Talks and keynotes

- [ ] **Add the Extract Summit speakers page** `[site]` **Me**
      `https://www.extractsummit.io/speakers`. Verified, and it carries your name and title in
      its own HTML. Strongest single item held. Belongs on `/talks/` and the standing page.

- [ ] **Find the AIC 2026 keynote list page** `[site]` **You**
      The resume claims you are named on the organiser's published keynote list. Only the
      conference page is held, not that list.

- [ ] **Find the ICCBI programme page**, if the conference publishes one `[site]` **You**

---

## Publications

- [ ] **Find the IJCA article URL or DOI** `[site]` **You**
      See Start here.

- [ ] **Find the ICCBI paper link**, if IEEE Xplore has it yet `[site]` **You**

---

## Memberships

- [ ] **Find the IEEE Senior Member register link** `[site]` **You**, then **Me** to add
      So the grade can be looked up rather than believed.

- [ ] **Find the RSS Fellow verification route** `[site]` **You**, then **Me** to add
      Sits alongside the SAS verification page already linked.

- [ ] **Add ORCID and LinkedIn to `/memberships/`** `[site]` **Me**
      ORCID is in the footer and on the home page. The memberships page is what an assessor
      reads beside the form.

---

## Standing and influence

- [ ] **Find the Authority Magazine article URL** `[site]` **You**
      Cited on the standing page as an interview and currently unlinked.

- [ ] **Find the HackerNoon ranking page** `[site]` **You**
      The claim that you rank 7th among AI and ML writers should point at HackerNoon's own
      numbering.

- [ ] **Add the children's AI guide repository** `[site]` **Me**
      `github.com/pravin-khandke/safe-ai-for-kids`, public and self verifying.

---

## Mentoring

- [ ] **Get the KSU capstone listing or sponsorship letter** `[site]` **You**
      Two mentoring claims currently source to project documentation that is not in hand.

---

## Locations for the venues with no flag

- [ ] **Supply the location for CICA, TEMSMET, ICAITech, ICNSBT, ARIIA and PlatCon** `[site]` **You**
      Seven venues carry no country flag because no location is recorded for them anywhere in
      the skills, notes or evidence folders. INTCEC genuinely has no physical venue, being a
      CMT-based international conference, so no flag is correct for it. Send the six and I
      will add their flags in one pass.

---

## Folder hygiene, surfaced by the earlier audits

- [ ] **Rename `2206_PlatCon` to `2026_PlatCon`** **You**
      Year typo in the folder name.

- [ ] **Strip the trailing space from the `2026 ICAITech ` folder name** **You**
      The space breaks path handling in scripts that do not quote.

- [ ] **Move the misfiled AMLDS certificate** **You**
      `2026_SMC/Certificate Pravin Khandke.pdf` is actually the AMLDS 2026 certificate. It
      belongs in `2026_AMLDS/` named `05_Certificate_AMLDS_2026.pdf` per the convention, and
      the SMC folder holds nothing else.

- [ ] **Give ICTMOD a folder structure** **You**
      Its two papers sit loose at the folder root with no `Papers/` or `Reviews/`. That is what
      made the first count miss them.

- [ ] **Consolidate `2026_iSemantic/reviews/` into `Reviews/`** **You**
      A redundant lowercase directory sits alongside the uppercase one. macOS treats them as
      separate, which is how evidence has gone missing before.

## Carried over from the first build

- [ ] **Lock the Capgemini and Cox dates** **You**
      The site says account 2004 to 2022 and migration 2013 to 2022, taken from the live form.
      The resume, LinkedIn and three earlier notes give other values, and there is an
      unexplained gap from March 2008 to May 2013. Nothing else on the consultancy page should
      be trusted until this is settled.

- [ ] **Confirm the four consultancy recommendations with the supporter** **You**
      Every consultancy claim sources to client confirmation available through the named
      supporter. Honest, and the weakest sourcing on the site. If the supporter will not
      attest to a specific recommendation, it comes off the page.

- [ ] **Open the Medium and Hashnode links by hand** **You**
      Both refuse scripted requests so they could not be checked. The Explainable AI entry
      points at the profile rather than the article and needs the article URL.

- [ ] **Confirm SCRS Fellow from a document** **You**
      The Soft Computing Research Society organises AIC 2026, the conference whose keynote the
      standing page cites. A fellowship grade from an IEEE conference organiser is worth
      publishing properly. If confirmed it belongs in the graded section.

- [ ] **Add evidence images** `[site]` **Me**, once you supply them
      Both reference sites carry none and neither does this one. Screenshots of a committee
      listing, a keynote slide or an award page would make the pages credible at a glance.
      Keep any that holds personal data out of `docs/`.

- [ ] **Revisit the IET page when the criteria are settled** `[site]` **Me** with **You**
      It names Repute and Insight and Experience as in preparation and leaves a third
      criterion open. Nothing on it is a submission yet.

---

## Also outstanding, from earlier today

- [ ] **Fix the https certificate** **You**
      Change the GoDaddy `www` record from `oversightengineering.com.` to
      `pravin-khandke.github.io`, then I will confirm the certificate and enable enforcement.
      The four URLs now in the BCS form point at https that does not work yet.

- [ ] **Replace the two dead resume links** **You**
      ICETM returns 404, and the CICBA domain no longer resolves.

- [ ] **Decide on the IECON and INCOSST counts** **You**
      IECON now carries three figures: 10 papers with a dedicated review, 14 on the venue list,
      17 papers on file. The 29 August audit is the only one that separates dedicated reviews
      from confirmations and it says 10. INCOSST: 6 on the list, 5 in the folder.

- [ ] **Settle the published figure conflict** **You**
      The Authority Magazine bio says 60+ papers across 17 conferences. The resume, the form
      and the site now say 73 papers across 26 venues. "More than 60" remains true, so it is
      not a contradiction, but an assessor comparing them sees a jump.

- [ ] **Update LinkedIn to the corrected figures** **You**, or **Me** to draft the wording
      The live profile still carries the old counts.

---

## Tally

| Area | Open |
|---|---|
| Peer review and committees | 8 |
| Talks and keynotes | 3 |
| Publications | 2 |
| Memberships | 3 |
| Standing and influence | 3 |
| Mentoring | 1 |
| Venue locations for flags | 1 |
| Folder hygiene | 5 |
| Carried over | 6 |
| Earlier today | 5 |
| **Total** | **38** |

Items marked **Me** can be done without anything from you, except the eighteen venue links
which need the ICETM and CICBA replacements and the six missing locations first.
