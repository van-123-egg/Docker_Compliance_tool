import subprocess
import os

def run_check():
    """1.2.1 Ensure auditing is configured for the Docker daemon"""
    try:
        if os.name == 'nt':
            # Check Windows Audit Policy for Detailed Tracking
            output = subprocess.check_output(["auditpol", "/get", "/category:Detailed Tracking"], stderr=subprocess.STDOUT).decode("utf-8")
            status = "PASS" if "Success" in output or "Failure" in output else "FAIL"
            details = "Windows Audit Policy is enabled for Detailed Tracking." if status == "PASS" else "Windows Audit Policy for Detailed Tracking is not fully configured."
        else:
            # Check the auditctl rules for dockerd
            output = subprocess.check_output(["auditctl", "-l"], stderr=subprocess.STDOUT).decode("utf-8")
            
            if "/usr/bin/dockerd" in output:
                status = "PASS"
                details = "Audit rules for Docker daemon are present."
            else:
                status = "FAIL"
                details = "No audit rules found for /usr/bin/dockerd."
            
        return {
            "Control_ID": "1.2.1",
            "Description": "Ensure auditing is configured for the Docker daemon",
            "Status": status,
            "Details": details
        }
    except Exception as e:
        return {"Control_ID": "1.2.1","Description": "Ensure auditing is configured for the Docker daemon", "Status": "ERROR", "Details": str(e)}