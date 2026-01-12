"""
Audio Transcriber
Converts audio files (.wav, .mp3, .m4a) to text using Whisper
"""

import os

# Ensure ffmpeg is in PATH (commonly installed in ~/.local/bin)
os.environ['PATH'] = os.path.expanduser('~/.local/bin') + ':' + os.environ.get('PATH', '')

import whisper


class AudioTranscriber:
    """
    Transcribes audio files using OpenAI's Whisper model (runs locally)
    """

    def __init__(self, model_size="base"):
        """
        Initialize the transcriber with a Whisper model

        Args:
            model_size (str): Model size - "tiny", "base", "small", "medium", "large"
                             Larger = more accurate but slower
                             - tiny: ~1GB RAM, fastest
                             - base: ~1GB RAM, good balance (default)
                             - small: ~2GB RAM, better accuracy
                             - medium: ~5GB RAM, high accuracy
                             - large: ~10GB RAM, best accuracy
        """
        print(f"   Loading Whisper model '{model_size}'...")
        self.model = whisper.load_model(model_size)
        print(f"   Whisper model loaded")

    def transcribe(self, audio_path):
        """
        Transcribe an audio file to text

        Args:
            audio_path (str): Path to audio file (.wav, .mp3, .m4a, etc.)

        Returns:
            dict: Transcription result with 'text' and 'segments'
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"   Transcribing {os.path.basename(audio_path)}...")
        result = self.model.transcribe(audio_path)

        return {
            'text': result['text'],
            'segments': result.get('segments', []),
            'language': result.get('language', 'en')
        }

    def transcribe_with_speakers(self, audio_path):
        """
        Transcribe and attempt to format with speaker labels

        Note: Whisper doesn't do speaker diarization, so this uses
        segment timestamps to add structure. For true speaker ID,
        you'd need pyannote or similar.

        Args:
            audio_path (str): Path to audio file

        Returns:
            str: Formatted transcript text
        """
        result = self.transcribe(audio_path)

        # Format segments with timestamps
        formatted_lines = []
        for segment in result['segments']:
            start = segment['start']
            text = segment['text'].strip()
            if text:
                timestamp = f"[{int(start // 60):02d}:{int(start % 60):02d}]"
                formatted_lines.append(f"{timestamp} {text}")

        return '\n'.join(formatted_lines)


# Test if run directly
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python transcriber.py <audio_file>")
        print("Supported formats: .wav, .mp3, .m4a, .flac, .ogg")
        sys.exit(1)

    audio_file = sys.argv[1]
    print(f"Transcribing: {audio_file}\n")

    transcriber = AudioTranscriber(model_size="base")
    result = transcriber.transcribe(audio_file)

    print("\n" + "=" * 60)
    print("TRANSCRIPT")
    print("=" * 60)
    print(result['text'])
    print("\n" + "=" * 60)
    print(f"Language detected: {result['language']}")
