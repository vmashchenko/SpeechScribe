import speech_recognition as sr
import os
import logging

logger = logging.getLogger(__name__)

def transcribe_audio(audio_file_path):
    """
    Transcribe audio file using Google Speech Recognition
    """
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Load the audio file
        with sr.AudioFile(audio_file_path) as source:
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
