#!/usr/bin/env python3
"""Catalog tools for the Driver-control GUI. No driver is downloaded or installed."""

from __future__ import annotations

import json
import os
from pathlib import Path

VM_RULE = "Linux VM only. Do not install on a main machine."


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def catalog_path() -> Path:
    return repo_root() / "drivers" / "old-gpu-catalog.json"


def load_catalog(path: Path | None = None) -> dict:
    return json.loads((path or catalog_path()).read_text(encoding="utf-8"))


def check_catalog(data: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if data.get("test_rule") != VM_RULE:
        errors.append("missing VM-only rule")
    vendors = data.get("vendors")
    if not isinstance(vendors, list) or not vendors:
        errors.append("vendors missing")
    else:
        for vendor in vendors:
            if not vendor.get("vendor") or not vendor.get("branches"):
                errors.append("vendor entry incomplete")
            for branch in vendor.get("branches") or []:
                if not branch.get("branch") or not branch.get("cards") or not branch.get("source"):
                    errors.append("branch entry incomplete")
    unique: list[str] = []
    for error in errors:
        if error not in unique:
            unique.append(error)
    return (not unique, unique)


def rows(data: dict) -> list[dict[str, str]]:
    found = []
    for vendor in data.get("vendors", []):
        open_source = vendor.get("open_source", "")
        if isinstance(open_source, list):
            open_source = ", ".join(open_source)
        for branch in vendor.get("branches", []):
            cards = branch.get("cards", [])
            found.append(
                {
                    "vendor": str(vendor.get("vendor", "")),
                    "open_source": str(open_source),
                    "branch": str(branch.get("branch", "")),
                    "cards": ", ".join(cards) if isinstance(cards, list) else str(cards),
                    "source": str(branch.get("source", "")),
                }
            )
    return found


def search_rows(items: list[dict[str, str]], query: str) -> list[dict[str, str]]:
    words = query.lower().split()
    if not words:
        return items
    return [item for item in items if all(word in " ".join(item.values()).lower() for word in words)]


def data_dir() -> Path:
    override = os.environ.get("DRIVER_CONTROL_DATA")
    path = Path(override) if override else Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "driver-control"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_selection(item: dict[str, str]) -> Path:
    payload = {
        "program": "driver-control-tools",
        "install": False,
        "vendor": item["vendor"],
        "branch": item["branch"],
        "cards": item["cards"],
        "open_source": item["open_source"],
        "source": item["source"],
    }
    path = data_dir() / "selection.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def read_selection(path: Path | None = None) -> dict:
    file = path or (data_dir() / "selection.json")
    return json.loads(file.read_text(encoding="utf-8"))


def plan(item: dict[str, str]) -> str:
    return "\n".join(
        [
            f"{item['vendor']} {item['branch']}: {item['cards']}",
            f"Try the open-source driver first: {item['open_source']}",
            f"Vendor page, for a VM only: {item['source']}",
            "This program does not install a driver.",
        ]
    ) + "\n"


def refuse_install() -> str:
    return "Refusing to install a driver. Stay in a Linux virtual machine and use the open-source driver from the tools selection.\n"
