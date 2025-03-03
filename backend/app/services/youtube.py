import subprocess
import os
import requests
from app.config import config


def get_transcript(yt_url: str):
    endpoint = "https://api.supadata.ai/v1/youtube/transcript"
    params = {
        "url": yt_url,
        "text": "true",
        "lang": "en"
    }
    headers = {
        "x-api-key": config.SUPADATA_API_KEY
    }

    response = requests.get(endpoint, params=params, headers=headers)
    if response.status_code == 200:
        res = response.json()
        return res.get("content")
    else:
        return None


def get_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    if "embed/" in url:
        return url.split("embed/")[-1]
    if "watch?v=" in url:
        return url.split("watch?v=")[-1].split("&")[0]
    return ""


def download_youtube_audio(url, output_file=None):
    video_id = get_video_id(url)
    if not video_id:
        return None

    if output_file is None:
        output_file = f"{video_id}.mp3"

    command = [
        "yt-dlp",
        "-f", "bestaudio[abr<=64]",
        "-o", output_file,
        "--extract-audio",
        "--audio-format", "mp3",
        url
    ]

    process = subprocess.run(command, capture_output=True, text=True)

    if process.returncode != 0:
        print("Error downloading audio:", process.stderr)
        return None

    file_size = os.path.getsize(output_file)
    if file_size > 19000000:
        output_file = compress_audio(output_file)

    return output_file


def compress_audio(input_file, max_size_bytes=19000000):
    file_size = os.path.getsize(input_file)

    if file_size <= max_size_bytes:
        print("File already within size limit.")
        return input_file

    # Get original duration
    duration_info = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_file],
        capture_output=True, text=True
    )

    duration = float(duration_info.stdout.strip())

    target_size_bits = max_size_bytes * 8
    optimal_bitrate = int((target_size_bits / duration) * 0.95)

    # Convert to kilobits per second for ffmpeg
    optimal_bitrate_k = str(optimal_bitrate // 1000) + "k"

    compressed_file = "compressed_audio.mp3"
    command = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
        "-i", input_file,
        "-b:a", optimal_bitrate_k,
        compressed_file
    ]

    subprocess.run(command, capture_output=True)

    compressed_size = os.path.getsize(compressed_file)
    print(f"Compressed file size: {compressed_size} bytes")

    # If still too large (due to encoder overhead or minimum bitrate constraints)
    if compressed_size > max_size_bytes:
        # Try again with an adjusted bitrate
        adjusted_factor = max_size_bytes / compressed_size * 0.95
        adjusted_bitrate = int(optimal_bitrate * adjusted_factor)
        adjusted_bitrate_k = str(adjusted_bitrate // 1000) + "k"

        adjusted_command = [
            "ffmpeg",
            "-y",
            "-i", input_file,
            "-b:a", adjusted_bitrate_k,
            compressed_file
        ]

        subprocess.run(adjusted_command, capture_output=True)

    return compressed_file
