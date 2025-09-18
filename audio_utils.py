# app/audio_utils.py
#imports
import os
import tempfile
import numpy as np
import sounddevice as sd
from pathlib import Path
from config import whisper_model, WHISPER_MODEL


# ------------------------------
# Constants (Whisper expects 16kHz mono input)
# ------------------------------
SAMPLE_RATE = 16000  # 16 kHz mono

# ------------------------------
# Local Microphone Recording
# ------------------------------
def record_audio(duration: int = 5) -> np.ndarray:
    """
    Record audio from the microphone.
    Returns a float32 NumPy array.
    """
    print(f"🎙️ Recording {duration} seconds...")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="float32")
    sd.wait()
    print("✅ Recording complete.")
    return audio

def save_wav(audio: np.ndarray, fs: int = SAMPLE_RATE) -> str:
    """
    Save a NumPy float32 array to WAV (16kHz mono).
    Returns the file path.
    """
    import wave

    temp_file = tempfile.mktemp(suffix=".wav")
    audio_int16 = (audio * 32767).astype(np.int16)
    
    with wave.open(temp_file, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(fs)
        wf.writeframes(audio_int16.tobytes())

    print(f"💾 Audio saved to {temp_file}")
    return temp_file

# ------------------------------
# Handle Twilio / Uploaded Bytes
# ------------------------------
def save_wav_from_bytes(audio_bytes: bytes) -> str:
    """
    Convert Twilio/other audio bytes (MP3, WAV, etc.) to 16kHz mono WAV using ffmpeg.
    Returns the path to the WAV file.
    """
    import tempfile
    import ffmpeg
    import mimetypes

    # Save bytes to temp input file with proper extension
    temp_in = tempfile.mktemp(suffix=".mp3")  # Twilio usually sends MP3
    with open(temp_in, "wb") as f:
        f.write(audio_bytes)

    # Temp output WAV file
    temp_out = tempfile.mktemp(suffix=".wav")

    # Convert to 16kHz mono WAV
    try:
        ffmpeg.input(temp_in, f='mp3').output(temp_out, ar=16000, ac=1).run(
            overwrite_output=True, capture_stdout=True, capture_stderr=True
        )
    except ffmpeg.Error as e:
        print("⚠️ FFmpeg conversion failed:", e.stderr.decode())
        raise
    finally:
        import os
        os.remove(temp_in)

    print(f"💾 Converted uploaded audio to WAV: {temp_out}")
    return temp_out


# ------------------------------
# Whisper Transcription
# ------------------------------
def transcribe_audio(audio_path: str) -> str:
    """
    Convert speech to text using Whisper model.
    Returns the transcribed text.
    """
    if not Path(audio_path).exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"🔎 Transcribing audio ({WHISPER_MODEL})...")
    try:
        result = whisper_model.transcribe(audio_path)
        text = result.get("text", "").strip()
    except Exception as e:
        print("⚠️ Whisper transcription failed:", str(e))
        raise

    print("📝 You said:", text)
    return text


# app/audio_utils.py
from gtts import gTTS

def text_to_speech(text: str, output_path: str):
    """
    Convert AI text to speech and save as mp3.
    """
    tts = gTTS(text=text, lang='en')
    tts.save(output_path)
