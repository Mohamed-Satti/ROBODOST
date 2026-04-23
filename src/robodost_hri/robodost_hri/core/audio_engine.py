import sounddevice as sd
import numpy as np
import queue

class AudioEngine:
    def __init__(self, sample_rate=16000, chunk_size=512):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio_queue = queue.Queue()
        self.stream = None

    def _callback(self, indata, frames, time, status):
        """This is called continuously by sounddevice for each audio chunk"""
        if status:
            print(f"Audio status: {status}")
        # Store a copy of the chunk into the queue immediately
        self.audio_queue.put(indata.copy())

    def start_listening(self):
        """Starts the non-blocking audio stream"""
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
