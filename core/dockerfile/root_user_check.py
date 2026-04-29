"""DL-02: Ensure a non-root USER is specified."""

from core.dockerfile.parser import parse_dockerfile


def run_check():
    """Ensure the Dockerfile specifies a non-root USER before the final CMD/ENTRYPOINT."""
    instructions = parse_dockerfile()
    if instructions is None:
        return {
            "Control_ID": "DL-02",
            "Description": "Ensure a non-root USER is specified",
            "Status": "N/A",
            "Details": "No target image configured."
        }

    user_instructions = [i for i in instructions if i["instruction"] == "USER"]
    
    if not user_instructions:
        return {
            "Control_ID": "DL-02",
            "Description": "Ensure a non-root USER is specified",
            "Status": "FAIL",
            "Details": "No USER instruction found. Container will run as root by default."
        }

    # Check the last USER instruction
    last_user = user_instructions[-1]
    user_value = last_user["arguments"].strip().split(":")[0]  # Handle USER user:group

    if user_value in ("root", "0", ""):
        return {
            "Control_ID": "DL-02",
            "Description": "Ensure a non-root USER is specified",
            "Status": "FAIL",
            "Details": f"Line {last_user['line']}: USER is set to '{user_value}' (root). Use a non-root user."
        }

    return {
        "Control_ID": "DL-02",
        "Description": "Ensure a non-root USER is specified",
        "Status": "PASS",
        "Details": f"Non-root USER '{user_value}' is set (line {last_user['line']})."
    }
