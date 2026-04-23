import os
import urllib.request
import wave
import sounddevice as sd
import numpy as np
from piper.voice import PiperVoice

class TtsEngine:
    def __init__(self, model_dir="models"):
        self.model_dir = os.path.join(os.path.dirname(__file__), model_dir)
        os.makedirs(self.model_dir, exist_ok=True)
        
        # We will use the lessac medium voice as a generic high-quality test voice
        self.model_name = "en_US-lessac-medium"
        self.onnx_file = os.path.join(self.model_dir, f"{self.model_name}.onnx")
        self.json_file = os.path.join(self.model_dir, f"{self.model_name}.onnx.json")

        self._ensure_model_exists()
        
        print("Loading Piper TTS Model...")
        self.voice = PiperVoice.load(self.onnx_file, config_path=self.json_file)
        self.sample_rate = self.voice.config.sample_rate

    def _ensure_model_exists(self):
        """Downloads the ONNX voice model if it's missing from the models directory."""
        if not os.path.exists(self.onnx_file) or not os.path.exists(self.json_file):
            print(f"Downloading Piper TTS Model ({self.model_name})... This only happens once.")
            base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium"
            urllib.request.urlretrieve(f"{base_url}/en_US-lessac-medium.onnx", self.onnx_file)
            urllib.request.urlretrieve(f"{base_url}/en_US-lessac-medium.onnx.json", self.json_file)

    def speak(self, text: str):
        """Synthesizes text and plays it directly over laptop speakers."""
        if not text or not text.strip():
            return

        print(f"[TTS] Synthesizing: {text}")
        
        # Piper yields a stream of AudioChunk objects
        # We collect them and play them directly to speakers
        frames_list = []
        for chunk in self.voice.synthesize(text):
            frames_list.append(np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16))

        if frames_list:
            full_audio = np.concatenate(frames_list)
            sd.play(full_audio, samplerate=self.sample_rate)
            sd.wait() # Blocking call so we don't start listening over our own voice
            
if __name__ == "__main__":
    tts = TtsEngine()
    tts.speak("Hello there! My speech engine is fully operational.")
