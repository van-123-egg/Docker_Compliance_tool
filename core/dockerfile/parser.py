"""
Dockerfile parser utility.
Reads and tokenizes a Dockerfile into structured instructions.
"""

import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

import subprocess
import logging

logger = logging.getLogger(__name__)

# Global state — set by main.py
_target_image = None
_parsed_instructions = None


def set_target_image(image_name):
    """Set the target image for all checks to use."""
    global _target_image, _parsed_instructions
    _target_image = image_name
    _parsed_instructions = None  # Reset cache


def get_target_image():
    """Get the currently configured target image."""
    return _target_image


def parse_dockerfile(image_name=None):
    """Parse a Docker image's history into a list of instruction dicts.
    
    Returns a list of:
        {"line": int, "instruction": str, "arguments": str, "raw": str}
    """
    global _parsed_instructions
    
    target = image_name or _target_image
    if target is None:
        return None

    if _parsed_instructions is not None and image_name is None:
        return _parsed_instructions

    try:
        # Get history newest to oldest
        result = subprocess.run(
            ["docker", "history", "--no-trunc", "--format", "{{.CreatedBy}}", target],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        logger.debug(f"Failed to get history for image {target}: {e}")
        return None

    instructions = []
    # Reverse so it's oldest to newest (like a Dockerfile)
    lines = result.stdout.strip().splitlines()[::-1]
    
    for i, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line:
            continue

        # Clean up some buildkit noise
        if line.endswith("# buildkit"):
            line = line[:-10].strip()

        # Some history entries are just commands without Dockerfile instructions (like bash commands).
        # We try to infer or normalize them.
        instruction = "UNKNOWN"
        arguments = line

        # If it starts with standard Dockerfile instructions
        parts = line.split(maxsplit=1)
        if parts and parts[0].upper() in (
            "CMD", "ENTRYPOINT", "EXPOSE", "ENV", "ADD", "COPY", "VOLUME", "USER", "WORKDIR", "ARG", "ONBUILD", "STOPSIGNAL", "HEALTHCHECK", "SHELL", "LABEL", "MAINTAINER", "RUN"
        ):
            instruction = parts[0].upper()
            arguments = parts[1] if len(parts) > 1 else ""
        elif line.startswith("#(nop)"):
            # Older docker formats #(nop) CMD ["/bin/sh"]
            nop_line = line.replace("#(nop)", "").strip()
            parts = nop_line.split(maxsplit=1)
            if parts and parts[0].upper() in ("CMD", "ENTRYPOINT", "EXPOSE", "ENV", "ADD", "COPY", "VOLUME", "USER", "WORKDIR", "ARG", "ONBUILD", "STOPSIGNAL", "HEALTHCHECK", "SHELL", "LABEL", "MAINTAINER", "RUN"):
                instruction = parts[0].upper()
                arguments = parts[1] if len(parts) > 1 else ""
        elif line.startswith("/bin/sh -c") or line.startswith("/bin/bash -c"):
            # It's a RUN command where the instruction isn't explicit
            instruction = "RUN"
            arguments = line

        instructions.append({
            "line": i + 1,  # Synthetic line number based on history order
            "instruction": instruction,
            "arguments": arguments,
            "raw": raw_line,
        })

    if image_name is None:
        _parsed_instructions = instructions
    
    return instructions

