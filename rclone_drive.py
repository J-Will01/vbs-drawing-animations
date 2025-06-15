import subprocess
from pathlib import Path

class RcloneDrive:
    def __init__(self, remote_name: str, image_dir: str, video_dir: str):
        self.remote_image_path = f"{remote_name}:{image_dir}"
        self.remote_video_path = f"{remote_name}:{video_dir}"

    def pull_images(self, local_path: Path):
        """Download new images from Drive to local_path."""
        subprocess.run([
            "rclone", "copy", self.remote_image_path, str(local_path),
            "--drive-skip-gdocs", "--ignore-existing"
        ], check=True)

    def push_videos(self, local_path: Path):
        """Upload videos from local_path to Drive."""
        subprocess.run([
            "rclone", "copy", str(local_path), self.remote_video_path
        ], check=True)
