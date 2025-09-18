from fastapi import FastAPI, Form, Response
from twilio.twiml.voice_response import VoiceResponse
from requests.auth import HTTPBasicAuth
import requests, tempfile, os, ffmpeg
from app.config import TWILIO_SID, TWILIO_TOKEN
from app.audio_utils import transcribe_audio
from app.assistant import ask_gemini

app = FastAPI(title="Twilio Voice Assistant")
SAMPLE_RATE = 16000


# -----------------------------
# Start Call
# ------------------------------
@app.post("/voice")
async def voice_webhook():
    """Initial webhook: greet user and start recording."""
    response = VoiceResponse()
    response.say(
        "Hello! You are connected to the AI assistant. Please speak after the beep.",
        voice="alice"
    )
    response.record(
        action="/handle_speech",
        max_length=15,          # seconds per turn
        play_beep=True,
        trim="do-not-trim"
    )
    return Response(content=str(response), media_type="application/xml")


# ------------------------------
# Background AI Processing
# ------------------------------
def process_audio(recording_url: str) -> str:
    """Download, convert, transcribe, and generate AI reply."""
    try:
        # Download audio
        resp = requests.get(recording_url, auth=HTTPBasicAuth(TWILIO_SID, TWILIO_TOKEN))
        audio_data = resp.content
        if not audio_data or len(audio_data) < 1000:
            return "⚠️ I couldn’t hear you properly. Please try again."

        # Save temp input MP3
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_in:
            temp_in.write(audio_data)
            temp_in_path = temp_in.name

        # Convert to WAV 16kHz mono
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_out:
            temp_out_path = temp_out.name

        ffmpeg.input(temp_in_path).output(
            temp_out_path, ar=SAMPLE_RATE, ac=1
        ).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)

        os.remove(temp_in_path)  # cleanup input mp3

        # Transcribe
        text = transcribe_audio(temp_out_path)
        print(f"📝 Transcript: {text}")

        # Get AI reply
        reply_text = ask_gemini(text) if text else "⚠️ I didn’t catch that."
        print(f"💬 AI Reply: {reply_text}")
        return reply_text

    except Exception as e:
        print(f"❌ Error in process_audio: {e}")
        return "⚠️ Sorry, something went wrong while processing your voice."


# ------------------------------
# Handle Recorded Speech
# ------------------------------
@app.post("/handle_speech")
async def handle_speech(RecordingUrl: str = Form(...)):
    """Looping speech handler: process input, reply, and re-record."""
    # Always produce a safe AI reply
    ai_reply = process_audio(RecordingUrl)

    # Build TwiML
    response = VoiceResponse()
    response.say(ai_reply, voice="alice")

    # 🔄 Loop forever until user hangs up
    response.record(
        action="/handle_speech",
        max_length=15,
        play_beep=True,
        trim="do-not-trim"
    )

    return Response(content=str(response), media_type="application/xml")
