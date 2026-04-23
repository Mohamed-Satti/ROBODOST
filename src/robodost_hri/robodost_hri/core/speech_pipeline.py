import numpy as np
import time
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
except ImportError:
    from audio_engine import AudioEngine
    from vad_engine import VadEngine
    from asr_engine import AsrEngine
    from tts_engine import TtsEngine

class SpeechPipeline:
    def __init__(self, silence_patience=15):
        """
        silence_patience: Number of consecutive silent chunks to endure
        before deciding the user has finished speaking.
        (15 chunks * 512 frames @ 16kHz ≈ 0.48 seconds of silence)
        """
        print("Initializing Speech Pipeline Components...")
        self.audio = AudioEngine()
        self.vad = VadEngine()
        self.asr = AsrEngine()
        self.tts = TtsEngine()
        self.wakeword = WakewordEngine()
        
        self.silence_patience = silence_patience
        self.audio_buffer = []
        
        # Finite State Machine states
        self.is_awake = False
        self.is_recording = False
        self.silence_frames = 0
        
        print("Pipeline Ready.")

    def run(self):
        print("Starting microphone stream. Speak into your laptop!")
        self.audio.start_listening()
        
        try:
            print("\n[SLEEP MODE] Waiting for wakeword 'alexa'...")
            while True:
                chunk = self.audio.get_chunk(block=True)
                if chunk is None:
                    continue
                
                # ------ STATE 1: ASLEEP (Awaiting Wake Word) ------
                if not self.is_awake:
                    if self.wakeword.detect(chunk):
                        print("\n[WAKE] Wake word detected! Listening for command...")
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
                            self._transcribe_buffer()
                            
                            # Return to Sleep State
                            self.is_recording = False
                            self.is_awake = False
                            self.audio_buffer = []
                            print("\n[SLEEP MODE] Waiting for wakeword 'alexa'...")

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
            print(f"\n---> 🤖 Transcript: \"{text}\" (Latency: {latency:.2f}s)\n")
            
            # ECHO BOT LOGIC: The robot will repeat what it heard back to you!
            self.tts.speak(text)
            
            # Flush the mic queue so the pipeline doesn't instantly transcribe the robot's own voice
            self.audio.flush()

if __name__ == "__main__":
    pipeline = SpeechPipeline()
    pipeline.run()
