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
    "https://pravin-khandke.hashnode.dev/clean-code-at-scale-how-sonar-became-our-silent-reviewer",
    "https://medium.com/@Pravin-Khandke/backend-architecture-in-the-age-of-ai-e73cc8bbf599",
    "https://medium.com/authority-magazine",
    "https://www.linkedin.com/in/pravin-khandke",  # blocks bots, opens for a person
    "https://fonts.googleapis.com",                # preconnect hint, not a link
    "https://fonts.gstatic.com",                   # preconnect hint, not a link
}
# The site's own pages: probing them here fails while HTTPS is broken, and
# the final verification task checks them with curl instead.
OWN_PREFIX = "https://oversightengineering.com"

def links():
    text = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                     for p in OUT.rglob("*.html"))
    for href in re.findall(r'href="(https?://[^"]+)"', text):
        if href.startswith(OWN_PREFIX):
            continue
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

def ok(url, status):
    # Any 2xx counts: IEEE endpoints answer bots with 202 Accepted.
    return (isinstance(status, int) and 200 <= status < 300) or (url in EXCEPTIONS)

def main():
    urls = sorted(set(links()))
    bad = []
    for url in urls:
        status = probe(url)
        good = ok(url, status)
        print(("ok  " if good else "FAIL") + f" {status}  {url}")
        if not good:
            bad.append(url)
    print(f"\nprobed {len(urls)} links, {len(bad)} failing")
    print("Verified on " + datetime.date.today().strftime("%-d %B %Y"))
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()