# app/assistant.py
from config import client ,speak

def ask_gemini(prompt: str, model_name: str = "gemini-2.0-flash-exp") -> str:
    """Send text to Gemini / GPT model and get response"""
    if not prompt.strip():
        return "⚠️ No prompt provided."

    print("🤖 Thinking...")
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    text = getattr(response, "text", "")
    print("💬 Assistant:", text)

    # Remove local TTS; Twilio <Say> will handle speech
    # if text:
    #     speak(text)

    return text
