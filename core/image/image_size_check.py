from core.utils.docker_client import get_all_images_info


# Images above this size (in bytes) are flagged — 1 GB default
SIZE_THRESHOLD_BYTES = 1 * 1024 * 1024 * 1024


def _format_size(size_bytes):
    """Convert bytes to a human-readable string."""
    if size_bytes >= 1024 ** 3:
        return f"{size_bytes / (1024 ** 3):.2f} GB"
    elif size_bytes >= 1024 ** 2:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / 1024:.0f} KB"


def run_check():
    """Ensure Docker images are not excessively large — bloated images often
    contain unnecessary packages, build tools, or debug utilities that widen
    the attack surface and slow deployments."""
    try:
        images = get_all_images_info()
        if not images:
            return {
                "Control_ID": "IMG-05",
                "Description": "Ensure Docker images are not excessively large",
                "Status": "PASS",
                "Details": "No local images found."
            }

        flagged = []
        for img in images:
            size = img.get("Size", 0)
            repo_tags = img.get("RepoTags", []) or ["<untagged>"]
            image_name = repo_tags[0]

            if size > SIZE_THRESHOLD_BYTES:
                flagged.append(f"{image_name} ({_format_size(size)})")

        threshold_str = _format_size(SIZE_THRESHOLD_BYTES)

        return {
            "Control_ID": "IMG-05",
            "Description": "Ensure Docker images are not excessively large",
            "Status": "WARN" if flagged else "PASS",
            "Details": f"Images exceeding {threshold_str}: {', '.join(flagged)}" if flagged else f"All images are under {threshold_str}."
        }
    except Exception as e:
        return {
            "Control_ID": "IMG-05",
            "Description": "Ensure Docker images are not excessively large",
            "Status": "ERROR",
            "Details": str(e)
        }
