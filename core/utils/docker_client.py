import subprocess
import json
import logging

logger = logging.getLogger(__name__)

def get_running_containers_info():
    """
    Fetches inspection details for all currently running Docker containers.
    Returns a list of dictionaries.
    """
    try:
        # Get all running container IDs
        cmd = ["docker", "ps", "-q"]
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8').strip()
        if not output:
            return []
            
        container_ids = output.split('\n')
        
        # Inspect them to get full JSON config
        inspect_cmd = ["docker", "inspect"] + container_ids
        inspect_output = subprocess.check_output(inspect_cmd, stderr=subprocess.DEVNULL).decode('utf-8')
        
        return json.loads(inspect_output)
    except Exception as e:
        logger.debug(f"Failed to get container info: {e}")
        return []


def get_all_images_info():
    """
    Fetches inspection details for all local Docker images.
    Returns a list of dictionaries with full image metadata.
    """
    try:
        # Get all image IDs
        cmd = ["docker", "image", "ls", "-q", "--no-trunc"]
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8').strip()
        if not output:
            return []

        # Deduplicate IDs (same image can appear multiple times with different tags)
        image_ids = list(set(output.split('\n')))

        # Inspect them to get full JSON config
        inspect_cmd = ["docker", "image", "inspect"] + image_ids
        inspect_output = subprocess.check_output(inspect_cmd, stderr=subprocess.DEVNULL).decode('utf-8')

        return json.loads(inspect_output)
    except Exception as e:
        logger.debug(f"Failed to get image info: {e}")
        return []


def get_image_list():
    """
    Fetches a lightweight list of all local Docker images with repo, tag, ID, and size.
    Returns a list of dictionaries.
    """
    try:
        cmd = ["docker", "image", "ls", "--format", "{{json .}}"]
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8').strip()
        if not output:
            return []

        images = []
        for line in output.splitlines():
            if line.strip():
                images.append(json.loads(line))
        return images
    except Exception as e:
        logger.debug(f"Failed to get image list: {e}")
        return []
