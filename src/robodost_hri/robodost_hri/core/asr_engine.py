from faster_whisper import WhisperModel
import numpy as np
import torch

class AsrEngine:
    def __init__(self, model_size="tiny", device=None, compute_type=None):
        """
        As user requested, we use the multilingual model (no '.en' ending).
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        if compute_type is None:
            compute_type = "float16" if device == "cuda" else "int8"
            
        print(f"[ASR] Loading Whisper '{model_size}' on {device} ({compute_type})...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.language = None # Auto-detect by default

    def set_language(self, language="auto"):
        if language == "auto":
            self.language = None
        else:
            self.language = language
        print(f"[ASR] Language set to: {self.language}")

    def transcribe(self, audio_buffer: np.ndarray) -> str:
        """
        Passes a continuous numpy float_32 buffer into faster-whisper.
        Since user specified multilingual testing, we don't force 'language'.
        """
        # Squeeze down to 1D if it's 2D
        audio_buffer = np.squeeze(audio_buffer)

        # Faster whisper takes numpy arrays directly!
        # We add vad_filter=True to double-check noise isolation
        # We add an initial_prompt to anchor the AI specifically into a TR/EN context
        # This prevents the 'tiny' model from wildly guessing Arabic/Chinese on noisy clips.
        segments, info = self.model.transcribe(
            audio_buffer, 
            beam_size=5,
            vad_filter=True,
            language=self.language,
            initial_prompt="Merhaba, hello, how are you? Nasılsın? (This is a Turkish and English conversation)"
        )

        # Re-assemble segments into single string
        transcription = []
        for segment in segments:
            transcription.append(segment.text.strip())

        return " ".join(transcription).strip()

if __name__ == "__main__":
    print("Loading ASR model...")
    asr = AsrEngine()
    print("ASR initialized successfully.")
