"""DL-03: Ensure ADD is not used for fetching remote URLs."""

from core.dockerfile.parser import parse_dockerfile


def run_check():
    """Flag ADD instructions used with remote URLs — COPY is safer for local files,
    and curl/wget + RUN is more transparent for remote downloads."""
    instructions = parse_dockerfile()
    if instructions is None:
        return {
            "Control_ID": "DL-03",
            "Description": "Ensure ADD is not used for remote URLs",
            "Status": "N/A",
            "Details": "No target image configured."
        }

    add_instructions = [i for i in instructions if i["instruction"] == "ADD"]
    if not add_instructions:
        return {
            "Control_ID": "DL-03",
            "Description": "Ensure ADD is not used for remote URLs",
            "Status": "PASS",
            "Details": "No ADD instructions found. COPY is used correctly."
        }

    flagged = []
    for inst in add_instructions:
        args = inst["arguments"]
        # Check if source looks like a URL
        if any(args.startswith(prefix) for prefix in ["http://", "https://", "ftp://"]):
            flagged.append(f"Line {inst['line']}: ADD {args[:60]}...")
        else:
            # Even local ADD should be flagged as WARN — COPY is preferred
            flagged.append(f"Line {inst['line']}: ADD used instead of COPY")

    return {
        "Control_ID": "DL-03",
        "Description": "Ensure ADD is not used for remote URLs",
        "Status": "WARN" if flagged else "PASS",
        "Details": (
            f"ADD instructions found (use COPY for local files, curl/wget for remote): {'; '.join(flagged)}"
            if flagged
            else "No ADD instructions found."
        )
    }
