import os
import whisper
import warnings


class Transcriber:
    def __init__(self, model_name="base"):
        # Suppress FP16 warning
        warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
        self.model = whisper.load_model(model_name)
        self.supported_formats = {'.mp3', '.wav', '.mp4', '.mkv', '.mov', '.flv', '.aac', '.m4a'}

    def is_supported_file(self, filepath):
        return os.path.splitext(filepath)[1].lower() in self.supported_formats

    def transcribe_file(self, filepath):
        result = self.model.transcribe(filepath)
        return result["text"]

    def save_transcript(self, filepath, transcript):
        output_file = f"{os.path.splitext(filepath)[0]}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcript)