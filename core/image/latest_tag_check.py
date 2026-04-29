from core.utils.docker_client import get_image_list


def run_check():
    """4.7 Ensure images are not tagged with 'latest' — using :latest breaks
    reproducibility and makes it impossible to audit which exact version is deployed."""
    try:
        images = get_image_list()
        if not images:
            return {
                "Control_ID": "IMG-01",
                "Description": "Ensure images are not tagged with 'latest'",
                "Status": "PASS",
                "Details": "No local images found."
            }

        flagged = []
        for img in images:
            repo = img.get("Repository", "<none>")
            tag = img.get("Tag", "<none>")

            # Skip intermediate / dangling images (handled by dangling_images check)
            if repo == "<none>":
                continue

            if tag in ["latest", "<none>"]:
                flagged.append(f"{repo}:{tag}")

        return {
            "Control_ID": "IMG-01",
            "Description": "Ensure images are not tagged with 'latest'",
            "Status": "FAIL" if flagged else "PASS",
            "Details": f"Images using latest/untagged: {', '.join(flagged)}" if flagged else "All images use specific version tags."
        }
    except Exception as e:
        return {
            "Control_ID": "IMG-01",
            "Description": "Ensure images are not tagged with 'latest'",
            "Status": "ERROR",
            "Details": str(e)
        }
