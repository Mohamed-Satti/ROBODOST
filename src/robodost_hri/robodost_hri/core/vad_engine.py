import torch
import numpy as np
import warnings

class VadEngine:
    def __init__(self, threshold=0.75, sample_rate=16000):
        self.threshold = threshold
        self.sample_rate = sample_rate

        # PyTorch hub sometimes throws warnings we don't care about
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                trust_repo=True
            )
            
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[VAD] Loading Silero VAD on {self.device}...")
        self.model = self.model.to(self.device)
        
        self.get_speech_timestamps, self.save_audio, self.read_audio, self.VADIterator, self.collect_chunks = utils

    def is_speech(self, chunk: np.ndarray) -> bool:
        """
        Takes a float32 numpy array chunk from the microphone 
        and returns True if the speech probability > self.threshold
        """
        # Ensure it's a 1D array of floats
        chunk_sq = np.squeeze(chunk)
        
        # Convert to PyTorch tensor and move to device
        tensor_chunk = torch.from_numpy(chunk_sq).to(self.device)
        
        # We must add the batch dimension since the model expects it: [batch_size, sequence_length]
        if tensor_chunk.ndim == 1:
            tensor_chunk = tensor_chunk.unsqueeze(0)

        # Get speech probability
        speech_prob = self.model(tensor_chunk, self.sample_rate).item()
        return speech_prob > self.threshold

if __name__ == "__main__":
    print("Loading VAD model...")
    vad = VadEngine()
    print("VAD initialized successfully.")
    # Test with dummy silence data
    dummy_audio_chunk = np.zeros(512, dtype=np.float32)
    has_speech = vad.is_speech(dummy_audio_chunk)
    print(f"Speech detected on silence: {has_speech}")
