import sounddevice as sd
import numpy as np
import queue
import subprocess
import threading
import urllib.request

class AudioEngine:
    def __init__(self, sample_rate=16000, chunk_size=512, ip_stream_url=None):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.ip_stream_url = ip_stream_url
        self.audio_queue = queue.Queue()
        self.stream = None
        
        # ffmpeg specific variables
        self.ffmpeg_process = None
        self.ffmpeg_thread = None
        self._stop_ffmpeg = False

    def _callback(self, indata, frames, time, status):
        """This is called continuously by sounddevice for each audio chunk"""
        if status:
            print(f"Audio status: {status}")
        # Store a copy of the chunk into the queue immediately
        self.audio_queue.put(indata.copy())

    def _ffmpeg_reader_thread(self):
        """Runs ffmpeg as a subprocess to stream from an IP camera"""
        print(f"Starting ffmpeg IP stream from {self.ip_stream_url}...")
        self.ffmpeg_process = subprocess.Popen(
            [
                "ffmpeg",
                "-loglevel", "quiet",
                "-i", self.ip_stream_url,
                "-f", "s16le",
                "-ac", "1",
                "-ar", str(self.sample_rate),
                "-"
            ],
            stdout=subprocess.PIPE,
            bufsize=10**8
        )
        
        # We need chunk_size * 2 bytes because 16-bit PCM uses 2 bytes per sample
        bytes_to_read = self.chunk_size * 2
        
        while not self._stop_ffmpeg:
            in_bytes = self.ffmpeg_process.stdout.read(bytes_to_read)
            if not in_bytes:
                print("[AudioEngine] FFMPEG stream ended or disconnected.")
                break
            
            # Convert bytes -> int16 array
            audio_data_int16 = np.frombuffer(in_bytes, dtype=np.int16)
            
            # Convert int16 array -> float32 array in range [-1.0, 1.0]
            audio_data_float32 = audio_data_int16.astype(np.float32) / 32768.0
            
            # Put in queue (reshaped to match sounddevice: (chunk_size, 1))
            self.audio_queue.put(audio_data_float32.reshape(-1, 1))
            
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()

    def start_listening(self):
        """Starts the non-blocking audio stream"""
        use_ip = False
        if self.ip_stream_url:
            print(f"[AudioEngine] Verifying IP stream {self.ip_stream_url}...")
            try:
                # Quickly ping the URL to make sure the phone app is running
                req = urllib.request.urlopen(self.ip_stream_url, timeout=2.0)
                req.close()
                use_ip = True
                print("[AudioEngine] IP stream is active.")
            except Exception as e:
                print(f"[AudioEngine] ⚠️ WARNING: IP stream unreachable ({e}). Falling back to system microphone!")
                
        if use_ip:
            self._stop_ffmpeg = False
            self.ffmpeg_thread = threading.Thread(target=self._ffmpeg_reader_thread, daemon=True)
            self.ffmpeg_thread.start()
        else:
            print("[AudioEngine] Starting local hardware microphone stream...")
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                blocksize=self.chunk_size,
                callback=self._callback
            )
            self.stream.start()

    def stop_listening(self):
        """Gracefully close the audio stream"""
        if self.ip_stream_url:
            self._stop_ffmpeg = True
            if self.ffmpeg_process:
                self.ffmpeg_process.terminate()
            if self.ffmpeg_thread:
                self.ffmpeg_thread.join(timeout=1.0)
        else:
            if self.stream is not None:
                self.stream.stop()
                self.stream.close()

    def get_chunk(self, block=True, timeout=None):
        """Pulls the next available chunk out of the queue"""
        try:
            return self.audio_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def flush(self):
        """Empties the queue to clear any buffered noise (like the robot's own speaker audio)"""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

if __name__ == '__main__':
    # Initialize your class and print audio arrays to test!
    engine = AudioEngine()
    engine.start_listening()
    print("Listening... Press Ctrl+C to stop.")
    try:
        while True:
            chunk = engine.get_chunk()
            if chunk is not None:
                # Print the RMS (volume) to prove it works
                rms = np.sqrt(np.mean(chunk**2))
                print(f"Volume: {rms:.5f}", end='\\r')
    except KeyboardInterrupt:
        engine.stop_listening()
        print("\\nStopped.")
