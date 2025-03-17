import speech_recognition as sr
import os
import logging
from pydub import AudioSegment
import tempfile

logger = logging.getLogger(__name__)

def convert_to_wav(input_path):
    """
    Convert audio file to WAV format
    """
    try:
        # Get the file extension
        ext = os.path.splitext(input_path)[1].lower()

        # Convert if not already WAV
        if ext != '.wav':
            audio = AudioSegment.from_file(input_path)
            wav_path = tempfile.mktemp(suffix='.wav')
            audio.export(wav_path, format='wav')
            return wav_path
        return input_path
    except Exception as e:
        raise Exception(f"Ошибка конвертации аудио: {str(e)}")

def transcribe_audio(audio_file_path):
    """
    Transcribe audio file using Google Speech Recognition
    """
    wav_path = None
    try:
        # Convert to WAV if needed
        wav_path = convert_to_wav(audio_file_path)

        # Initialize recognizer
        recognizer = sr.Recognizer()

        # Load the audio file
        with sr.AudioFile(wav_path) as source:
            # Read the audio data
            audio_data = recognizer.record(source)

            # Recognize speech using Google Speech Recognition
            text = recognizer.recognize_google(audio_data, language="ru-RU")
            return text

    except sr.UnknownValueError:
        raise Exception("Google Speech Recognition не смог распознать аудио")
    except sr.RequestError as e:
        raise Exception(f"Ошибка сервиса Google Speech Recognition; {str(e)}")
    except Exception as e:
        raise Exception(f"Ошибка при распознавании: {str(e)}")
    finally:
        # Clean up temporary WAV file if it was created
        if wav_path and wav_path != audio_file_path:
            try:
                os.remove(wav_path)
            except:
                pass