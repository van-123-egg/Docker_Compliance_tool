from core.utils.docker_client import get_running_containers_info

def run_check():
    """5.10 Ensure that the host's network namespace is not shared"""
    containers = get_running_containers_info()
    if not containers:
        return {"Control_ID": "5.10", "Status": "PASS","Description": "Ensure that the host's network namespace is not shared", "Details": "No running containers"}
        
    failed_containers = []
    for c in containers:
        if c.get("HostConfig", {}).get("NetworkMode") == "host":
            failed_containers.append(c.get("Name", "").lstrip('/'))
            
    return {
        "Control_ID": "5.10",
        "Description": "Ensure that the host's network namespace is not shared",
        "Status": "FAIL" if failed_containers else "PASS",
        "Details": f"Containers using host network: {', '.join(failed_containers)}" if failed_containers else "No containers sharing host network."
    }