import click
import tempfile
import os
from .processor import video_to_slides, download_video


@click.command()
@click.option("--url", help="YouTube video or playlist URL")
@click.option("--video", help="Local video file path")
@click.option("--output", default="out.pdf", help="Output PDF file name")
@click.option(
    "--resolution", default="720", help="Video resolution for download (default: 720p)"
)
@click.option(
    "--face-detection/--no-face-detection",
    default=True,
    help="Enable/disable face detection",
)
@click.option(
    "--diff-threshold",
    default=9.0,
    type=float,
    help="Difference threshold for duplicate detection",
)
@click.option("--tmp-folder", help="Custom temporary folder for frames (optional)")
def cli(url, video, output, resolution, face_detection, diff_threshold, tmp_folder):
    if url:
        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = os.path.join(temp_dir, "video.mp4")
            download_video(url, video_path, resolution)
            video_to_slides(
                video_path, output, face_detection, diff_threshold, tmp_folder
            )
    elif video:
        video_to_slides(video, output, face_detection, diff_threshold, tmp_folder)
    else:
        click.echo("Please provide either a YouTube URL or a local video file path.")
