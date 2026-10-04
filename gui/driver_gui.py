#!/usr/bin/env python3
"""Catalog GUI for Driver-control.

Browses the old GPU catalog and runs the catalog check.
It does not download or install a driver.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import catalog_tools as tools


def main() -> int:
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        print("This GUI needs tkinter. On Fedora: sudo dnf install python3-tkinter", file=sys.stderr)
        return 1

    try:
        data = tools.load_catalog()
    except (OSError, ValueError) as exc:
        print(f"Could not read the catalog: {exc}", file=sys.stderr)
        return 1

    items = tools.rows(data)
    root = tk.Tk()
    root.title("Driver-control tools")
    root.geometry("760x520")

    warning = ttk.Label(
        root,
        text="Linux virtual machine only. These tools do not install a driver.",
        wraplength=720,
    )
    warning.pack(fill="x", padx=12, pady=(12, 4))

    allowed = tk.BooleanVar(value=False)

    search_var = tk.StringVar()
    status = tk.StringVar(value="Confirm the virtual machine, then pick a card.")
    detail = tk.StringVar(value="No card selected.")

    tools_frame = ttk.Frame(root)
    tools_frame.pack(fill="both", expand=True, padx=12, pady=8)

    search = ttk.Entry(tools_frame, textvariable=search_var)
    search.pack(fill="x")

    listing = tk.Listbox(tools_frame, height=12)
    listing.pack(fill="both", expand=True, pady=8)

    detail_label = ttk.Label(tools_frame, textvariable=detail, wraplength=720, justify="left")
    detail_label.pack(fill="x")
    status_label = ttk.Label(tools_frame, textvariable=status, wraplength=720)
    status_label.pack(fill="x", pady=(6, 0))

    buttons = ttk.Frame(root)
    buttons.pack(fill="x", padx=12, pady=(0, 12))

    def shown_items() -> list[dict[str, str]]:
        return tools.search_rows(items, search_var.get())

    def refill(*_args) -> None:
        listing.delete(0, "end")
        for item in shown_items():
            listing.insert("end", f"{item['vendor']}  {item['branch']}  {item['cards']}")

    def selected() -> dict[str, str] | None:
        picked = listing.curselection()
        current = shown_items()
        if not picked or picked[0] >= len(current):
            return None
        return current[picked[0]]

    def show_selected(_event=None) -> None:
        item = selected()
        if item is None:
            detail.set("No card selected.")
            return
        detail.set(
            f"{item['vendor']} {item['branch']}: {item['cards']}\n"
            f"Try the open-source driver first: {item['open_source']}\n"
            f"Vendor page, for a VM only: {item['source']}"
        )

    def run_check() -> None:
        ok, errors = tools.check_catalog(data)
        if ok:
            status.set(f"Catalog check: ok. {len(items)} target(s). No driver was installed.")
            return
        status.set("Catalog check: fail. " + "; ".join(errors))

    def copy_link() -> None:
        item = selected()
        if item is None:
            status.set("Select a card before copying its vendor page.")
            return
        root.clipboard_clear()
        root.clipboard_append(item["source"])
        status.set("Vendor page copied. Open it yourself, inside the VM only.")

    def toggle() -> None:
        state = "normal" if allowed.get() else "disabled"
        search.configure(state=state)
        listing.configure(state=state)
        for button in (check_button, copy_button):
            button.configure(state=state)
        if allowed.get():
            status.set("Tools unlocked. This still does not install a driver.")
        else:
            status.set("Confirm the virtual machine, then pick a card.")

    check_button = ttk.Button(buttons, text="Check catalog", command=run_check, state="disabled")
    copy_button = ttk.Button(buttons, text="Copy vendor page", command=copy_link, state="disabled")
    check_button.pack(side="left")
    copy_button.pack(side="left", padx=8)

    ttk.Checkbutton(
        root,
        text="I am inside a Linux virtual machine, not a main machine",
        variable=allowed,
        command=toggle,
    ).pack(anchor="w", padx=12, pady=(0, 8))

    search_var.trace_add("write", refill)
    listing.bind("<<ListboxSelect>>", show_selected)
    refill()
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
