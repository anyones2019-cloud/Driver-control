#!/usr/bin/env python3
"""Flatpak window for Driver-control Tools. Uses GTK 4.24 from the GNOME 51 runtime."""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import catalog_tools as tools

APP_ID = "io.github.anyones2019.DriverControlTools"


def main() -> int:
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk

    data = tools.load_catalog()
    items = tools.rows(data)

    class ToolsApp(Gtk.Application):
        def do_activate(self):
            window = Gtk.ApplicationWindow(application=self, title="Driver-control Tools")
            window.set_default_size(760, 520)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            box.set_margin_top(12)
            box.set_margin_bottom(12)
            box.set_margin_start(12)
            box.set_margin_end(12)
            window.set_child(box)

            box.append(Gtk.Label(label="Linux virtual machine only. This program does not install a driver.", wrap=True, xalign=0))
            box.append(Gtk.Label(label="GUI bug report: https://github.com/anyones2019-cloud/Driver-control/issues/new?template=gui_bug_report.yml", wrap=True, xalign=0))

            allowed = Gtk.CheckButton(label="I am inside a Linux virtual machine, not a main machine")
            box.append(allowed)

            search = Gtk.Entry(placeholder_text="Search cards")
            box.append(search)

            scrolled = Gtk.ScrolledWindow()
            scrolled.set_vexpand(True)
            listing = Gtk.ListBox()
            listing.set_selection_mode(Gtk.SelectionMode.SINGLE)
            scrolled.set_child(listing)
            box.append(scrolled)

            detail = Gtk.Label(label="No card selected.", wrap=True, xalign=0)
            status = Gtk.Label(label="Confirm the virtual machine, then pick a card.", wrap=True, xalign=0)
            box.append(detail)
            box.append(status)

            actions = Gtk.Box(spacing=8)
            check_button = Gtk.Button(label="Check catalog")
            copy_button = Gtk.Button(label="Copy vendor page")
            actions.append(check_button)
            actions.append(copy_button)
            box.append(actions)

            rows_by_widget = []

            def visible_items():
                return tools.search_rows(items, search.get_text())

            def refill():
                nonlocal rows_by_widget
                while child := listing.get_first_child():
                    listing.remove(child)
                rows_by_widget = []
                for item in visible_items():
                    label = Gtk.Label(label=f"{item['vendor']}  {item['branch']}  {item['cards']}", xalign=0)
                    listing.append(label)
                    rows_by_widget.append(item)

            def selected_item():
                row = listing.get_selected_row()
                if row is None:
                    return None
                index = row.get_index()
                if index < 0 or index >= len(rows_by_widget):
                    return None
                return rows_by_widget[index]

            def on_select(_listing, _row):
                item = selected_item()
                if item is None:
                    detail.set_text("No card selected.")
                    return
                detail.set_text(tools.plan(item).rstrip())
                tools.write_selection(item)
                status.set_text("Saved for the driver helper. No driver was installed.")

            def on_check(_button):
                ok, errors = tools.check_catalog(data)
                if ok:
                    status.set_text(f"Catalog check: ok. {len(items)} target(s). No driver was installed.")
                else:
                    status.set_text("Catalog check: fail. " + "; ".join(errors))

            def on_copy(_button):
                item = selected_item()
                if item is None:
                    status.set_text("Select a card before copying its vendor page.")
                    return
                from gi.repository import Gdk

                window.get_clipboard().set_content(Gdk.ContentProvider.new_for_value(item["source"]))
                status.set_text("Vendor page copied. Open it yourself, inside the VM only.")

            def toggle(_button):
                enabled = allowed.get_active()
                for widget in (search, listing, check_button, copy_button):
                    widget.set_sensitive(enabled)
                status.set_text("Tools unlocked. This still does not install a driver." if enabled else "Confirm the virtual machine, then pick a card.")

            search.connect("changed", lambda *_a: refill())
            listing.connect("row-selected", on_select)
            check_button.connect("clicked", on_check)
            copy_button.connect("clicked", on_copy)
            allowed.connect("toggled", toggle)
            refill()
            toggle(allowed)
            window.present()
            if os.environ.get("DRIVER_CONTROL_TOOLS_SMOKE") == "1":
                from gi.repository import GLib

                def smoke():
                    allowed.set_active(True)
                    row = listing.get_row_at_index(0)
                    listing.select_row(row)
                    check_button.emit("clicked")
                    checked = status.get_text()
                    copy_button.emit("clicked")
                    copied = status.get_text()
                    print(f"SMOKE check={checked}", flush=True)
                    print(f"SMOKE copy={copied}", flush=True)
                    print(f"SMOKE detail={detail.get_text().splitlines()[0]}", flush=True)
                    if "Catalog check: ok" not in checked:
                        print("SMOKE_FAIL check", flush=True)
                    self.quit()
                    return False

                GLib.idle_add(smoke)

    app = ToolsApp(application_id=APP_ID)
    return app.run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
