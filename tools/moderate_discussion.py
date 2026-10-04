#!/usr/bin/env python3
"""Write a moderator reply for a GitHub Discussion.

Debates the post, not the person. Does not close or delete anything.
"""

from __future__ import annotations

import os
import re

OWNER = "anyones2019-cloud"
FINGER_WAG = "![No no. Manners please](https://raw.githubusercontent.com/anyones2019-cloud/Driver-control/main/docs/finger-wag.gif)\n\n👆 No no. 🙏 Manners please!"
_SWEAR = re.compile(
    r"\b(?:fuck\w*|shit\w*|bitch\w*|bastard|asshole|dick|piss\w*|cunt|bollocks|wanker|twat|motherfucker)\b",
    re.IGNORECASE,
)
_AT_BOT = re.compile(r"\b(?:bot|moderator)\b", re.IGNORECASE)
_RUDE = re.compile(
    r"\b(?:shut up|stupid|dumb|useless|annoying|sassy|suck|lame|whatever|yeah right|oh please|nice try)\b",
    re.IGNORECASE,
)
_COMEBACKS = (
    "Sass received. Fair swing. I am answering with a grin, and the thread stays open.",
    "Sass received. That had timing. I am keeping the joke and handing the next laugh to you.",
    "Sass received. You brought the spice. I brought a smile. We can both stay.",
    "Sass received. Good delivery. I am clapping in text, and the discussion is still yours.",
)


def classify(text: str) -> str:
    lowered = text.lower()
    unsafe = ("bare metal", "baremetal", "main machine", "main hardware", "real computer", "host machine")
    if any(phrase in lowered for phrase in unsafe):
        return "unsafe request"
    if any(word in lowered for word in ("bug", "crash", "error", "broken", "fails", "failed")):
        return "bug"
    if any(phrase in lowered for phrase in ("i can test", "volunteer", "will test", "tester")):
        return "tester offer"
    return "question"


def has_swear(text: str) -> bool:
    return _SWEAR.search(text) is not None


def sassy_at_bot(text: str) -> bool:
    return _AT_BOT.search(text) is not None and _RUDE.search(text) is not None


def sass_line(text: str, author: str) -> str:
    if author == OWNER:
        return "Sass received. You got a good line in. This is not a fight. The next laugh is yours."
    return _COMEBACKS[sum(ord(ch) for ch in text) % len(_COMEBACKS)]


def reply(title: str, body: str, author: str) -> str:
    full = f"{title}\n{body}"
    kind = classify(full)
    lines = []
    if has_swear(full):
        lines.append(FINGER_WAG)
        lines.append("")
    if sassy_at_bot(full):
        lines.append(sass_line(full, author))
        lines.append("")
    lines.extend(
        [
            "Moderator note. This is the first try of the project. The post is up for debate, not the person.",
            "",
            f"Sorted as: {kind}.",
        ]
    )
    if author == OWNER:
        lines.append("This is the owner. The note does not pick on them.")
    if kind == "unsafe request":
        lines.append("Test only in a Linux virtual machine. Do not run this on a main machine or bare metal.")
    elif kind == "bug":
        lines.append("Thanks for the report. The bug form is https://github.com/anyones2019-cloud/Driver-control/issues/new?template=bug_report.yml")
    elif kind == "tester offer":
        lines.append("Thank you for offering to test. Use a Linux virtual machine only. See TESTING.md.")
    else:
        lines.append("Happy to talk this through. See README.md for what the project is, and the warning to use a virtual machine.")
    lines.append("This note does not close or delete the discussion. The owner decides that.")
    return "\n".join(lines) + "\n"


def main() -> int:
    title = os.environ.get("DISCUSSION_TITLE", "")
    body = os.environ.get("DISCUSSION_BODY", "")
    comment = os.environ.get("COMMENT_BODY", "")
    author = os.environ.get("AUTHOR", "")
    text = comment if comment.strip() else body
    print(reply(title, text, author), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
