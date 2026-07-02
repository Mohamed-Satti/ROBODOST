from flask import Flask, render_template
from flask_socketio import SocketIO
from robodost_hri.core.speech_pipeline import SpeechPipeline

app = Flask(__name__)
app.config['SECRET_KEY'] = 'robodost_secret!'
# async_mode='eventlet' is highly recommended for performance, but threading works as fallback
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

pipeline = None

def pipeline_event_callback(event_name, data):
    """
    This callback is passed to the SpeechPipeline.
    Whenever the pipeline changes state or generates text, it fires this,
    and we immediately push it to the connected Web UI clients.
    """
    socketio.emit(event_name, data)

def start_pipeline():
    global pipeline
    if pipeline is None:
        print("[Flask] Initializing Speech Pipeline...")
        pipeline = SpeechPipeline(event_callback=pipeline_event_callback)
        # Run it (this will block this thread, which is fine since we ran it as a background task)
        pipeline.run()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def test_connect():
    print("[Flask] Client connected to Web Dashboard")

@socketio.on('get_models')
def handle_get_models():
    if pipeline:
        models = pipeline.get_llm_models()
        socketio.emit('models_list', models)

@socketio.on('update_settings')
def handle_update_settings(data):
    if pipeline:
        pipeline.update_settings(
            llm_model=data.get('llm_model'),
            ip_stream_url=data.get('ip_stream_url'),
            asr_lang=data.get('asr_lang'),
            tts_lang=data.get('tts_lang')
        )

if __name__ == '__main__':
    # Start the speech pipeline in a background task
    print("Starting pipeline thread...")
    socketio.start_background_task(start_pipeline)
    
    # Start the web server
    print("Starting Web Dashboard on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
