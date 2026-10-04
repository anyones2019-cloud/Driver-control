# Testing

Public volunteer testers are asked to:

1. Use a Linux virtual machine only. Fedora is the target. Flatpak is the intended install path.
2. Run `python3 scripts/check-catalog.py`. It must print `ok`.
3. Pick an old GPU family from drivers/old-gpu-catalog.json.
4. The catalog GUI is `python3 gui/driver_gui.py`. It does not install a driver. On Fedora it needs `python3-tkinter`. The Flatpak build is in packaging/flatpak/FLATPAK.md. After a card is picked, `python3 scripts/driver_link.py` should print the same open-source driver and must refuse `--install`.
5. Report distro, VM software, catalog check result, and pass or fail. GUI bugs use https://github.com/anyones2019-cloud/Driver-control/issues/new?template=gui_bug_report.yml

Do not test on a main hardware machine.

Virus scanning is enabled on commits. Every push and pull request is scanned. If the scan is clean, the commit is allowed and stays on main. Only an infected commit is moved to quarantine.
