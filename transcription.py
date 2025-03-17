import os
from openai import OpenAI, OpenAIError

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

openai = OpenAI(api_key=OPENAI_API_KEY)

def transcribe_audio(audio_file_path):
    """
    Transcribe audio file using OpenAI Whisper API
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return response.text
    except OpenAIError as e:
        if "insufficient_quota" in str(e):
            raise Exception(
                "Your OpenAI account has reached its usage limit. "
                "Please check your billing details at: "
                "https://platform.openai.com/account/billing"
            )
        raise Exception(f"Transcription failed: {str(e)}")