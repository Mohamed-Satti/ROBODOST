from faster_whisper import WhisperModel
import numpy as np
import torch

class AsrEngine:
    def __init__(self, model_size="base", device=None, compute_type=None):
        """
        As user requested, we use the multilingual model (no '.en' ending).
        """
        if device is None:
            # We will aggressively try to load on CUDA first, completely ignoring PyTorch's awareness.
            # Many Jetson environments have CUDA available for CTranslate2 even if PyTorch is CPU-only.
            try:
                print(f"[ASR] Attempting to load Whisper '{model_size}' on CUDA (int8)...")
                self.model = WhisperModel(model_size, device="cuda", compute_type="int8")
                print("[ASR] Successfully loaded on CUDA!")
                self.language = None
                return
            except Exception as e:
                print(f"[ASR] CUDA failed ({e}). Falling back to CPU (int8)...")
                device = "cpu"
                compute_type = "int8"
        
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.set_language("auto") # Initialize defaults

    def set_language(self, language="auto"):
        if language == "auto":
            self.language = None
            self.initial_prompt = "Merhaba, hello, how are you? Nasılsın? (This is a Turkish and English conversation)"
        elif language == "tr":
            self.language = "tr"
            self.initial_prompt = "Merhaba, nasılsın? Bu bir Türkçe konuşmasıdır."
        else:
            self.language = language
            self.initial_prompt = "Hello, how are you? This is an English conversation."
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
            initial_prompt=self.initial_prompt,
            condition_on_previous_text=False # Prevents hallucination loops on small models
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
