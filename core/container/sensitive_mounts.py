from core.utils.docker_client import get_running_containers_info

def run_check():
    """5.6 Ensure sensitive host system directories are not mounted on containers"""
    sensitive_dirs = ['/', '/boot', '/dev', '/etc', '/lib', '/lib64', '/proc', '/sys', '/usr']
    containers = get_running_containers_info()
    if not containers:
        return {"Control_ID": "5.6", "Status": "PASS","Description": "Ensure sensitive host system directories are not mounted", "Details": "No running containers"}
        
    failed_containers = {}
    for c in containers:
        mounts = c.get("Mounts", [])
        bad_mounts = [m.get("Source") for m in mounts if m.get("Source") in sensitive_dirs]
        if bad_mounts:
            failed_containers[c.get("Name", "").lstrip('/')] = bad_mounts
            
    return {
        "Control_ID": "5.6",
        "Description": "Ensure sensitive host system directories are not mounted",
        "Status": "FAIL" if failed_containers else "PASS",
        "Details": f"Violations: {failed_containers}" if failed_containers else "No sensitive mounts found."
    }