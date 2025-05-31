import os
import subprocess
import requests
import time
from pathlib import Path

# This assumes start_model_server.py lives *outside* the AnimatedDrawings repo
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR / "AnimatedDrawings"
SCRIPT_PATH = REPO_ROOT / "scripts" / "download_model.py"
CHECKPOINT_DIR = REPO_ROOT / "checkpoints"
MODEL_FILE = CHECKPOINT_DIR / "drawn_humanoid_detector.mar"


def download_model():
    if not MODEL_FILE.exists():
        print("⬇️ Downloading detection model...")
        subprocess.run(["python", str(SCRIPT_PATH)], cwd=REPO_ROOT)
    else:
        print("✅ Detection model already present.")


def start_torchserve():
    print("🚀 Starting TorchServe...")
    if not CHECKPOINT_DIR.exists():
        print(f"❌ Checkpoints directory missing: {CHECKPOINT_DIR}")
        return

    subprocess.run(
        [
            "torchserve",
            "--start",
            "--ncs",
            "--model-store",
            str(CHECKPOINT_DIR),
            "--models",
            "drawn_humanoid_detector=drawn_humanoid_detector.mar",
        ]
    )


def wait_for_server(timeout=20):
    print("⏳ Waiting for model server to start...")
    for _ in range(timeout):
        try:
            r = requests.get("http://localhost:8080/ping")
            if r.status_code == 200:
                print("✅ TorchServe is live!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    print("❌ Failed to start TorchServe.")
    return False


if __name__ == "__main__":
    download_model()
    start_torchserve()
    wait_for_server()
