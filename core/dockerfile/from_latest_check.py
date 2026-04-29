"""DL-01: Ensure FROM does not use :latest tag."""

from core.dockerfile.parser import parse_dockerfile


def run_check():
    """Ensure Dockerfile base images pin a specific version tag instead of :latest."""
    instructions = parse_dockerfile()
    if instructions is None:
        return {
            "Control_ID": "DL-01",
            "Description": "Ensure FROM does not use :latest tag",
            "Status": "N/A",
            "Details": "No Dockerfile configured. Use --dockerfile-path."
        }

    from_instructions = [i for i in instructions if i["instruction"] == "FROM"]
    if not from_instructions:
        return {
            "Control_ID": "DL-01",
            "Description": "Ensure FROM does not use :latest tag",
            "Status": "N/A",
            "Details": "No FROM instruction found in Dockerfile."
        }

    flagged = []
    for inst in from_instructions:
        image = inst["arguments"].split()[0] if inst["arguments"] else ""
        # Ignore build stage aliases (AS ...) — just check the image reference
        image = image.split(" AS ")[0].split(" as ")[0].strip()

        if image.lower() == "scratch":
            continue

        if ":" not in image:
            flagged.append(f"Line {inst['line']}: {image} (no tag specified, defaults to :latest)")
        elif image.endswith(":latest"):
            flagged.append(f"Line {inst['line']}: {image}")

    return {
        "Control_ID": "DL-01",
        "Description": "Ensure FROM does not use :latest tag",
        "Status": "FAIL" if flagged else "PASS",
        "Details": f"Base images using :latest: {'; '.join(flagged)}" if flagged else "All FROM instructions use pinned version tags."
    }
