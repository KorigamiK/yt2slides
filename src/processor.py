import os
import shutil
import tempfile
from pathlib import Path
from tqdm import tqdm
import click
import cv2
from PIL import Image, ImageChops, ImageStat
import yt_dlp
import subprocess


def download_video(url, output_path, resolution="720"):
    ydl_opts = {
        "format": f"bestvideo[height<={resolution}][ext=mp4]/best[ext=mp4]",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def video_to_slides(
    video_path, output, face_detection, diff_threshold, tmp_folder=None
):
    frames_folder = (
        Path(tmp_folder) / "frames" if tmp_folder else Path(tempfile.mkdtemp())
    )
    frames_folder.mkdir(parents=True, exist_ok=True)

    try:
        extract_slides(video_path, frames_folder)
        remove_duplicates(frames_folder, face_detection, diff_threshold)
        write_to_pdf(frames_folder, output)
    finally:
        if tmp_folder and click.confirm(
            "Do you want to keep the temporary frames folder?", default=False
        ):
            click.echo(f"Frames folder kept at: {frames_folder}")
        else:
            shutil.rmtree(frames_folder)
            click.echo("Temporary frames folder removed.")


def extract_slides(video_path, frames_folder):
    frames_folder = Path(frames_folder)
    frames_folder.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-loglevel",
        "quiet",
        "-i",
        str(video_path),
        "-vsync",
        "0",
        "-vf",
        "select='eq(pict_type,PICT_TYPE_I)'",
        "-f",
        "image2",
        str(frames_folder / "frame_%03d.jpeg"),
    ]
    print("Extracting frames...")
    subprocess.run(cmd, check=True)


cv2.setUseOptimized(True)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def remove_duplicates(frames_folder, face_detection, diff_threshold):
    print("Removing duplicates...")
    frames = sorted(frames_folder.glob("*.jpeg"))
    duplicate_set = set()

    def process_image(img_path):
        img = cv2.imread(str(img_path))
        if face_detection:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            if any(w > img.shape[0] * 0.25 for (_, _, w, _) in faces):
                duplicate_set.add(img_path)
                return None
        return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    last_frame = process_image(frames[0])

    for i, frame_path in tqdm(
        enumerate(frames[1:], 1), total=len(frames) - 1, desc="Processing frames"
    ):
        cur_frame = process_image(frame_path)
        if cur_frame is None:
            continue

        diff_img = ImageChops.difference(cur_frame, last_frame)
        diff_percent = 100 * (sum(ImageStat.Stat(diff_img).mean) / (3 * 255))

        if diff_percent <= diff_threshold:
            duplicate_set.add(frames[i - 1])
        last_frame = cur_frame

    for image in tqdm(duplicate_set, desc="Removing duplicates"):
        image.unlink()

    print(f"Removed {len(duplicate_set)} duplicates and full screen faces")


def write_to_pdf(frames_folder, output):
    frames = sorted(Path(frames_folder).glob("*.jpeg"))
    images = [
        Image.open(frame).convert("RGB")
        for frame in tqdm(frames, desc="Loading images")
    ]
    images[0].save(output, save_all=True, append_images=images[1:])
    print(f"Output written to {output}")
