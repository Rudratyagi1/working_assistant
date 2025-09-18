# test_call.py
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

# Twilio credentials from .env
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
MY_NUMBER = os.getenv("MY_PHONE_NUMBER")

client = Client(TWILIO_SID, TWILIO_TOKEN)

# Make the call
call = client.calls.create(
    to=MY_NUMBER,
    from_=TWILIO_NUMBER,
    url="https://d638852df1c0.ngrok-free.app/voice"  # Your public Ngrok HTTPS URL
)

print("✅ Call initiated:", call.sid)
 

