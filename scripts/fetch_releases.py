#!/usr/bin/env python3
"""Download the signed APKs attached to the apps' GitHub Releases into repo/.

Reads apps.yml. Each APK gets its release's publication date as its file date, so that
`fdroid update --use-date-from-apk` gives every version a stable "added" date from one run to
the next. Writes sources.txt, one line per downloaded asset, which the workflow uses to tell
whether anything changed since the last deployment.

Needs GH_TOKEN (any token that can read the repositories' releases).
"""

import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

import yaml

API = "https://api.github.com"
REPO_DIR = Path("repo")


def request(url, accept="application/vnd.github+json"):
    headers = {"Accept": accept, "X-GitHub-Api-Version": "2022-11-28"}
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=120)


def releases(repo):
    with request(f"{API}/repos/{repo}/releases?per_page=100") as response:
        return json.load(response)


def wanted(asset):
    """Release APKs only: a debug build can't update a release-signed install."""
    name = asset["name"].lower()
    return name.endswith(".apk") and "debug" not in name and "unsigned" not in name


def main():
    apps = yaml.safe_load(Path("apps.yml").read_text())["apps"]
    REPO_DIR.mkdir(exist_ok=True)
    sources = []
    problems = 0

    for app in apps:
        repo = app["repo"]
        keep = int(app.get("keep", 3))
        try:
            published = [r for r in releases(repo) if not r["draft"] and not r["prerelease"]]
        except Exception as error:  # noqa: BLE001 - report and go on with the other apps
            print(f"::warning::{repo}: can't list releases ({error}). A private repository "
                  "needs the APPS_TOKEN secret.")
            problems += 1
            continue
        published.sort(key=lambda r: r["published_at"], reverse=True)

        found = 0
        for release in published:
            apks = [a for a in release["assets"] if wanted(a)]
            if not apks:
                continue
            found += 1
            if found > keep:
                break
            date = datetime.fromisoformat(release["published_at"].replace("Z", "+00:00"))
            for asset in apks:
                # Unique per release: some apps give every release's APK the same name.
                filename = f"{repo.split('/')[1]}-{release['tag_name']}-{asset['name']}"
                filename = filename.replace("/", "_")
                target = REPO_DIR / filename
                print(f"{repo} {release['tag_name']}: {asset['name']}")
                with request(asset["url"], accept="application/octet-stream") as response:
                    target.write_bytes(response.read())
                os.utime(target, (date.timestamp(), date.timestamp()))
                sources.append(f"{repo} {release['tag_name']} {asset['id']} {asset['updated_at']}")
        if not found:
            print(f"::notice::{repo}: no release with a signed APK yet")

    Path("sources.txt").write_text("".join(line + "\n" for line in sorted(sources)))
    print(f"{len(sources)} APKs downloaded")
    # Don't publish a repository with apps silently missing from it.
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
