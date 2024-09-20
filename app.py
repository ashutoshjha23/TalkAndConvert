from flask import Flask, render_template, request, jsonify, send_from_directory
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile

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
    tts = gTTS(text=text, lang='en')
    
    # Use a temporary file to store the audio
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        tts.save(tmp_file.name)
        audio_url = f"/audio/{os.path.basename(tmp_file.name)}"
        return jsonify({'audio_url': audio_url})

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(tempfile.gettempdir(), filename)

if __name__ == '__main__':
    app.run(debug=True)
