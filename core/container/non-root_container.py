from core.utils.docker_client import get_running_containers_info

def run_check():
    """4.1 Ensure that a user for the container has been created"""
    containers = get_running_containers_info()
    if not containers:
        return {"Control_ID": "4.1", "Status": "PASS","Description": "Ensure that a user for the container has been created (Non-root)", "Details": "No running containers"}
        
    failed_containers = []
    for c in containers:
        user = c.get("Config", {}).get("User", "")
        if user in ["", "0", "root"]:
            failed_containers.append(c.get("Name", "").lstrip('/'))
            
    return {
        "Control_ID": "4.1",
        "Description": "Ensure that a user for the container has been created (Non-root)",
        "Status": "FAIL" if failed_containers else "PASS",
        "Details": f"Running as root: {', '.join(failed_containers)}" if failed_containers else "All containers run as non-root."
    }