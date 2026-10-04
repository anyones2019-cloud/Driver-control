# Bugs found 2026-10-04

Checked on Linux. No installer program exists, so driver install was not run.

- Fixed: TESTING.md told testers to run a program and also said there is nothing to run.
- Fixed: added scripts/check-catalog.py so the catalog can be validated on Linux.
- Open: README says MIT. The LICENSE file and GitHub license detection are AGPL-3.0. Not changed.
- Open: .gitignore is a Jekyll template and does not match this project. Not changed.
- Open: proprietary GPU packages are not in the repo, so they cannot be install-tested here.
