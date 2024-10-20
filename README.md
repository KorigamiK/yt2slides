# yt2slides

Convert a local or a YouTube video/playlist into pdf slides

## Installation

You will need ffmpeg installed.

```bash
pip install -r requirements.txt
```

## Usage

```bash
Usage: main.py [OPTIONS]

Options:
  --url TEXT                      YouTube video or playlist URL
  --video TEXT                    Local video file path
  --output TEXT                   Output PDF file name
  --resolution TEXT               Video resolution for download (default: 720p)
  --face-detection / --no-face-detection
                                  Enable/disable face detection
  --diff-threshold FLOAT          Difference threshold for duplicate detection
  --tmp-folder TEXT               Custom temporary folder for frames
                                  (optional)
  --help                          Show this message and exit.
```

## Example

```bash
python main.py --url https://www.youtube.com/watch?v=6J6kF4ZGv6M --output slides.pdf
```

Example slides [lec7.pdf](https://github.com/user-attachments/files/17450383/lec7.pdf)


```bash
python yt2slides.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --output "slides.pdf" \
  --resolution 1080 --no-face-detection --diff-threshold 5.0
```
