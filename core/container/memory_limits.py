from core.utils.docker_client import get_running_containers_info

def run_check():
    """5.11 Ensure that the memory usage for containers is limited"""
    containers = get_running_containers_info()
    if not containers:
        return {"Control_ID": "5.11", "Status": "PASS","Description": "Ensure that the memory usage for containers is limited", "Details": "No running containers"}
        
    failed_containers = []
    for c in containers:
        if c.get("HostConfig", {}).get("Memory", 0) == 0:
            failed_containers.append(c.get("Name", "").lstrip('/'))
            
    return {
        "Control_ID": "5.11",
        "Description": "Ensure that the memory usage for containers is limited",
        "Status": "FAIL" if failed_containers else "PASS",
        "Details": f"Containers without memory limits: {', '.join(failed_containers)}" if failed_containers else "All containers have memory limits."
    }