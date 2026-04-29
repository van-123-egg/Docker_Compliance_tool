import os

def run_check():
    """3.4 Ensure that docker.socket file permissions are set to 644 or more restrictive"""
    path = "/usr/lib/systemd/system/docker.socket"
    if not os.path.exists(path):
        return {"Control_ID": "3.4","Description": "Ensure that docker.socket file permissions are set to 644 or more restrictive",  "Status": "N/A", "Details": "File not found"}
        
    stat = os.stat(path)
    perms = oct(stat.st_mode)[-3:]
    
    status = "PASS" if int(perms, 8) <= 0o644 else "FAIL"
    return {
        "Control_ID": "3.4",
        "Description": "Ensure that docker.socket file permissions are set to 644 or more restrictive",
        "Status": status,
        "Details": f"Permissions: {perms}"
    }