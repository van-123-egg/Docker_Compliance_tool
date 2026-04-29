import subprocess
import os

def run_check():
    """1.1.2 Ensure only trusted users are allowed to control Docker daemon"""
    try:
        if os.name == 'nt':
            output = subprocess.check_output(["net", "localgroup", "docker-users"]).decode("utf-8")
            users = []
            capture = False
            for line in output.splitlines():
                if "-------------------------------------------------------------------------------" in line:
                    capture = True
                    continue
                if capture and line.strip() and not line.startswith("The command completed successfully"):
                    users.append(line.strip())
        else:
            # Get members of the docker group
            output = subprocess.check_output(["getent", "group", "docker"]).decode("utf-8")
            users_str = output.strip().split(":")[-1]
            users = [u for u in users_str.split(",") if u]
            
        return {
            "Control_ID": "1.1.2",
            "Description": "Ensure only trusted users are allowed to control Docker daemon",
            "Status": "MANUAL_REVIEW", # Requires a human to verify if these users are authorized
            "Details": f"Users in docker group: {', '.join(users) if users else 'None'}"
        }
    except Exception as e:
        return {"Control_ID": "1.1.2","Description": "Ensure only trusted users are allowed to control Docker daemon",  "Status": "ERROR", "Details": str(e)}