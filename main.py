import os
import stat
import zipfile
import urllib.request
import subprocess
import yaml
import traceback
from pathlib import Path
from PIL import Image

# === PATH SETUP ===
SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT / "AnimatedDrawings"

INPUT_DIR = SCRIPT_ROOT / "input_drawings"
OUTPUT_ROOT = SCRIPT_ROOT / "output_folders"
FINAL_VIDEO = SCRIPT_ROOT / "final_vbs_video.mp4"
MUSIC_FILE = SCRIPT_ROOT / "background_music.mp3"
FFMPEG_DIR = SCRIPT_ROOT / "bin"

IMAGE_TO_ANIMATION_SCRIPT = REPO_ROOT / "examples" / "image_to_animation.py"


def get_ffmpeg_binary():
    ffmpeg_path = FFMPEG_DIR / "ffmpeg"
    zip_path = FFMPEG_DIR / "ffmpeg.zip"

    if ffmpeg_path.exists():
        os.environ["IMAGEIO_FFMPEG_EXE"] = str(ffmpeg_path)
        return str(ffmpeg_path)

    print("🔽 Downloading ffmpeg binary for macOS...")
    FFMPEG_DIR.mkdir(parents=True, exist_ok=True)
    download_url = "https://evermeet.cx/ffmpeg/ffmpeg-6.1.zip"
    urllib.request.urlretrieve(download_url, zip_path)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for name in zip_ref.namelist():
            if name == "ffmpeg":
                zip_ref.extract(name, FFMPEG_DIR)
                break

    ffmpeg_path.chmod(ffmpeg_path.stat().st_mode | stat.S_IEXEC)
    os.environ["IMAGEIO_FFMPEG_EXE"] = str(ffmpeg_path)
    print(f"✅ ffmpeg ready at {ffmpeg_path}")
    return str(ffmpeg_path)


def ensure_dirs():
    for d in [INPUT_DIR, OUTPUT_ROOT, FFMPEG_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def convert_heic_to_png_mac(image_path: Path) -> Path:
    if image_path.suffix.lower() != ".heic":
        return image_path

    png_path = image_path.with_suffix(".png")
    if png_path.exists():
        print(f"🔁 {png_path.name} already exists, skipping")
        return png_path

    try:
        subprocess.run(
            ["sips", "-s", "format", "png", str(image_path), "--out", str(png_path)],
            check=True,
        )
        print(f"✅ Converted HEIC → PNG: {image_path.name}")
        return png_path
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to convert HEIC file {image_path.name}: {e}")
        return None


def convert_images_to_png():
    print("🖼️ Converting images to .png...")
    supported_extensions = [".png", ".jpg", ".jpeg", ".heic"]

    for image_path in INPUT_DIR.iterdir():
        if image_path.suffix.lower() not in supported_extensions:
            print(f"⚠️ Skipping unsupported file: {image_path.name}")
            continue

        try:
            if image_path.suffix.lower() == ".heic":
                converted = convert_heic_to_png_mac(image_path)
                if not converted:
                    continue
                continue

            new_path = image_path.with_suffix(".png")
            if new_path.exists():
                print(f"🔁 {new_path.name} already exists, skipping conversion")
                continue

            img = Image.open(image_path)
            img = img.convert("RGBA")
            img.save(new_path)
            print(f"✅ Converted {image_path.name} → {new_path.name}")

        except Exception as e:
            print(f"❌ Failed to convert {image_path.name}: {e}")
            traceback.print_exc()


def animate_all_images():
    print("🎬 Generating animations...")
    for image in INPUT_DIR.glob("*.png"):
        output_folder = OUTPUT_ROOT / image.stem
        output_folder.mkdir(parents=True, exist_ok=True)
        print(f"🧠 Animating {image.name} → {output_folder.name}")
        subprocess.run(
            ["python", str(IMAGE_TO_ANIMATION_SCRIPT), str(image), str(output_folder)]
        )


def stitch_videos():
    print("📽️ Stitching videos...")
    ffmpeg_bin = get_ffmpeg_binary()
    filelist_path = SCRIPT_ROOT / "filelist.txt"

    mp4_files = sorted(p for p in OUTPUT_ROOT.rglob("video.mp4") if p.exists())
    if not mp4_files:
        print("❌ No video clips found to stitch.")
        return

    with open(filelist_path, "w") as f:
        for mp4 in mp4_files:
            f.write(f"file '{mp4.resolve()}'\n")

    subprocess.run(
        [
            ffmpeg_bin,
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(filelist_path),
            "-c",
            "copy",
            str(FINAL_VIDEO),
        ]
    )

    if MUSIC_FILE.exists():
        final_with_music = FINAL_VIDEO.with_name(FINAL_VIDEO.stem + "_with_music.mp4")
        subprocess.run(
            [
                ffmpeg_bin,
                "-i",
                str(FINAL_VIDEO),
                "-i",
                str(MUSIC_FILE),
                "-shortest",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                str(final_with_music),
            ]
        )
        print(f"🎵 Video with music saved as: {final_with_music}")
    else:
        print(f"🎬 Final video saved as: {FINAL_VIDEO}")

    filelist_path.unlink()


def main():
    ensure_dirs()
    convert_images_to_png()
    animate_all_images()
    stitch_videos()
    print("✅ All done!")


if __name__ == "__main__":
    main()
