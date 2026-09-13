# Deploy — oversightengineering.com on GitHub Pages

> ## Current status, 13 September 2026
>
> **Live and working over http.** DNS is done: the apex resolves to all four GitHub
> addresses and the site serves `Server: GitHub.com`.
>
>     http://oversightengineering.com/                200
>     http://oversightengineering.com/bcs/invention/  200
>     http://oversightengineering.com/bcs/consultancy/ 200
>     http://oversightengineering.com/bcs/mentoring/  200
>     http://oversightengineering.com/bcs/standing/   200
>
> **HTTPS is not ready.** GitHub is still presenting its `*.github.io` wildcard, which does
> not match the domain, so `https://` fails the certificate check. Let's Encrypt
> provisioning usually completes within a few minutes and can take up to 24 hours. Do not
> tick Enforce HTTPS until `https://oversightengineering.com/` loads without a warning.
>
> **The repo name is misspelled.** It is `oversightengineering` with an extra "ing",
> while the domain is `oversightengineering`. The Pages custom domain is correct, so
> nothing is broken. Rename it if you want the GitHub URL to match:
>
>     gh repo rename oversightengineering
>     git remote set-url origin https://github.com/pravin-khandke/oversightengineering.git
>
> **www points at the apex rather than at GitHub.** It resolves and works, because the apex
> A records carry it through to GitHub. GitHub's own documentation asks for a CNAME to
> `pravin-khandke.github.io` instead. Worth changing if the certificate does not issue on
> its own, since an unexpected record can fail their domain check.

Everything below is the exact sequence. Nothing here is published, because it sits outside `docs/`.

Repo: `~/Documents/GitHub/oversightengineering`
Publish root: `docs/`
Domain: `oversightengineering.com` (registered at GoDaddy)

---

## Part A — Push the repo to GitHub

Run from `~/Documents/GitHub/oversightengineering`:

    git init -b main
    git add -A
    git commit -m "site: BCS and IET fellowship evidence record"
    gh repo create oversightengineering --public --source=. --remote=origin --push

Already done for you if the repo exists. Check with `gh repo view pravin-khandke/oversightengineering`.

---

## Part B — Turn on GitHub Pages

1. Open `https://github.com/pravin-khandke/oversightengineering`
2. Click **Settings** (top row of tabs, far right).
3. In the left sidebar, click **Pages**.
4. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
5. Under **Branch**, pick **main** and set the folder to **/docs**. Click **Save**.
6. Wait one to two minutes. Reload the page. A banner appears saying "Your site is live at ...".
7. The temporary address is `https://pravin-khandke.github.io/oversightengineering/`. Open it and confirm the site loads before touching DNS.

Do not skip step 7. If the site does not load there, DNS will not fix it.

---

## Part C — Point the GoDaddy domain at it

Two records sets are needed: A records for the bare domain, and a CNAME for `www`.

The four A records are GitHub's published addresses, confirmed by DNS lookup at the time of writing:

    185.199.108.153
    185.199.109.153
    185.199.110.153
    185.199.111.153

### Steps in GoDaddy

1. Sign in at `https://sso.godaddy.com`.
2. Go to **My Products**. Find `oversightengineering.com` and click **DNS** (sometimes labelled **Manage DNS**).
3. You will see a records table. Delete the existing **A record** whose name is `@` and whose value points at GoDaddy's parking page. That is the record serving the current "Launching Soon" page.
4. Click **Add New Record** and create the four A records, one at a time:

       Type: A    Name: @    Value: 185.199.108.153    TTL: 600 seconds
       Type: A    Name: @    Value: 185.199.109.153    TTL: 600 seconds
       Type: A    Name: @    Value: 185.199.110.153    TTL: 600 seconds
       Type: A    Name: @    Value: 185.199.111.153    TTL: 600 seconds

5. Add the IPv6 addresses as well, so the site answers on both protocols:

       Type: AAAA    Name: @    Value: 2606:50c0:8000::153    TTL: 600 seconds
       Type: AAAA    Name: @    Value: 2606:50c0:8001::153    TTL: 600 seconds
       Type: AAAA    Name: @    Value: 2606:50c0:8002::153    TTL: 600 seconds
       Type: AAAA    Name: @    Value: 2606:50c0:8003::153    TTL: 600 seconds

6. Edit the existing **CNAME** record named `www` so its value is `pravin-khandke.github.io`. If there is no CNAME record, add one. Do not put a trailing dot, and do not include the repo name.

7. Click **Save**. GoDaddy usually applies the change within a few minutes, though propagation can take up to 48 hours.

### Then tell GitHub about the domain

8. Back in the repo, **Settings** then **Pages**.
9. Under **Custom domain**, type `oversightengineering.com` and click **Save**.
   This writes a `CNAME` file into the publish root. One already exists in `docs/CNAME`, so it will match.
10. Wait for the DNS check to pass. It can take ten minutes to a few hours.
11. Once it passes, tick **Enforce HTTPS**. GitHub issues the certificate on its own. The site will then serve over `https://` and redirect `http://` to it.
12. Tick **Enforce HTTPS** only after the check passes. Ticking it early leaves the site unreachable over both protocols until the certificate is issued.

---

## Part D — Verify

Once DNS has propagated:

    dig +short A oversightengineering.com          # expect the four GitHub addresses
    dig +short CNAME www.oversightengineering.com     # expect pravin-khandke.github.io
    curl -sS -o /dev/null -w "%{http_code}\n" https://oversightengineering.com/
    curl -sS -o /dev/null -w "%{http_code}\n" https://oversightengineering.com/bcs/invention/

All four BCS URL rows need to answer 200, since they go on the form:

    https://oversightengineering.com/bcs/invention/
    https://oversightengineering.com/bcs/consultancy/
    https://oversightengineering.com/bcs/mentoring/
    https://oversightengineering.com/bcs/standing/

Then open each in a browser. This matters more than the status codes do, because BCS promises the linked resource is publicly accessible and supports the position. A page that answers 200 while rendering nothing satisfies the letter and fails the intent.

---

## Part E — If something breaks

| Symptom | Cause and fix |
|---|---|
| Site loads at `github.io` but not on the domain | DNS not propagated, or the A records are wrong. Re-check them with `dig`. |
| GoDaddy shows a "Launching Soon" page still | The old parking A record was not deleted. It must be removed, not added alongside. |
| Custom domain saved but check never passes | The CNAME record for `www` is wrong, or a stale AAAA record is pointing elsewhere. |
| Site loads but CSS is missing | The stylesheet link is absolute (`/assets/css/site.css`). Confirm `docs/assets/css/site.css` was committed. |
| Pages serves nothing, 404 everywhere | Pages source is set to the wrong folder. It must be **main** and **/docs**. |
| Nav links 404 | Every link is absolute to the apex domain. If the site is being tested at the `github.io` address before DNS, links will leave that host. Expected. |

---

## Why the site is shaped the way it is

- **Content lives in `build.py`, not in `docs/`.** `docs/` is generated. Editing it by hand means the next build silently discards the change.
- **`docs/.nojekyll` is deliberate.** It stops GitHub Pages running Jekyll, which does nothing useful here and would ignore files with leading underscores.
- **`docs/CNAME` holds the domain.** GitHub writes it when the custom domain is saved, and shipping it in the repo keeps the setting from being lost.
- **Nothing sensitive is in `docs/`.** The checklist, this file and the build script all sit outside the publish root, so Pages never serves them.
- **The prose follows the same writing rules as every other document.** Zero em dashes, zero semicolons, no inline comma list of three or more items. The build can be re-checked at any time:

      cd ~/Documents/GitHub/oversightengineering && python3 build.py
