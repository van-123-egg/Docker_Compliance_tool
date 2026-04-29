import os
try:
    import pwd
    import grp
except ImportError:
    pwd = None
    grp = None

def run_check():
    """3.15 Ensure that the Docker socket file ownership is set to root:docker"""
    path = "/var/run/docker.sock"
    if not os.path.exists(path):
        return {"Control_ID": "3.15","Description": "Ensure that the Docker socket file ownership is set to root:docker",  "Status": "N/A", "Details": "Socket not found"}
        
    if pwd is None or grp is None:
        return {"Control_ID": "3.15","Description": "Ensure that the Docker socket file ownership is set to root:docker",  "Status": "N/A", "Details": "pwd/grp modules not available on this OS (Windows)"}
        
    stat = os.stat(path)
    owner = pwd.getpwuid(stat.st_uid).pw_name
    group = grp.getgrgid(stat.st_gid).gr_name
    
    status = "PASS" if owner == "root" and group == "docker" else "FAIL"
    return {
        "Control_ID": "3.15",
        "Description": "Ensure that the Docker socket file ownership is set to root:docker",
        "Status": status,
        "Details": f"Owner: {owner}, Group: {group}"
    }