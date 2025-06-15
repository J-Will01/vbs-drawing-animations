import time
from pathlib import Path
import subprocess

from rclone_drive import RcloneDrive

# === Base Paths ===
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
LOCAL_IMAGE_DIR = DATA_DIR / "input"
LOCAL_VIDEO_DIR = DATA_DIR / "output"

# These should match the shared folder structure
REMOTE_NAME = "gdrive"
REMOTE_IMAGE_SUBPATH = "VBS-Drawings/input"
REMOTE_VIDEO_SUBPATH = "VBS-Drawings/output"

# === Initialize Drive Handler ===
drive = RcloneDrive(
    remote_name=REMOTE_NAME,
    image_dir=REMOTE_IMAGE_SUBPATH,
    video_dir=REMOTE_VIDEO_SUBPATH
)

# === Main Processing Function ===
def process_new_images():
    drive.pull_images(LOCAL_IMAGE_DIR)

    for img_file in LOCAL_IMAGE_DIR.glob("*.png"):
        print(f"🎨 Animating {img_file.name}")
        result = subprocess.run([
            "python",
            "process_drawing.py",
            str(img_file)
        ])

        if result.returncode == 0:
            print(f"✅ Animation complete: {img_file.name}")
            img_file.unlink()  # Optional: delete image after success
        else:
            print(f"❌ Failed to process {img_file.name}")

    drive.push_videos(LOCAL_VIDEO_DIR)

# === Main Loop ===
if __name__ == "__main__":
    LOCAL_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    LOCAL_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        process_new_images()
        print("⏳ Waiting 15 seconds...\n")
        time.sleep(15)
