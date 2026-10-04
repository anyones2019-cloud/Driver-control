# Testing

Public volunteer testers are asked to:

1. Use a Linux virtual machine only. Fedora is the target. Flatpak is the intended install path.
2. Run `python3 scripts/check-catalog.py`. It must print `ok`.
3. Pick an old GPU family from drivers/old-gpu-catalog.json.
4. The catalog GUI is `python3 gui/driver_gui.py`. It does not install a driver. On Fedora it needs `python3-tkinter`.
5. Report distro, VM software, catalog check result, and pass or fail on the GitHub issue.

Do not test on a main hardware machine.

Virus scanning is enabled on commits. Every push and pull request is scanned. If the scan is clean, the commit is allowed and stays on main. Only an infected commit is moved to quarantine.
