"""DL-01: Ensure FROM does not use :latest tag."""

from core.dockerfile.parser import parse_dockerfile


def run_check():
    """DL-01 is N/A because docker history does not expose FROM instructions."""
    return {
        "Control_ID": "DL-01",
        "Description": "Ensure FROM does not use :latest tag",
        "Status": "N/A",
        "Details": "FROM instructions are not preserved in image history. See Image Security checks (IMG-01) for tag validation."
    }


