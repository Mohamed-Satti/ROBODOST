import os
import numpy as np
import openwakeword
from openwakeword.model import Model

class WakewordEngine:
    def __init__(self, wakeword_phrase="robodost", threshold=0.5):
        print(f"Loading WakeWord Engine: [{wakeword_phrase}]")
        openwakeword.utils.download_models() # ensures built-ins are ready
        
        # Look for the custom model in the models/ directory
        custom_model_path = os.path.join(os.path.dirname(__file__), "models", f"{wakeword_phrase}.onnx")
        
        if os.path.exists(custom_model_path):
            print(f"Found custom model at {custom_model_path}")
            self.model = Model(wakeword_models=[custom_model_path], inference_framework="onnx")
            self.keyword = wakeword_phrase
        else:
            print(f"Custom model '{wakeword_phrase}.onnx' not found! Falling back to 'alexa'.")
            self.model = Model(wakeword_models=["alexa"], inference_framework="onnx")
            self.keyword = "alexa"
            
        self.threshold = threshold

    def detect(self, chunk_f32: np.ndarray) -> bool:
        """
        Takes the base float32 [-1, 1] chunk from the microphone stream
        and converts it to standard 16-bit PCM expected heavily by openwakeword
        """
        # Convert audio array from float32 to int16 (what openwakeword expects natively)
        chunk_i16 = (chunk_f32 * 32767).astype(np.int16).flatten()
        
        # Predict updates the state of the model and returns the score dictionary
        prediction = self.model.predict(chunk_i16)
        
        # Get the score for our specific keyword
        for model_name, score in prediction.items():
            if self.keyword in model_name.lower():
                if score > self.threshold:
                    return True
                    
        return False

if __name__ == "__main__":
    engine = WakewordEngine()
    print("Wakeword ready!")
