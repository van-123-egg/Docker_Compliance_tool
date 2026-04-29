"""DL-08: Ensure secrets are not stored in Dockerfile ENV instructions."""

import re
from core.dockerfile.parser import parse_dockerfile

def run_check():
    """Ensure secrets (passwords, keys, tokens) are not stored in ENV instructions, 
    which are visible via docker inspect."""
    instructions = parse_dockerfile()
    if instructions is None:
        return {
            "Control_ID": "DL-08",
            "Description": "Ensure secrets are not stored in Dockerfile ENV instructions",
            "Status": "N/A",
            "Details": "No target image configured."
        }

    env_instructions = [i for i in instructions if i["instruction"] == "ENV"]
    if not env_instructions:
        return {
            "Control_ID": "DL-08",
            "Description": "Ensure secrets are not stored in Dockerfile ENV instructions",
            "Status": "PASS",
            "Details": "No ENV instructions found."
        }

    secret_keywords = [
        "PASSWORD", "PASSWD", "PWD", "SECRET", "TOKEN", "KEY", "AUTH", "CREDENTIAL", "CERT"
    ]
    
    flagged = []
    for inst in env_instructions:
        args = inst["arguments"].upper()
        # Look for secret keywords in the ENV assignments
        for keyword in secret_keywords:
            if re.search(rf'\b{keyword}\b\s*=', args) or re.search(rf'\b{keyword}\s+', args):
                flagged.append(f"Line {inst['line']}: ENV instruction contains potential secret '{keyword}'")
                break

    return {
        "Control_ID": "DL-08",
        "Description": "Ensure secrets are not stored in Dockerfile ENV instructions",
        "Status": "WARN" if flagged else "PASS",
        "Details": f"Potential secrets found in ENV: {'; '.join(flagged)}. Use Docker secrets instead." if flagged else "No secrets found in ENV instructions."
    }
