from flask import Flask, render_template, request, jsonify, send_from_directory
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
from pydub import AudioSegment
from pydub.playback import play

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/recognize', methods=['POST'])
def recognize():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            return {'text': text}
        except sr.UnknownValueError:
            return {'error': 'Could not understand audio'}
        except sr.RequestError as e:
            return {'error': f'Could not request results; {e}'}

@app.route('/speak', methods=['POST'])
def speak():
    text = request.form['text']
    pitch = float(request.form.get('pitch', 1.0)) 

    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        tts.save(tmp_file.name)
    audio = AudioSegment.from_mp3(tmp_file.name)
    new_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * pitch)})
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    new_audio.export(output_file.name, format="mp3")

    audio_url = f"/audio/{os.path.basename(output_file.name)}"
    return jsonify({'audio_url': audio_url})

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(tempfile.gettempdir(), filename)

if __name__ == '__main__':
    app.run(debug=True)
