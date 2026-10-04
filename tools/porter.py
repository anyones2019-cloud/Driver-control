#!/usr/bin/env python3
"""Greet a programmer the first time they join the repository."""

from __future__ import annotations

import os

OWNER = "anyones2019-cloud"
SKIP = {OWNER, "github-actions", "github-actions[bot]"}
NOTICE = "https://github.com/anyones2019-cloud/Driver-control/discussions/3"
BUGS = "https://github.com/anyones2019-cloud/Driver-control/issues/new?template=bug_report.yml"


def should_greet(author: str, earlier_posts: int) -> bool:
    if not author or author in SKIP or author.endswith("[bot]"):
        return False
    return earlier_posts <= 0


def welcome(author: str) -> str:
    return "\n".join(
        [
            f"Welcome, {author}. I am the porter.",
            "",
            "This is your first time here. Please read the notice board:",
            NOTICE,
            "",
            "House rules:",
            "- Debate the post, not the person.",
            "- A swear word gets a finger wag. Sass at the bot gets a joke, not an insult.",
            "- Test only in a Linux virtual machine. Do not use a main machine or bare metal.",
            "- License is GNU GPL version 3.",
            f"- Bugs go here: {BUGS}",
            "",
            "Glad you joined.",
            "",
        ]
    )


def main() -> int:
    author = os.environ.get("AUTHOR", "")
    earlier = int(os.environ.get("EARLIER_POSTS", "0"))
    if not should_greet(author, earlier):
        print("No greeting. Not a new programmer.")
        return 0
    print(welcome(author), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
