#!/usr/bin/env python3
"""Linux check for the old GPU catalog."""
import json
import sys
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "drivers" / "old-gpu-catalog.json"
data = json.loads(path.read_text(encoding="utf-8"))
errors = []
if data.get("test_rule") != "Linux VM only. Do not install on a main machine.":
    errors.append("missing VM-only rule")
vendors = data.get("vendors")
if not isinstance(vendors, list) or not vendors:
    errors.append("vendors missing")
else:
    for vendor in vendors:
        if not vendor.get("vendor") or not vendor.get("branches"):
            errors.append("vendor entry incomplete")
        for branch in vendor.get("branches", []):
            if not branch.get("branch") or not branch.get("cards") or not branch.get("source"):
                errors.append("branch entry incomplete")
if errors:
    print("fail")
    for error in errors:
        print(error)
    sys.exit(1)
print("ok")
print(f"vendors={len(vendors)}")
