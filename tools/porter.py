#!/usr/bin/env python3
"""Greet a programmer the first time they join the repository."""

from __future__ import annotations

import os

OWNER = "anyones2019-cloud"
SKIP = {OWNER, "github-actions", "github-actions[bot]"}
NOTICE = "https://github.com/anyones2019-cloud/Driver-control/discussions/3"
BUGS = "https://github.com/anyones2019-cloud/Driver-control/issues/new?template=bug_report.yml"
GUI_BUGS = "https://github.com/anyones2019-cloud/Driver-control/issues/new?template=gui_bug_report.yml"


def should_greet(author: str, earlier_posts: int) -> bool:
    if not author or author in SKIP or author.endswith("[bot]"):
        return False
    return earlier_posts <= 0


def welcome(author: str) -> str:
    return "\n".join(
        [
            f"Welcome, {author}. I am the porter. I will show you around.",
            "",
            "What this project is",
            "Driver-control is a beginner project. The aim is a GUI that helps people install Linux hardware drivers, with Fedora, Flatpak, and gaming hardware in mind. The owner is learning in public. A catalog GUI is in gui/driver_gui.py. It does not install drivers. Run it only in a Linux virtual machine.",
            "",
            "License",
            "GNU GPL version 3. Read LICENSE before you copy or change the project.",
            "",
            "Map of the repo",
            "- README.md is the front door and the warning.",
            "- TESTING.md is the tester checklist.",
            "- LINUX-VM.md is the virtual-machine note.",
            "- drivers/README.md explains old NVIDIA, AMD, and Intel GPU families.",
            "- drivers/old-gpu-catalog.json is the list of old GPU targets. It is a catalog, not a driver download.",
            "- scripts/check-catalog.py checks that catalog. On a good run it prints ok.",
            "- packaging/flatpak/FLATPAK.md builds Driver-control Tools as its own Flatpak. Picking a card writes a selection. scripts/driver_link.py reads it and refuses to install a driver.",
            f"- The discussion notice board is {NOTICE}",
            "",
            "How a new programmer should test",
            "1. Use a Linux virtual machine only. Fedora is the target. Flatpak is the intended install path.",
            "2. Run python3 scripts/check-catalog.py and look for ok.",
            "3. Pick one old GPU family from the catalog.",
            "4. Try the open-source driver first. Those already in the kernel and Mesa are nouveau, radeon, amdgpu, and i915.",
            "5. This repo does not contain NVIDIA, AMD, or Intel proprietary binaries. Download those from the vendor, and only inside the VM.",
            "6. Report the distro, the VM software, the catalog result, and pass or fail.",
            f"Bug form: {BUGS}",
            f"GUI bug form: {GUI_BUGS}",
            "",
            "Safety that is already on",
            "Every push and pull request is virus-scanned. A clean commit stays on main. Only an infected commit is moved to quarantine.",
            "In Discussions, debate the post, not the person. A swear word gets a finger wag. Sass at the bot gets a joke, not an insult. The bot does not pick on the owner, and it does not close or delete a discussion.",
            "",
            "Do not run this on a main machine or bare metal.",
            "Glad you joined. Ask in Discussions if you get lost.",
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
