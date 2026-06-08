#!/usr/bin/env python3
"""Post oss-paper-ci report as a GitHub PR comment.

Usage in GitHub Actions:
    - name: Comment PR
      if: github.event_name == 'pull_request'
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: python scripts/comment_pr.py oss-paper-ci-report.md
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: comment_pr.py <report.md>")
        return 1

    report_path = sys.argv[1]
    if not os.path.exists(report_path):
        print(f"Report not found: {report_path}")
        return 0

    # Check if running in GitHub Actions context
    github_token = os.environ.get("GITHUB_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")

    if not github_token or not repository:
        print("Not in GitHub Actions context. Skipping PR comment.")
        print(f"Report available at: {report_path}")
        return 0

    # Read report
    with open(report_path, encoding="utf-8") as f:
        report_content = f.read()

    # Get PR number from event payload
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    pr_number = None

    if event_path and os.path.exists(event_path):
        with open(event_path, encoding="utf-8") as f:
            event = json.load(f)
        pr_number = event.get("pull_request", {}).get("number")

    if not pr_number:
        print("Not a pull_request event. Skipping comment.")
        return 0

    # Post comment via GitHub API
    url = f"https://api.github.com/repos/{repository}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = json.dumps({"body": report_content}).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            print(f"Comment posted to PR #{pr_number} (HTTP {status})")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Failed to post comment: HTTP {e.code} - {body}")
        return 1
    except Exception as e:
        print(f"Failed to post comment: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
