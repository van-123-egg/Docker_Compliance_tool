import subprocess
import json

def run_check():
    """2.4 Ensure insecure registries are not used"""
    try:
        # Fetching the raw registry config from docker info
        output = subprocess.check_output(["docker", "info", "--format", "{{json .RegistryConfig.InsecureRegistryCIDRs}}"]).decode("utf-8")
        registries = json.loads(output)
        
        # 127.0.0.0/8 is present by default for local loopback. Anything else is flagged.
        insecure_external = [reg for reg in registries if not reg.startswith("127.")]
        
        status = "FAIL" if insecure_external else "PASS"
        return {
            "Control_ID": "2.4",
            "Description": "Ensure insecure registries are not used",
            "Status": status,
            "Details": f"Insecure registries configured: {', '.join(insecure_external)}" if insecure_external else "No external insecure registries configured."
        }
    except Exception as e:
        return {"Control_ID": "2.4","Description": "Ensure insecure registries are not used",  "Status": "ERROR", "Details": str(e)}