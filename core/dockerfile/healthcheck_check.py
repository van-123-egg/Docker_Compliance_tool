"""DL-06: Ensure HEALTHCHECK instructions have been added to container images."""

from core.dockerfile.parser import parse_dockerfile

def run_check():
    """Ensure HEALTHCHECK instructions have been added to container images."""
    instructions = parse_dockerfile()
    if instructions is None:
        return {
            "Control_ID": "DL-06",
            "Description": "Ensure HEALTHCHECK instructions have been added to container images",
            "Status": "N/A",
            "Details": "No target image configured."
        }

    healthcheck_instructions = [i for i in instructions if i["instruction"] == "HEALTHCHECK"]
    
    if not healthcheck_instructions:
        return {
            "Control_ID": "DL-06",
            "Description": "Ensure HEALTHCHECK instructions have been added to container images",
            "Status": "FAIL",
            "Details": "No HEALTHCHECK instruction found."
        }
        
    last_healthcheck = healthcheck_instructions[-1]
    if last_healthcheck["arguments"].strip() == "NONE":
         return {
            "Control_ID": "DL-06",
            "Description": "Ensure HEALTHCHECK instructions have been added to container images",
            "Status": "FAIL",
            "Details": f"Line {last_healthcheck['line']}: HEALTHCHECK is set to NONE."
        }

    return {
        "Control_ID": "DL-06",
        "Description": "Ensure HEALTHCHECK instructions have been added to container images",
        "Status": "PASS",
        "Details": f"HEALTHCHECK instruction found (line {last_healthcheck['line']})."
    }
