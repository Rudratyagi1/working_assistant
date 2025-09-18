import os
from dotenv import load_dotenv
import whisper
from google import genai
import pyttsx3

# ------------------------------
# Load .env
# ------------------------------
load_dotenv()

# ------------------------------
# Twilio
# ------------------------------
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
MY_NUMBER = os.getenv("MY_PHONE_NUMBER")

# ------------------------------
# Gemini AI
# ------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in .env")
client = genai.Client()  # automatically reads GEMINI_API_KEY

# ------------------------------
# Whisper
# ------------------------------
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
whisper_model = whisper.load_model(WHISPER_MODEL)

# ------------------------------
# FastAPI host/port
# ------------------------------
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8000))


# TTS
TTS_VOICE = os.getenv("TTS_VOICE", "alice")
TTS_RATE = int(os.getenv("TTS_RATE", 150))
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", TTS_RATE)
tts_engine.setProperty("voice", TTS_VOICE)
tts_engine.setProperty("volume", 1.0)


def speak(text: str):
    tts_engine.say(text)
    tts_engine.runAndWait()
