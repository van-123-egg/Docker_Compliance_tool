from datetime import datetime, timezone
from core.utils.docker_client import get_all_images_info


# Images older than this many days are flagged
STALENESS_THRESHOLD_DAYS = 90


def run_check():
    """Ensure Docker images are not outdated — stale images may contain
    unpatched vulnerabilities from their base OS or language runtime."""
    try:
        images = get_all_images_info()
        if not images:
            return {
                "Control_ID": "IMG-02",
                "Description": "Ensure Docker images are not outdated",
                "Status": "PASS",
                "Details": "No local images found."
            }

        now = datetime.now(timezone.utc)
        flagged = []

        for img in images:
            created_str = img.get("Created", "")
            repo_tags = img.get("RepoTags", []) or ["<untagged>"]
            image_name = repo_tags[0]

            if not created_str:
                continue

            try:
                # Docker timestamps are ISO 8601 with nanoseconds — truncate to microseconds
                # Example: "2024-01-15T10:30:00.123456789Z"
                clean_ts = created_str.split(".")[0] + "+00:00"
                created_dt = datetime.fromisoformat(clean_ts)
                age_days = (now - created_dt).days

                if age_days > STALENESS_THRESHOLD_DAYS:
                    flagged.append(f"{image_name} ({age_days}d old)")
            except (ValueError, TypeError):
                continue

        return {
            "Control_ID": "IMG-02",
            "Description": "Ensure Docker images are not outdated",
            "Status": "FAIL" if flagged else "PASS",
            "Details": f"Stale images (>{STALENESS_THRESHOLD_DAYS}d): {', '.join(flagged)}" if flagged else f"All images are within {STALENESS_THRESHOLD_DAYS}-day freshness window."
        }
    except Exception as e:
        return {
            "Control_ID": "IMG-02",
            "Description": "Ensure Docker images are not outdated",
            "Status": "ERROR",
            "Details": str(e)
        }
