#!/usr/bin/env python3
"""Probe every external link in docs/ so the check can be re-run at filing time.

Run:  python3 probe_links.py

Every link is probed. None is skipped. A link falls into one of three groups:
  ok       the server answered 2xx
  BLOCKED  the server refused a script (403, 429 or 999) and the link is on the
           BOT_BLOCKED list. A person must open it. It is printed on every run.
  FAIL     anything else, including a dead link that is on the BOT_BLOCKED list

Exit 0 when every link is ok. Exit 2 when the only open items are BLOCKED links that
need a manual check. Exit 1 when any link fails.
"""
import pathlib, re, sys, urllib.request, urllib.error, datetime

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"
# Sites that answer scripts and headless browsers with a challenge page or a login wall.
# Checked 11 October 2026: Cloudflare challenge on Hashnode and Medium, login wall on LinkedIn.
BOT_BLOCKED = {
    "https://pravin-khandke.hashnode.dev/",
    "https://pravin-khandke.hashnode.dev/clean-code-at-scale-how-sonar-became-our-silent-reviewer",
    "https://pravin-khandke.hashnode.dev/the-emergence-of-explainable-ai-in-deep-learning-bridging-the-gap-between-model-complexity-and-human-trust",
    "https://medium.com/@Pravin-Khandke/backend-architecture-in-the-age-of-ai-e73cc8bbf599",
    "https://medium.com/authority-magazine/c-suite-perspectives-on-ai-pravin-khandke-on-where-to-use-ai-and-where-to-rely-only-on-humans-854b733e03a1",
    "https://www.linkedin.com/in/pravin-khandke",
}
BLOCK_STATUSES = {403, 429, 999}
# Connection hints in the page head, not links a reader follows.
NOT_LINKS = {"https://fonts.googleapis.com", "https://fonts.gstatic.com"}
# The site's own pages: probing them here fails while HTTPS is broken, and
# the final verification checks them with curl instead.
OWN_PREFIX = "https://oversightengineering.com"


def links():
    text = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                     for p in OUT.rglob("*.html"))
    for href in re.findall(r'href="(https?://[^"]+)"', text):
        if href.startswith(OWN_PREFIX) or href in NOT_LINKS:
            continue
        yield href


def probe(url):
    """Return the HTTP status, or "unreachable". HTTP errors keep their real code."""
    last = "unreachable"
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method,
                                     headers={"User-Agent": "Mozilla/5.0 linkcheck"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status
        except urllib.error.HTTPError as e:
            last = e.code
        except Exception:
            last = "unreachable"
    return last


def classify(url, status):
    # Any 2xx counts: IEEE endpoints answer bots with 202 Accepted.
    if isinstance(status, int) and 200 <= status < 300:
        return "ok"
    if url in BOT_BLOCKED and status in BLOCK_STATUSES:
        return "BLOCKED"
    return "FAIL"


def main():
    urls = sorted(set(links()))
    failing, blocked = [], []
    for url in urls:
        status = probe(url)
        group = classify(url, status)
        print(f"{group:<7} {status}  {url}")
        if group == "FAIL":
            failing.append(url)
        elif group == "BLOCKED":
            blocked.append(url)
    print(f"\nprobed {len(urls)} links: {len(urls) - len(failing) - len(blocked)} ok, "
          f"{len(blocked)} blocked, {len(failing)} failing")
    today = datetime.date.today().strftime("%-d %B %Y")
    if blocked:
        print("\nOpen these in a browser and confirm each one loads the right page:")
        for url in blocked:
            print("  " + url)
    print(f"\nVerified on {today}" + (", except the blocked links above" if blocked else ""))
    sys.exit(1 if failing else (2 if blocked else 0))


if __name__ == "__main__":
    main()
