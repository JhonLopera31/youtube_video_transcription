import json
import logging
import os
import tempfile
from pathlib import Path

import openai
from pytubefix import YouTube
from pytubefix.cli import on_progress
from tenacity import retry, stop_after_attempt, wait_random_exponential
from utils.exceptions import VideoExtractionError

_logger = logging.getLogger(__name__)


openai.api_key = os.environ["OPENAI_API_KEY"]


def download_video(video_id: str):
    video_url = f"https://youtu.be/{video_id}"
    try:
        _logger.info(f"Downloading video: {video_url}")
        yt = YouTube(video_url, on_progress_callback=on_progress)
    except Exception as e:
        _logger.error(e)
        raise VideoExtractionError("Error extracting video") from e
    return yt


def download_audio(video_id: str, youtube_video):
    audio_filename = f"{video_id}.m4a"
    tmpdirname = tempfile.TemporaryDirectory()
    audio_file = Path(tmpdirname.name) / audio_filename  # temp save the downloaded audio file

    _logger.info("Downloading audio from video")
    stream = youtube_video.streams.get_audio_only()

    if not stream:
        _logger.error("No audio found'")
        raise VideoExtractionError("No audio found for'")

    _logger.info(f"Downloading audio in {audio_file}")
    stream.download(output_path=tmpdirname.name, filename=audio_filename)

    return audio_file, tmpdirname


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def _transcribe_with_backoff(**kwargs):
    return openai.Audio.transcribe(**kwargs)


def perform_audio_transcription(video_id: str, audio_file_path: str):
    json_tmpdirname = tempfile.TemporaryDirectory()
    json_file_path = Path(json_tmpdirname.name) / f"{video_id}.json"  # save json with transcription

    _logger.info("Starting audio transcription")
    with open(audio_file_path, "rb") as fb:
        transcript = _transcribe_with_backoff(model="whisper-1", file=fb, language="en")
        transcript_text = transcript["text"]

    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump({"video_id": video_id, "text": transcript_text}, f)

    return json_file_path, json_tmpdirname
