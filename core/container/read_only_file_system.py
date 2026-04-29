from core.utils.docker_client import get_running_containers_info

def run_check():
    """5.13 Ensure that the container's root filesystem is mounted as read only"""
    containers = get_running_containers_info()
    if not containers:
        return {"Control_ID": "5.13", "Status": "PASS","Description": "Ensure that the container's root filesystem is mounted as read only", "Details": "No running containers"}
        
    failed_containers = []
    for c in containers:
        if not c.get("HostConfig", {}).get("ReadonlyRootfs", False):
            failed_containers.append(c.get("Name", "").lstrip('/'))
            
    return {
        "Control_ID": "5.13",
        "Description": "Ensure that the container's root filesystem is mounted as read only",
        "Status": "FAIL" if failed_containers else "PASS",
        "Details": f"Containers with writable rootfs: {', '.join(failed_containers)}" if failed_containers else "All containers have read-only rootfs."
    }