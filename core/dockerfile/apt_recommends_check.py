"""DL-05: Ensure apt-get uses --no-install-recommends."""

import re
from core.dockerfile.parser import parse_dockerfile


def run_check():
    """Flag apt-get install commands that don't use --no-install-recommends,
    which pulls unnecessary packages and increases attack surface."""
    instructions = parse_dockerfile()
    if instructions is None:
        return {
            "Control_ID": "DL-05",
            "Description": "Ensure apt-get uses --no-install-recommends",
            "Status": "N/A",
            "Details": "No Dockerfile configured. Use --dockerfile-path."
        }

    run_instructions = [i for i in instructions if i["instruction"] == "RUN"]
    if not run_instructions:
        return {
            "Control_ID": "DL-05",
            "Description": "Ensure apt-get uses --no-install-recommends",
            "Status": "PASS",
            "Details": "No RUN instructions found."
        }

    flagged = []
    for inst in run_instructions:
        args = inst["arguments"]
        # Look for apt-get install without --no-install-recommends
        if re.search(r'apt-get\s+install', args):
            if '--no-install-recommends' not in args:
                flagged.append(f"Line {inst['line']}: apt-get install without --no-install-recommends")

    if not flagged:
        # Check if any apt-get install exists at all
        has_apt = any(re.search(r'apt-get\s+install', i["arguments"]) for i in run_instructions)
        if not has_apt:
            detail = "No apt-get install commands found."
        else:
            detail = "All apt-get install commands use --no-install-recommends."
    else:
        detail = f"Missing --no-install-recommends: {'; '.join(flagged)}"

    return {
        "Control_ID": "DL-05",
        "Description": "Ensure apt-get uses --no-install-recommends",
        "Status": "WARN" if flagged else "PASS",
        "Details": detail
    }
