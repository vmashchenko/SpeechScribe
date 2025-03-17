import os
import logging
from pydub import AudioSegment
import tempfile

logger = logging.getLogger(__name__)

def split_audio(audio_segment, max_duration_sec=59):
    """
    Split audio into chunks of specified duration
    """
    parts = []
    length_ms = len(audio_segment)
    max_duration_ms = max_duration_sec * 1000
    
    for i in range(0, length_ms, max_duration_ms):
        end = min(i + max_duration_ms, length_ms)
        part = audio_segment[i:end]
        
        # Create temporary file for the part
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        part.export(temp_file.name, format='wav')
        parts.append(temp_file.name)
        
    return parts

def convert_to_wav(input_path, split=False):
    """
    Convert audio file to WAV format and optionally split into parts
    """
    try:
        # Get the file extension
        ext = os.path.splitext(input_path)[1].lower()
        
        # Load audio file
        audio = AudioSegment.from_file(input_path)
        
        if split:
            # Split audio into parts
            return split_audio(audio)
        else:
            # Convert to WAV if not already
            if ext != '.wav':
                wav_path = tempfile.mktemp(suffix='.wav')
                audio.export(wav_path, format='wav')
                return [wav_path]
            return [input_path]
            
    except Exception as e:
        raise Exception(f"Ошибка обработки аудио: {str(e)}")

def cleanup_files(file_paths):
    """
    Clean up temporary files
    """
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.error(f"Ошибка при удалении временного файла {path}: {str(e)}")
