import numpy as np
import openwakeword
from openwakeword.model import Model

class WakewordEngine:
    def __init__(self, wakeword_phrase="alexa", threshold=0.5):
        # NOTE: openwakeword will automatically download the pre-trained onnx model for "alexa" to .cache 
        print(f"Loading WakeWord Engine: [{wakeword_phrase}]")
        openwakeword.utils.download_models() # ensures built-ins are ready
        
        # TODO: To train a customized "hey robodost" model offline:
        # Run the scripts from openWakeWord repository. You will just need an ONNX file produced
        # by their generator and place it into models/ and pass inference_framework=\"onnx\" and 
        # wakeword_models=[\"models/hey_robodost.onnx\"] to the Model configuration below.
        
        self.model = Model(wakeword_models=[wakeword_phrase], inference_framework="onnx")
        self.keyword = wakeword_phrase
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
