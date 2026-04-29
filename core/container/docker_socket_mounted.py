from core.utils.docker_client import get_running_containers_info

def run_check():
    """5.32 Ensure that the Docker socket is not mounted inside any containers"""
    containers = get_running_containers_info()
    if not containers:
        return {"Control_ID": "5.32", "Status": "PASS","Description": "Ensure that the Docker socket is not mounted inside any containers", "Details": "No running containers"}
        
    failed_containers = []
    for c in containers:
        mounts = c.get("Mounts", [])
        for mount in mounts:
            if "docker.sock" in mount.get("Source", "") or "docker.sock" in mount.get("Destination", ""):
                failed_containers.append(c.get("Name", "").lstrip('/'))
                break
                
    return {
        "Control_ID": "5.32",
        "Description": "Ensure that the Docker socket is not mounted inside any containers",
        "Status": "FAIL" if failed_containers else "PASS",
        "Details": f"Containers mounting docker.sock: {', '.join(failed_containers)}" if failed_containers else "No containers mounting the Docker socket."
    }