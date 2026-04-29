"""
Dockerfile parser utility.
Reads and tokenizes a Dockerfile into structured instructions.
"""

import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Global state — set by main.py via set_dockerfile_path()
_dockerfile_path = None
_parsed_instructions = None


def set_dockerfile_path(path):
    """Set the Dockerfile path for all checks to use."""
    global _dockerfile_path, _parsed_instructions
    _dockerfile_path = path
    _parsed_instructions = None  # Reset cache


def get_dockerfile_path():
    """Get the currently configured Dockerfile path."""
    return _dockerfile_path


def parse_dockerfile(path=None):
    """Parse a Dockerfile into a list of instruction dicts.
    
    Returns a list of:
        {"line": int, "instruction": str, "arguments": str, "raw": str}
    
    Handles multi-line instructions (backslash continuation).
    """
    global _parsed_instructions
    
    filepath = path or _dockerfile_path
    if filepath is None:
        return None

    if _parsed_instructions is not None and path is None:
        return _parsed_instructions

    filepath = Path(filepath)
    if not filepath.exists():
        logger.debug(f"Dockerfile not found: {filepath}")
        return None

    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        logger.debug(f"Failed to read Dockerfile: {e}")
        return None

    instructions = []
    lines = content.splitlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            i += 1
            continue

        # Handle multi-line (backslash continuation)
        raw_line = line
        line_num = i + 1
        while line.endswith('\\') and i + 1 < len(lines):
            i += 1
            continuation = lines[i].strip()
            raw_line += '\n' + continuation
            line = line[:-1].rstrip() + ' ' + continuation

        # Parse instruction and arguments
        match = re.match(r'^(\w+)\s*(.*)', line, re.DOTALL)
        if match:
            instruction = match.group(1).upper()
            arguments = match.group(2).strip()
            instructions.append({
                "line": line_num,
                "instruction": instruction,
                "arguments": arguments,
                "raw": raw_line,
            })

        i += 1

    if path is None:
        _parsed_instructions = instructions
    
    return instructions
