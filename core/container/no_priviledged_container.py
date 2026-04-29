from core.utils.docker_client import get_running_containers_info

def run_check():
    """5.5 Ensure that privileged containers are not used"""
    containers = get_running_containers_info()
    if not containers:
        return {"Control_ID": "5.5", "Status": "PASS","Description": "Ensure that privileged containers are not used", "Details": "No running containers"}
        
    failed_containers = []
    for c in containers:
        if c.get("HostConfig", {}).get("Privileged", False):
            failed_containers.append(c.get("Name", "").lstrip('/'))
            
    return {
        "Control_ID": "5.5",
        "Description": "Ensure that privileged containers are not used",
        "Status": "FAIL" if failed_containers else "PASS",
        "Details": f"Privileged containers: {', '.join(failed_containers)}" if failed_containers else "No privileged containers found."
    }