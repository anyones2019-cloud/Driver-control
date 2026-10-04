# Testing

Public volunteer testers are asked to:

1. Use a Linux virtual machine only. Fedora is the target. Flatpak is the intended install path.
2. Run `python3 scripts/check-catalog.py`. It must print `ok`.
3. Pick an old GPU family from drivers/old-gpu-catalog.json.
4. There is no installer program in this repo yet. Do not expect a GUI to launch.
5. Report distro, VM software, catalog check result, and pass or fail on the GitHub issue.

Do not test on a main hardware machine.
