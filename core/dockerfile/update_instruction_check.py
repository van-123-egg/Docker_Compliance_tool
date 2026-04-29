"""DL-07: Ensure update instructions are not used alone."""

import re
from core.dockerfile.parser import parse_dockerfile

def run_check():
    """Ensure update instructions (e.g., apt-get update) are not used alone in a RUN statement.
    Using them alone caches the update step, leading to outdated packages later."""
    instructions = parse_dockerfile()
    if instructions is None:
        return {
            "Control_ID": "DL-07",
            "Description": "Ensure update instructions are not used alone",
            "Status": "N/A",
            "Details": "No target image configured."
        }

    run_instructions = [i for i in instructions if i["instruction"] == "RUN"]
    if not run_instructions:
        return {
            "Control_ID": "DL-07",
            "Description": "Ensure update instructions are not used alone",
            "Status": "PASS",
            "Details": "No RUN instructions found."
        }

    flagged = []
    for inst in run_instructions:
        args = inst["arguments"]
        
        # Check for apt-get update without apt-get install
        if re.search(r'apt-get\s+update', args) and not re.search(r'apt-get\s+(install|upgrade)', args):
            flagged.append(f"Line {inst['line']}: apt-get update used without install/upgrade")
            
        # Check for apk update without apk add
        if re.search(r'apk\s+update', args) and not re.search(r'apk\s+(add|upgrade)', args):
             flagged.append(f"Line {inst['line']}: apk update used without add/upgrade")

    return {
        "Control_ID": "DL-07",
        "Description": "Ensure update instructions are not used alone",
        "Status": "WARN" if flagged else "PASS",
        "Details": f"Isolated update commands found: {'; '.join(flagged)}" if flagged else "No isolated update instructions found."
    }
