class YoutubeTranscriptionError(Exception):
    def __init__(self, message="Video extraction failed"):
        self.message = message

    def __str__(self):
        return f"Error in transcription Process. {self.message}"


class VideoExtractionError(YoutubeTranscriptionError):
    def __init__(self, message="Video extraction failed"):
        super().__init__(message)


class AudioExtractionError(YoutubeTranscriptionError):
    def __init__(self, message="Audio extraction failed"):
        super().__init__(message)
