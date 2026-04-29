import os
try:
    import pwd
    import grp
except ImportError:
    pwd = None
    grp = None

def run_check():
    """3.3 Ensure that docker.socket file ownership is set to root:root"""
    path = "/usr/lib/systemd/system/docker.socket"
    if not os.path.exists(path):
        return {"Control_ID": "3.3","Description": "Ensure that docker.socket file ownership is set to root:root",  "Status": "N/A", "Details": "File not found"}
        
    if pwd is None or grp is None:
        return {"Control_ID": "3.3","Description": "Ensure that docker.socket file ownership is set to root:root",  "Status": "N/A", "Details": "pwd/grp modules not available on this OS (Windows)"}
        
    stat = os.stat(path)
    owner = pwd.getpwuid(stat.st_uid).pw_name
    group = grp.getgrgid(stat.st_gid).gr_name
    
    status = "PASS" if owner == "root" and group == "root" else "FAIL"
    return {
        "Control_ID": "3.3",
        "Description": "Ensure that docker.socket file ownership is set to root:root",
        "Status": status,
        "Details": f"Owner: {owner}, Group: {group}"
    }