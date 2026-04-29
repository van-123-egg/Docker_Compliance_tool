"""
Centralized severity levels and remediation guidance for all Docker CIS checks.

Severity levels follow CIS benchmark impact ratings:
  CRITICAL — Direct container escape or host compromise
  HIGH     — Significant security weakening
  MEDIUM   — Defense-in-depth violations
  LOW      — Hardening recommendations
  INFO     — Informational / best practice
"""

# Map of Control_ID -> severity level
SEVERITY_MAP = {
    # Host Configuration
    "1.2.1":         "HIGH",
    "1.1.2":         "HIGH",

    # Daemon Configuration
    "Daemon_Status": "CRITICAL",
    "2.6":           "CRITICAL",
    "2.4":           "HIGH",
    "2.11":          "MEDIUM",

    # Socket Configuration
    "3.15":          "HIGH",
    "3.16":          "HIGH",
    "3.3":           "MEDIUM",
    "3.4":           "MEDIUM",

    # Container Runtime
    "5.5":           "CRITICAL",
    "4.1":           "HIGH",
    "5.13":          "MEDIUM",
    "5.11":          "HIGH",
    "5.10":          "CRITICAL",
    "5.6":           "CRITICAL",
    "5.32":          "CRITICAL",

    # Image Security
    "IMG-01":        "MEDIUM",
    "IMG-02":        "MEDIUM",
    "IMG-03":        "HIGH",
    "IMG-04":        "LOW",
    "IMG-05":        "LOW",
    "IMG-06":        "CRITICAL",
}


# Map of Control_ID -> remediation guidance with exact docker commands
REMEDIATION_MAP = {
    # --- Host Configuration ---
    "1.2.1": {
        "fix": (
            "Linux: Add audit rules for Docker daemon:\n"
            "  sudo auditctl -w /usr/bin/dockerd -k docker\n"
            "  sudo auditctl -w /etc/docker -k docker\n"
            "Windows: Enable Detailed Tracking via:\n"
            "  auditpol /set /category:\"Detailed Tracking\" /success:enable /failure:enable"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 1.2.1"
    },
    "1.1.2": {
        "fix": (
            "Review and remove untrusted users from the docker group:\n"
            "  Linux:   sudo gpasswd -d <username> docker\n"
            "  Windows: net localgroup docker-users <username> /delete\n"
            "Only grant Docker access to users who require it."
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 1.1.2"
    },

    # --- Daemon Configuration ---
    "Daemon_Status": {
        "fix": (
            "Start the Docker daemon:\n"
            "  Linux:   sudo systemctl start docker\n"
            "  Windows: Start-Service docker  OR  open Docker Desktop"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Pre-requisite"
    },
    "2.6": {
        "fix": (
            "Configure TLS for the Docker daemon:\n"
            "  dockerd --tlsverify --tlscacert=ca.pem --tlscert=server-cert.pem --tlskey=server-key.pem -H=0.0.0.0:2376\n"
            "Or add to /etc/docker/daemon.json:\n"
            "  {\"tls\": true, \"tlsverify\": true, \"tlscacert\": \"/path/ca.pem\", \"tlscert\": \"/path/cert.pem\", \"tlskey\": \"/path/key.pem\"}"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 2.6"
    },
    "2.4": {
        "fix": (
            "Remove insecure registries from /etc/docker/daemon.json:\n"
            "  Remove the \"insecure-registries\" key or set it to an empty list:\n"
            "  {\"insecure-registries\": []}\n"
            "Then restart Docker: sudo systemctl restart docker"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 2.4"
    },
    "2.11": {
        "fix": (
            "Configure a remote logging driver in /etc/docker/daemon.json:\n"
            "  {\"log-driver\": \"syslog\", \"log-opts\": {\"syslog-address\": \"tcp://your-log-server:514\"}}\n"
            "Other options: splunk, gelf, fluentd, awslogs\n"
            "Then restart Docker: sudo systemctl restart docker"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 2.11"
    },

    # --- Socket Configuration ---
    "3.15": {
        "fix": (
            "Set correct ownership on the Docker socket:\n"
            "  sudo chown root:docker /var/run/docker.sock"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 3.15"
    },
    "3.16": {
        "fix": (
            "Set restrictive permissions on the Docker socket:\n"
            "  sudo chmod 660 /var/run/docker.sock"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 3.16"
    },
    "3.3": {
        "fix": (
            "Set correct ownership on the docker.socket unit file:\n"
            "  sudo chown root:root /usr/lib/systemd/system/docker.socket"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 3.3"
    },
    "3.4": {
        "fix": (
            "Set restrictive permissions on the docker.socket unit file:\n"
            "  sudo chmod 644 /usr/lib/systemd/system/docker.socket"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 3.4"
    },

    # --- Container Runtime ---
    "5.5": {
        "fix": (
            "Do NOT use the --privileged flag. Instead, grant only specific capabilities:\n"
            "  docker run --cap-drop ALL --cap-add NET_BIND_SERVICE <image>\n"
            "If a container currently uses --privileged, re-create it without that flag:\n"
            "  docker stop <container> && docker rm <container>\n"
            "  docker run --cap-drop ALL --cap-add <NEEDED_CAP> <image>"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 5.5"
    },
    "4.1": {
        "fix": (
            "Always specify a non-root user in your Dockerfile:\n"
            "  RUN useradd -r appuser\n"
            "  USER appuser\n"
            "Or pass --user at runtime:\n"
            "  docker run --user 1000:1000 <image>"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 4.1"
    },
    "5.13": {
        "fix": (
            "Run containers with a read-only root filesystem:\n"
            "  docker run --read-only <image>\n"
            "Use tmpfs for writable directories:\n"
            "  docker run --read-only --tmpfs /tmp --tmpfs /run <image>"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 5.13"
    },
    "5.11": {
        "fix": (
            "Set memory limits when running containers:\n"
            "  docker run --memory=512m --memory-swap=1g <image>\n"
            "In docker-compose.yml:\n"
            "  deploy:\n"
            "    resources:\n"
            "      limits:\n"
            "        memory: 512M"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 5.11"
    },
    "5.10": {
        "fix": (
            "Do NOT use --network=host. Use bridge (default) or custom networks:\n"
            "  docker run --network=bridge <image>\n"
            "Or create a custom network:\n"
            "  docker network create mynet\n"
            "  docker run --network=mynet <image>"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 5.10"
    },
    "5.6": {
        "fix": (
            "Do NOT mount sensitive host directories. Remove volume mounts for:\n"
            "  /, /boot, /dev, /etc, /lib, /proc, /sys, /usr\n"
            "Use named volumes instead of host bind mounts:\n"
            "  docker volume create app-data\n"
            "  docker run -v app-data:/app/data <image>"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 5.6"
    },
    "5.32": {
        "fix": (
            "Do NOT mount the Docker socket inside containers:\n"
            "  Remove -v /var/run/docker.sock:/var/run/docker.sock from your docker run command.\n"
            "If you need Docker API access, use a restricted proxy like docker-socket-proxy:\n"
            "  docker run -v /var/run/docker.sock:/var/run/docker.sock tecnativa/docker-socket-proxy"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 5.32"
    },

    # --- Image Security ---
    "IMG-01": {
        "fix": (
            "Always use specific version tags instead of :latest:\n"
            "  docker pull nginx:1.25.3  (instead of docker pull nginx:latest)\n"
            "In Dockerfile:\n"
            "  FROM python:3.12-slim  (instead of FROM python:latest)\n"
            "Re-tag existing images:\n"
            "  docker tag myapp:latest myapp:1.0.0"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 4.7"
    },
    "IMG-02": {
        "fix": (
            "Rebuild images from updated base images regularly:\n"
            "  docker pull <base-image>:<tag>\n"
            "  docker build --no-cache -t myapp:latest .\n"
            "Set up a CI/CD pipeline to rebuild images on a schedule (e.g., weekly)."
        ),
        "reference": "Docker Security Best Practices — Image Freshness"
    },
    "IMG-03": {
        "fix": (
            "Enable Docker Content Trust:\n"
            "  export DOCKER_CONTENT_TRUST=1\n"
            "To make it permanent, add to your shell profile (~/.bashrc or ~/.profile):\n"
            "  echo 'export DOCKER_CONTENT_TRUST=1' >> ~/.bashrc\n"
            "Windows PowerShell:\n"
            "  [System.Environment]::SetEnvironmentVariable('DOCKER_CONTENT_TRUST','1','User')"
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 4.5"
    },
    "IMG-04": {
        "fix": (
            "Remove dangling (untagged) images to reclaim disk space:\n"
            "  docker image prune -f\n"
            "To also remove unused images (not just dangling):\n"
            "  docker image prune -a -f\n"
            "Automate cleanup in CI/CD pipelines after builds."
        ),
        "reference": "Docker Security Best Practices — Image Hygiene"
    },
    "IMG-05": {
        "fix": (
            "Reduce image size by using minimal base images:\n"
            "  FROM alpine:3.19  OR  FROM python:3.12-slim\n"
            "Use multi-stage builds to exclude build tools:\n"
            "  FROM golang:1.22 AS builder\n"
            "  RUN go build -o app .\n"
            "  FROM alpine:3.19\n"
            "  COPY --from=builder /app /app"
        ),
        "reference": "Docker Security Best Practices — Minimal Images"
    },
    "IMG-06": {
        "fix": (
            "Scan images for vulnerabilities before deployment:\n"
            "  docker scout cves <image>    (Docker Desktop built-in)\n"
            "  trivy image <image>          (open-source alternative)\n"
            "Fix critical vulnerabilities by updating base image and dependencies:\n"
            "  docker pull <base-image>:<latest-patch-version>\n"
            "  docker build --no-cache -t myapp:latest ."
        ),
        "reference": "CIS Docker Benchmark v1.6.0, Section 4.4"
    },
}


def enrich_result(result):
    """Add Severity and Remediation fields to a check result dict."""
    control_id = result.get("Control_ID", "")
    result["Severity"] = SEVERITY_MAP.get(control_id, "INFO")

    remediation = REMEDIATION_MAP.get(control_id)
    if remediation and result.get("Status") in ("FAIL", "WARN", "ERROR"):
        result["Remediation"] = remediation["fix"]
        result["Reference"] = remediation["reference"]
    else:
        result["Remediation"] = ""
        result["Reference"] = REMEDIATION_MAP.get(control_id, {}).get("reference", "")

    return result
