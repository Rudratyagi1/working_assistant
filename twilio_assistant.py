from fastapi import FastAPI, Form, BackgroundTasks, Response
from twilio.twiml.voice_response import VoiceResponse
from requests.auth import HTTPBasicAuth
import requests, tempfile, os, ffmpeg, uuid
from config import TWILIO_SID, TWILIO_TOKEN
from audio_utils import transcribe_audio
from assistant import ask_gemini

app = FastAPI(title="Twilio Voice Assistant")
SAMPLE_RATE = 16000

# -----------------------------
# Start Call
# ------------------------------
@app.post("/voice")
async def voice_webhook():
    response = VoiceResponse()
    response.say(
        "Hello! You are connected to the AI assistant. Please speak after the beep.",
        voice="alice"
    )
    response.record(
        action="/handle_speech",
        max_length=15,
        play_beep=True,
        trim="do-not-trim"
    )
    return Response(content=str(response), media_type="application/xml")

# ------------------------------
# Background AI Processing
# ------------------------------
def process_audio(recording_url: str):
    # Download audio
    resp = requests.get(recording_url, auth=HTTPBasicAuth(TWILIO_SID, TWILIO_TOKEN))
    audio_data = resp.content
    if not audio_data or len(audio_data) < 1000:
        return "⚠️ Could not process your speech."

    # Save temp input
    temp_in = tempfile.mktemp(suffix=".mp3")
    with open(temp_in, "wb") as f:
        f.write(audio_data)

    # Convert to WAV 16kHz mono
    temp_out = tempfile.mktemp(suffix=".wav")
    ffmpeg.input(temp_in).output(temp_out, ar=SAMPLE_RATE, ac=1).run(
        overwrite_output=True, capture_stdout=True, capture_stderr=True
    )
    os.remove(temp_in)

    # Transcribe
    text = transcribe_audio(temp_out)
    print(f"📝 Transcript: {text}")

    # Get AI reply
    reply_text = ask_gemini(text) if text else "⚠️ Could not understand."
    print(f"💬 AI Reply: {reply_text}")
    return reply_text

# ------------------------------
# Handle Recorded Speech
# ------------------------------
@app.post("/handle_speech")
async def handle_speech(RecordingUrl: str = Form(...), background_tasks: BackgroundTasks = None):
    # Process AI reply synchronously
    ai_reply = process_audio(RecordingUrl)

    response = VoiceResponse()
    response.say(ai_reply, voice="alice")  # Twilio native TTS, no files

    # Record next input for multi-turn conversation
    response.record(
        action="/handle_speech",
        max_length=15,
        play_beep=True,
        trim="do-not-trim"
    )
    return Response(content=str(response), media_type="application/xml")
