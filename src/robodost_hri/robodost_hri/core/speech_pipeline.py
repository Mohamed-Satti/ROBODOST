import os
import sys
import numpy as np
import time

# Add robodost_llm to path so we can import it directly for testing
llm_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../robodost_llm/robodost_llm"))
sys.path.append(llm_path)

try:
    from .audio_engine import AudioEngine
    from .vad_engine import VadEngine
    from .asr_engine import AsrEngine
    from .tts_engine import TtsEngine
    from .wakeword_engine import WakewordEngine
except ImportError:
    from audio_engine import AudioEngine
    from vad_engine import VadEngine
    from asr_engine import AsrEngine
    from tts_engine import TtsEngine
    from wakeword_engine import WakewordEngine

try:
    from llm_engine import LlmEngine
except ImportError as e:
    print(f"Warning: Could not import LlmEngine. Error: {e}")

class SpeechPipeline:
    def __init__(self, silence_patience=15, event_callback=None):
        """
        silence_patience: Number of consecutive silent chunks to endure
        before deciding the user has finished speaking.
        (15 chunks * 512 frames @ 16kHz ≈ 0.48 seconds of silence)
        """
        print("Initializing Speech Pipeline Components...")
        # To go back to using a hardware microphone, simply remove the ip_stream_url parameter
        self.audio = AudioEngine(ip_stream_url="http://192.168.1.103:8080/audio.wav")
        self.vad = VadEngine()
        self.asr = AsrEngine()
        self.tts = TtsEngine()
        self.wakeword = WakewordEngine()
        self.llm = LlmEngine()
        
        self.event_callback = event_callback
        self.silence_patience = silence_patience
        self.audio_buffer = []
        
        # Finite State Machine states
        self.is_awake = False
        self.is_recording = False
        self.silence_frames = 0
        
        print("Pipeline Ready.")

    def _emit(self, event_name, data):
        if self.event_callback:
            self.event_callback(event_name, data)

    def get_llm_models(self):
        return self.llm.get_available_models()

    def update_settings(self, llm_model=None, ip_stream_url=None, asr_lang=None, tts_lang=None):
        print(f"[Pipeline] Updating settings: LLM={llm_model}, ASR={asr_lang}, TTS={tts_lang}, IP={ip_stream_url}")
        if llm_model:
            self.llm.set_model(llm_model)
        if asr_lang:
            self.asr.set_language(asr_lang)
            if hasattr(self.llm, 'set_language'):
                self.llm.set_language(asr_lang)
        if tts_lang:
            self.tts.set_voice(tts_lang)
        if ip_stream_url is not None and ip_stream_url != self.audio.ip_stream_url:
            self.audio.stop_listening()
            self.audio.ip_stream_url = ip_stream_url if ip_stream_url.strip() else None
            self.audio.start_listening()

    def run(self):
        print("Starting microphone stream. Speak into your laptop!")
        self._emit('status', 'STARTING')
        self.audio.start_listening()
        
        try:
            print("\n[SLEEP MODE] Waiting for wakeword 'alexa'...")
            self._emit('status', 'ASLEEP')
            while True:
                chunk = self.audio.get_chunk(block=True)
                if chunk is None:
                    continue
                
                # ------ STATE 1: ASLEEP (Awaiting Wake Word) ------
                if not self.is_awake:
                    if self.wakeword.detect(chunk):
                        print("\n[WAKE] Wake word detected! Listening for command...")
                        self._emit('status', 'LISTENING')
                        self.is_awake = True
                        self.is_recording = True
                        self.silence_frames = 0
                        self.audio_buffer = []
                    continue
                
                # ------ STATE 2: AWAKE (Recording user command) ------
                # TODO: To implement True Barge-in (interrupting TTS), the TTS engine must play 
                # in a background thread, and this loop must continuously call self.wakeword.detect() 
                # even while transcribing or awaiting TTS, throwing an interrupt flag to stop TTS.
                
                is_speech = self.vad.is_speech(chunk)
                
                if is_speech:
                    if not self.is_recording:
                        # Should rarely hit this since Wakeword auto-starts recording
                        self.is_recording = True
                    self.silence_frames = 0
                    self.audio_buffer.append(chunk)
                else:
                    if self.is_recording:
                        # User stopped speaking but we give them a little bit of patience
                        self.silence_frames += 1
                        self.audio_buffer.append(chunk)
                        
                        if self.silence_frames > self.silence_patience:
                            print("\n[VAD] Silence detected. Transcribing...")
                            self._emit('status', 'THINKING')
                            self._transcribe_buffer()
                            
                            # Return to Sleep State
                            self.is_recording = False
                            self.is_awake = False
                            self.audio_buffer = []
                            self.audio.flush()  # Flush the queue so we don't immediately re-trigger
                            print("\n[SLEEP MODE] Waiting for wakeword 'alexa'...")
                            self._emit('status', 'ASLEEP')

        except KeyboardInterrupt:
            print("\nShutting down pipeline.")
            self.audio.stop_listening()

    def _transcribe_buffer(self):
        if not self.audio_buffer:
            return
            
        # Combine all the collected chunks into one contiguous flat numpy array
        full_audio = np.concatenate(self.audio_buffer)
        
        # We don't want to transcribe extremely short noises (e.g. a keyboard click)
        # 16000 hz * 0.3s = 4800 frames. If it's shorter than 4800 total elements, ignore it.
        if len(full_audio) < 4800:
            print("[ASR] Audio too short to be speech. Ignored.")
            return

        start_time = time.time()
        text = self.asr.transcribe(full_audio)
        latency = time.time() - start_time
        
        if text:
            print(f"\n---> 🗣️ User: \"{text}\" (ASR Latency: {latency:.2f}s)\n")
            self._emit('transcript', {'role': 'user', 'text': text})
            
            # Send to LLM
            print(f"\n---> 🤖 ROBODOST: ", end="", flush=True)
            self._emit('status', 'SPEAKING')
            
            full_response = ""
            for chunk in self.llm.generate_stream(text):
                print(chunk + " ", end="", flush=True)
                full_response += chunk + " "
                
                # Incrementally update UI
                self._emit('transcript', {'role': 'robot', 'text': full_response})
                
                # Speak chunk incrementally
                self.tts.speak(chunk)
                
            print("\n")
            
            # Flush the mic queue so the pipeline doesn't instantly transcribe the robot's own voice
            self.audio.flush()

if __name__ == "__main__":
    pipeline = SpeechPipeline()
    pipeline.run()
