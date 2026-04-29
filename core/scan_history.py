"""
Automatic scan history manager.
Saves every scan result to ~/.docker-compliance/scans/ with timestamps.
"""

import json
import os
import platform
from datetime import datetime
from pathlib import Path


def _get_history_dir():
    """Get the scan history directory path."""
    home = Path.home()
    history_dir = home / ".docker-compliance" / "scans"
    history_dir.mkdir(parents=True, exist_ok=True)
    return history_dir


def save_scan(report_data, score_info):
    """Save a scan result to the history directory.
    
    Returns the path to the saved file.
    """
    history_dir = _get_history_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"scan_{timestamp}.json"
    filepath = history_dir / filename

    scan_record = {
        "timestamp": score_info["timestamp"],
        "hostname": platform.node(),
        "score_pct": score_info["score_pct"],
        "passed": score_info["passed"],
        "failed": score_info["failed"],
        "warned": score_info["warned"],
        "na": score_info["na"],
        "errors": score_info["errors"],
        "severity_fails": score_info["severity_fails"],
        "results": report_data,
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(scan_record, f, indent=2)

    return str(filepath)


def get_all_scans():
    """Get a list of all saved scans, sorted by timestamp (newest first).
    
    Returns a list of dicts with: filename, filepath, timestamp, score_pct
    """
    history_dir = _get_history_dir()
    scans = []

    for f in sorted(history_dir.glob("scan_*.json"), reverse=True):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            scans.append({
                "filename": f.name,
                "filepath": str(f),
                "timestamp": data.get("timestamp", "Unknown"),
                "score_pct": data.get("score_pct", 0),
                "passed": data.get("passed", 0),
                "failed": data.get("failed", 0),
                "hostname": data.get("hostname", "Unknown"),
            })
        except (json.JSONDecodeError, IOError):
            continue

    return scans


def get_latest_scan():
    """Get the most recent saved scan, or None if no scans exist."""
    scans = get_all_scans()
    if not scans:
        return None
    
    filepath = scans[0]["filepath"]
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_scan_by_file(filepath):
    """Load a scan from a specific file path."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def print_history():
    """Print a formatted table of all saved scans."""
    scans = get_all_scans()

    if not scans:
        print("\n  No scan history found. Run a scan first.\n")
        return

    try:
        from tabulate import tabulate
        headers = ["#", "Timestamp", "Score", "Passed", "Failed", "Host"]
        rows = []
        for i, s in enumerate(scans, 1):
            rows.append([
                i,
                s["timestamp"],
                f"{s['score_pct']}%",
                s["passed"],
                s["failed"],
                s["hostname"],
            ])
        print(f"\n  Scan History ({len(scans)} scans found in ~/.docker-compliance/scans/)\n")
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        print()
    except ImportError:
        print(f"\n  Scan History ({len(scans)} scans):\n")
        for i, s in enumerate(scans, 1):
            print(f"  {i}. [{s['timestamp']}] Score: {s['score_pct']}% | "
                  f"Pass: {s['passed']} Fail: {s['failed']} | {s['hostname']}")
        print()
