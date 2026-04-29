import subprocess


def run_check():
    """Ensure there are no dangling (untagged) Docker images — dangling images
    are leftover layers that waste disk, may contain sensitive data, and increase
    the attack surface."""
    try:
        cmd = ["docker", "images", "-f", "dangling=true", "-q"]
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8").strip()

        if not output:
            return {
                "Control_ID": "IMG-04",
                "Description": "Ensure there are no dangling images",
                "Status": "PASS",
                "Details": "No dangling images found."
            }

        dangling_ids = [img_id for img_id in output.splitlines() if img_id.strip()]
        count = len(dangling_ids)

        return {
            "Control_ID": "IMG-04",
            "Description": "Ensure there are no dangling images",
            "Status": "WARN",
            "Details": f"{count} dangling image(s) found. Run 'docker image prune' to clean up."
        }
    except subprocess.CalledProcessError:
        return {
            "Control_ID": "IMG-04",
            "Description": "Ensure there are no dangling images",
            "Status": "N/A",
            "Details": "Docker daemon is not reachable. Cannot check for dangling images."
        }
    except Exception as e:
        return {
            "Control_ID": "IMG-04",
            "Description": "Ensure there are no dangling images",
            "Status": "ERROR",
            "Details": str(e)
        }
