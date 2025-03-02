import logging

from modules import load_data, text_extraction

_logger = logging.getLogger(__name__)


def run_process(arg):
    _logger.info("starting video data extraction")
    youtube_obj = text_extraction.download_video(arg.video_id)
    audio_path, tpm_dir = text_extraction.download_audio(arg.video_id, youtube_obj)
    transcription_json_path, tpm_dir_json = text_extraction.perform_audio_transcription(arg.video_id, audio_path)
    _logger.info("finished video data extraction")

    _logger.info("Loading data to database")
    load_data.load_to_postgres(transcription_json_path)
    _logger.info("Done")
