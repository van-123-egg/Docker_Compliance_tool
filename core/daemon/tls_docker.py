import subprocess
import os

def run_check():
    """2.6 Ensure TLS authentication for Docker daemon is configured"""
    try:
        if os.name == 'nt':
            # Check running process arguments for TLS flags using a privileged cross-host container
            cmd = ["docker", "run", "--rm", "--pid=host", "alpine", "ps", "-ef"]
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8")
        else:
            # Use native Linux system ps command
            output = subprocess.check_output(["ps", "-ef"]).decode("utf-8")
        
        dockerd_lines = [line for line in output.splitlines() if "dockerd" in line and "grep" not in line]
        
        tls_enabled = False
        for line in dockerd_lines:
            if "--tlsverify" in line or "--tls" in line:
                tls_enabled = True
                break
                
        return {
            "Control_ID": "2.6",
            "Description": "Ensure TLS authentication for Docker daemon is configured",
            "Status": "PASS" if tls_enabled else "MANUAL_REVIEW", # TLS can also be set in daemon.json
            "Details": "TLS flags found in process args." if tls_enabled else "TLS flags not in process args. Check daemon.json manually."
        }
    except Exception as e:
        return {"Control_ID": "2.6","Description": "Ensure TLS authentication for Docker daemon is configured",  "Status": "ERROR", "Details": str(e)}