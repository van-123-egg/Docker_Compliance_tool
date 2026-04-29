"""
Diff engine for comparing two scan results.
Shows what improved, regressed, and changed between scans.
"""

import json

try:
    from tabulate import tabulate
except ImportError:
    tabulate = None


def _flatten_results(scan_data):
    """Flatten a scan's results into a dict keyed by Control_ID."""
    results_dict = {}
    # Handle both direct report data and saved scan format
    report = scan_data.get("results", scan_data)

    for section, checks in report.items():
        if not isinstance(checks, list):
            continue
        for check in checks:
            control_id = check.get("Control_ID")
            if control_id:
                results_dict[control_id] = {
                    "status": check.get("Status", "UNKNOWN"),
                    "description": check.get("Description", ""),
                    "severity": check.get("Severity", "INFO"),
                    "section": section,
                }
    return results_dict


def compare_scans(old_scan, new_scan):
    """Compare two scans and return categorized differences.
    
    Returns a dict with keys: fixed, regressed, new, removed, unchanged
    """
    old_results = _flatten_results(old_scan)
    new_results = _flatten_results(new_scan)

    old_ids = set(old_results.keys())
    new_ids = set(new_results.keys())

    fixed = []       # FAIL/WARN -> PASS
    regressed = []   # PASS -> FAIL/WARN
    new_checks = []  # Only in new scan
    removed = []     # Only in old scan
    unchanged = []   # Same status

    # Checks in both scans
    for cid in old_ids & new_ids:
        old_status = old_results[cid]["status"]
        new_status = new_results[cid]["status"]
        desc = new_results[cid]["description"]
        severity = new_results[cid]["severity"]

        if old_status == new_status:
            unchanged.append({"id": cid, "status": new_status, "desc": desc, "severity": severity})
        elif new_status == "PASS" and old_status in ("FAIL", "WARN", "ERROR"):
            fixed.append({"id": cid, "old": old_status, "new": new_status, "desc": desc, "severity": severity})
        elif old_status == "PASS" and new_status in ("FAIL", "WARN", "ERROR"):
            regressed.append({"id": cid, "old": old_status, "new": new_status, "desc": desc, "severity": severity})
        else:
            unchanged.append({"id": cid, "status": f"{old_status} -> {new_status}", "desc": desc, "severity": severity})

    # New checks
    for cid in new_ids - old_ids:
        new_checks.append({
            "id": cid,
            "status": new_results[cid]["status"],
            "desc": new_results[cid]["description"],
            "severity": new_results[cid]["severity"],
        })

    # Removed checks
    for cid in old_ids - new_ids:
        removed.append({
            "id": cid,
            "status": old_results[cid]["status"],
            "desc": old_results[cid]["description"],
            "severity": old_results[cid]["severity"],
        })

    return {
        "fixed": fixed,
        "regressed": regressed,
        "new": new_checks,
        "removed": removed,
        "unchanged": unchanged,
    }


def print_diff(old_scan, new_scan):
    """Print a formatted diff report between two scans."""
    diff = compare_scans(old_scan, new_scan)

    old_score = old_scan.get("score_pct", "?")
    new_score = new_scan.get("score_pct", "?")
    old_ts = old_scan.get("timestamp", "Unknown")
    new_ts = new_scan.get("timestamp", "Unknown")

    # Score change indicator
    if isinstance(old_score, (int, float)) and isinstance(new_score, (int, float)):
        delta = new_score - old_score
        if delta > 0:
            trend = f"(+{delta}%)  IMPROVED"
        elif delta < 0:
            trend = f"({delta}%)  REGRESSED"
        else:
            trend = "(no change)"
    else:
        trend = ""

    width = 58
    border = "=" * width
    divider = "-" * width

    print()
    print(f"  +{border}+")
    print(f"  |{'Compliance Trend':^{width}}|")
    print(f"  +{divider}+")
    print(f"  |{f'{old_ts}  ->  {new_ts}':^{width}}|")
    print(f"  |{f'Score: {old_score}% -> {new_score}%  {trend}':^{width}}|")
    print(f"  +{border}+")

    # Fixed
    if diff["fixed"]:
        print(f"\n  FIXED (FAIL -> PASS): {len(diff['fixed'])} check(s)")
        if tabulate:
            rows = [[f["id"], f["desc"][:50], f["severity"], f"{f['old']} -> {f['new']}"] for f in diff["fixed"]]
            print(tabulate(rows, headers=["Control", "Description", "Severity", "Change"], tablefmt="simple", stralign="left"))
        else:
            for f in diff["fixed"]:
                print(f"    + {f['id']}  {f['desc'][:50]}  ({f['old']} -> {f['new']})")

    # Regressed
    if diff["regressed"]:
        print(f"\n  REGRESSED (PASS -> FAIL): {len(diff['regressed'])} check(s)")
        if tabulate:
            rows = [[r["id"], r["desc"][:50], r["severity"], f"{r['old']} -> {r['new']}"] for r in diff["regressed"]]
            print(tabulate(rows, headers=["Control", "Description", "Severity", "Change"], tablefmt="simple", stralign="left"))
        else:
            for r in diff["regressed"]:
                print(f"    - {r['id']}  {r['desc'][:50]}  ({r['old']} -> {r['new']})")

    # New checks
    if diff["new"]:
        print(f"\n  NEW CHECKS: {len(diff['new'])} check(s) added")
        if tabulate:
            rows = [[n["id"], n["desc"][:50], n["severity"], n["status"]] for n in diff["new"]]
            print(tabulate(rows, headers=["Control", "Description", "Severity", "Status"], tablefmt="simple", stralign="left"))
        else:
            for n in diff["new"]:
                print(f"    * {n['id']}  {n['desc'][:50]}  [{n['status']}]")

    # Removed checks
    if diff["removed"]:
        print(f"\n  REMOVED CHECKS: {len(diff['removed'])} check(s) removed")
        for r in diff["removed"]:
            print(f"    x {r['id']}  {r['desc'][:50]}")

    # Summary
    if not diff["fixed"] and not diff["regressed"] and not diff["new"] and not diff["removed"]:
        print("\n  No changes detected between the two scans.")

    print(f"\n  Unchanged: {len(diff['unchanged'])} check(s)\n")
