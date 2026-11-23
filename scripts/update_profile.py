"""Refresh a local profile card using public GitHub data only.
No third-party statistics service, credentials or private repository access.
"""
import datetime as dt
import html
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
USER = "sh3boo"


def get(path):
    request = urllib.request.Request(
        "https://api.github.com/" + path,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "sh3boo-profile"},
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.load(response)


def main():
    user = get(f"users/{USER}")
    repos = []
    for page in range(1, 21):
        batch = get(f"users/{USER}/repos?per_page=100&page={page}")
        repos.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise RuntimeError("Repository pagination limit reached; keep prior snapshot.")
    owned = [repo for repo in repos if not repo["fork"]]
    stars = sum(repo["stargazers_count"] for repo in owned)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    metrics = [(str(user["public_repos"]), "PUBLIC REPOS"),
               (str(user["followers"]), "FOLLOWERS")]
    for theme, bg, fg, secondary, rule in [
        ("dark", "#0d1720", "#eff8f4", "#9eb6b7", "#29404b"),
        ("light", "#f0f7f3", "#152c30", "#4c6866", "#c9dcd2"),
    ]:
        parts = []
        for index, (value, label) in enumerate(metrics):
            x = 28 + index * 215
            parts.append(f'<text x="{x}" y="135" font-size="52" font-weight="700">{html.escape(value)}</text>')
            parts.append(f'<text x="{x}" y="166" font-size="19" fill="{secondary}">{html.escape(label)}</text>')
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="440" height="270" viewBox="0 0 440 270" role="img" aria-labelledby="title desc">
<title id="title">Public GitHub snapshot</title><desc id="desc">{html.escape(', '.join(value + ' ' + label for value, label in metrics))}. Updated {stamp}.</desc>
<rect width="440" height="270" rx="16" fill="{bg}"/>
<g font-family="Arial, sans-serif" fill="{fg}">
<circle cx="38" cy="36" r="5" fill="#55cfa7"/><text x="54" y="42" font-size="18" letter-spacing="2">GITHUB PULSE</text>
<path d="M28 64H412" stroke="{rule}"/>
{''.join(parts)}
<text x="28" y="216" font-size="17" fill="{secondary}">LAST SUCCESSFUL REFRESH</text>
<text x="28" y="244" font-size="19" fill="{secondary}">{stamp}</text>
</g></svg>'''
        (ROOT / "assets" / f"pulse-{theme}.svg").write_text(svg)
    print(f"Updated public snapshot: {len(repos)} repos, {user['followers']} followers, {stars} non-fork stars.")


if __name__ == "__main__":
    main()
