import subprocess

def run_check():
    """2.11 Ensure that centralized and remote logging is configured"""
    try:
        output = subprocess.check_output(["docker", "info", "--format", "{{.LoggingDriver}}"]).decode("utf-8").strip()
        
        # 'json-file' and 'local' are standard but do not fulfill remote logging requirements
        status = "FAIL" if output in ["json-file", "local"] else "PASS"
        
        return {
            "Control_ID": "2.11",
            "Description": "Ensure centralized and remote logging is configured",
            "Status": status,
            "Details": f"Current logging driver: {output}"
        }
    except Exception as e:
        return {"Control_ID": "2.11","Description": "Ensure centralized and remote logging is configured",  "Status": "ERROR", "Details": str(e)}