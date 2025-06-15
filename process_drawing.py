import sys
from pathlib import Path
import subprocess
import os

def process_image(image_path: Path):
    image_path = image_path.resolve()
    image_name = image_path.stem
    repo_root = Path(__file__).resolve().parents[1]
    data_dir = repo_root / "data"
    output_dir = data_dir / "output" / image_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Unset EGL override just in case
    env = os.environ.copy()
    env.pop("PYOPENGL_PLATFORM", None)

    # Run the official image-to-animation script inside Xvfb
    print(f"🎞️ Animating {image_name} via image_to_animation.py")
    result = subprocess.run([
        "xvfb-run", "-s", "-screen 0 1024x768x24",
        "python3", str(repo_root / "examples" / "image_to_animation.py"),
        str(image_path),
        str(output_dir)
    ], cwd=repo_root)



    # Move final video to data/output/image_name.mp4
    video_output = output_dir / "video.gif"  # NOTE: it creates .gif not .mp4
    final_video = data_dir / "output" / f"{image_name}.gif"

    if result.returncode == 0 and video_output.exists():
        video_output.rename(final_video)
        print(f"✅ Video saved: {final_video}")
        return True
    else:
        print(f"❌ Animation failed for {image_name}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 process_drawing.py <image_path>")
        sys.exit(1)

    image_file = Path(sys.argv[1])
    if not image_file.exists():
        print(f"❌ Image not found: {image_file}")
        sys.exit(1)

    process_image(image_file)
