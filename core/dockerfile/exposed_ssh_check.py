"""DL-04: Ensure SSH port 22 is not exposed."""

from core.dockerfile.parser import parse_dockerfile


def run_check():
    """Flag EXPOSE instructions that include port 22 (SSH).
    SSH should not be running inside containers."""
    instructions = parse_dockerfile()
    if instructions is None:
        return {
            "Control_ID": "DL-04",
            "Description": "Ensure SSH port 22 is not exposed",
            "Status": "N/A",
            "Details": "No target image configured."
        }

    expose_instructions = [i for i in instructions if i["instruction"] == "EXPOSE"]
    if not expose_instructions:
        return {
            "Control_ID": "DL-04",
            "Description": "Ensure SSH port 22 is not exposed",
            "Status": "PASS",
            "Details": "No EXPOSE instructions found."
        }

    flagged = []
    for inst in expose_instructions:
        ports = inst["arguments"].split()
        for port in ports:
            # Handle port/protocol format like 22/tcp
            port_num = port.split("/")[0].strip()
            if port_num == "22":
                flagged.append(f"Line {inst['line']}: EXPOSE {port}")

    return {
        "Control_ID": "DL-04",
        "Description": "Ensure SSH port 22 is not exposed",
        "Status": "FAIL" if flagged else "PASS",
        "Details": (
            f"SSH port exposed: {'; '.join(flagged)}. Do not run SSH inside containers."
            if flagged
            else "Port 22 is not exposed."
        )
    }
