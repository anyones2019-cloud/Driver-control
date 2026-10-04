#!/usr/bin/env python3
"""Driver helper. Reads the card chosen in Driver-control Tools. Does not install."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gui"))

import catalog_tools as tools


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--install" in args:
        print(tools.refuse_install(), end="")
        return 2
    try:
        item = tools.read_selection()
    except (OSError, ValueError):
        print("No card selected yet. Open Driver-control Tools and pick a card.", file=sys.stderr)
        return 1
    print(tools.plan(item), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
