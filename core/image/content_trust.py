import os


def run_check():
    """4.5 Ensure Content Trust for Docker is enabled — Docker Content Trust (DCT)
    uses digital signatures to verify image integrity and publisher identity.
    Without it, tampered images can be pulled and run."""
    try:
        dct_value = os.environ.get("DOCKER_CONTENT_TRUST", "")

        if dct_value == "1":
            status = "PASS"
            details = "DOCKER_CONTENT_TRUST is enabled (set to '1')."
        elif dct_value:
            status = "FAIL"
            details = f"DOCKER_CONTENT_TRUST is set to '{dct_value}' — must be '1' to enforce signing."
        else:
            status = "FAIL"
            details = "DOCKER_CONTENT_TRUST is not set. Image pulls are not signature-verified."

        return {
            "Control_ID": "IMG-03",
            "Description": "Ensure Content Trust for Docker is enabled",
            "Status": status,
            "Details": details
        }
    except Exception as e:
        return {
            "Control_ID": "IMG-03",
            "Description": "Ensure Content Trust for Docker is enabled",
            "Status": "ERROR",
            "Details": str(e)
        }
