import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pytube import YouTube
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise ValueError("OpenAI API key not found. Make sure you have a .env file with OPENAI_API_KEY set.")
except Exception as e:
    print(e)

def get_transcript_from_youtube(url):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        print("Downloading audio...")
        audio_file_path = audio_stream.download(filename="temp_audio.mp4")
        print("Download complete.")
        
        with open(audio_file_path, "rb") as audio_file:
            print("Transcribing with Whisper...")
            transcript_object = openai.audio.transcriptions.create(
              model="whisper-1", 
              file=audio_file
            )
            print("Transcription complete.")
        
        os.remove(audio_file_path)
        
        return transcript_object.text

    except Exception as e:
        print(f"An error occurred: {e}")
        if os.path.exists("temp_audio.mp4"):
            os.remove("temp_audio.mp4")
        return None

@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    data = request.get_json()
    youtube_url = data.get('url')

    if not youtube_url:
        return jsonify({"error": "YouTube URL is required"}), 400

    print(f"Received URL: {youtube_url}")
    transcript = get_transcript_from_youtube(youtube_url)

    if transcript:
        return jsonify({"transcript": transcript})
    else:
        return jsonify({"error": "Failed to transcribe video. Check the URL and server logs."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

