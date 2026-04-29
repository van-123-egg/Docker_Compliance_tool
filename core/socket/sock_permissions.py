import os

def run_check():
    """3.16 Ensure that the Docker socket file permissions are set to 660 or more restrictively"""
    path = "/var/run/docker.sock"
    if not os.path.exists(path):
        return {"Control_ID": "3.16","Description": "Ensure that the Docker socket file permissions are set to 660 or more restrictively",  "Status": "N/A", "Details": "Socket not found"}
        
    stat = os.stat(path)
    perms = oct(stat.st_mode)[-3:]
    
    status = "PASS" if int(perms, 8) <= 0o660 else "FAIL"
    return {
        "Control_ID": "3.16",
        "Description": "Ensure that the Docker socket file permissions are set to 660 or more restrictively",
        "Status": status,
        "Details": f"Permissions: {perms}"
    }