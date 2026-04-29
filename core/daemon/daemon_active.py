import subprocess
import os

def run_check():
    """Ensure Docker daemon is actively running"""
    try:
        if os.name == 'nt':
            subprocess.check_output(["docker", "info"], stderr=subprocess.DEVNULL)
            status = "PASS"
            details = "Docker daemon is active and reachable"
        else:
            output = subprocess.check_output(["systemctl", "is-active", "docker"]).decode("utf-8").strip()
            status = "PASS" if output == "active" else "FAIL"
            details = f"Docker service is {output}"
            
        return {
            "Control_ID": "Daemon_Status",
            "Status": status,
            "Description": "Ensure Docker daemon is running",
            "Details": details
        }
    except FileNotFoundError:
        return {
            "Control_ID": "Daemon_Status", 
            "Status": "N/A", 
            "Description": "Ensure Docker daemon is running",
            "Details": "Docker executable not found in PATH."
        }
    except subprocess.CalledProcessError:
        return {
            "Control_ID": "Daemon_Status", 
            "Status": "FAIL", 
            "Description": "Ensure Docker daemon is running",
            "Details": "Docker daemon is not reachable."
        }
    except Exception as e:
        return {
            "Control_ID": "Daemon_Status", 
            "Status": "ERROR", 
            "Description": "Ensure Docker daemon is running",
            "Details": str(e)
        }