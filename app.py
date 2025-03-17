import os
import logging
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile
from audio_utils import convert_to_wav, cleanup_files

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure upload settings
ALLOWED_EXTENSIONS = {'m4a', 'wav', 'mp3'}
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не предоставлен'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Неверный формат файла. Пожалуйста, загрузите аудио файл (m4a, wav, mp3)'}), 400

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Check if we need to split audio
        split_audio = request.form.get('split_audio', 'false').lower() == 'true'

        # Convert and potentially split audio
        wav_files = convert_to_wav(filepath, split=split_audio)

        # Get the selected service
        service = request.form.get('service', 'google')  # Default to Google

        if service == 'openai':
            from transcription import transcribe_audio
        else:
            from google_transcription import transcribe_audio

        # Process each part
        results = []
        for wav_file in wav_files:
            try:
                text = transcribe_audio(wav_file)
                results.append(text)
            except Exception as e:
                logger.error(f"Ошибка распознавания части аудио: {str(e)}")
                results.append(f"Ошибка распознавания: {str(e)}")

        # Clean up temporary files
        cleanup_files([filepath] + wav_files)

        # Return results
        if len(results) == 1:
            return jsonify({
                'success': True,
                'text': results[0]
            })
        else:
            return jsonify({
                'success': True,
                'text': '\n\n'.join(results),
                'parts': results
            })

    except Exception as e:
        logger.error(f"Ошибка транскрипции: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download_transcription():
    try:
        text = request.json.get('text', '')
        if not text:
            return jsonify({'error': 'Текст не предоставлен'}), 400

        # Create temporary file for download
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt')
        temp_file.write(text)
        temp_file.close()

        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name='transcription.txt',
            mimetype='text/plain'
        )

    except Exception as e:
        logger.error(f"Ошибка скачивания: {str(e)}")
        return jsonify({'error': str(e)}), 500