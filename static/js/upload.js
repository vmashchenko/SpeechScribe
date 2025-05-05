document.addEventListener('DOMContentLoaded', function() {
    const audioFileInput = document.getElementById('audioFile');
    const uploadBtn = document.getElementById('uploadBtn');
    const progressSection = document.getElementById('progressSection');
    const resultSection = document.getElementById('resultSection');
    const errorSection = document.getElementById('errorSection');
    const transcriptionResults = document.getElementById('transcriptionResults');
    const downloadBtn = document.getElementById('downloadBtn');
    const errorMessage = document.getElementById('errorMessage');
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.getElementById('progressText');
    const splitAudioCheckbox = document.getElementById('splitAudio');

    // Enable upload button only when files are selected
    audioFileInput.addEventListener('change', function() {
        uploadBtn.disabled = !this.files.length;
        resetUI();
    });

    // Handle file upload and transcription
    uploadBtn.addEventListener('click', async function() {
        const files = Array.from(audioFileInput.files);
        if (!files.length) return;

        resetUI();
        showProgress();

        const results = [];
        let completed = 0;

        for (const file of files) {
            try {
                const formData = new FormData();
                formData.append('file', file);
                const service = document.querySelector('input[name="service"]:checked').value;
                formData.append('service', service);
                formData.append('split_audio', splitAudioCheckbox.checked);

                progressText.textContent = `Обработка файла ${file.name} (${completed + 1}/${files.length})...`;
                progressBar.style.width = `${(completed / files.length) * 100}%`;
                progressBar.setAttribute('aria-valuenow', (completed / files.length) * 100);

                const response = await fetch('/transcribe', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(`${file.name}: ${data.error || 'Ошибка распознавания'}`);
                }

                results.push({
                    filename: file.name,
                    text: data.text,
                    parts: data.parts || null
                });

                completed++;
                progressBar.style.width = `${(completed / files.length) * 100}%`;
                progressBar.setAttribute('aria-valuenow', (completed / files.length) * 100);

            } catch (error) {
                results.push({
                    filename: file.name,
                    error: error.message
                });
            }
        }

        showResults(results);
    });

    // Handle download functionality
    downloadBtn.addEventListener('click', async function() {
        try {
            const textElements = document.querySelectorAll('.transcription-text');
            const allText = Array.from(textElements).map(el => {
                const filename = el.getAttribute('data-filename');
                const text = el.value;
                return `=== ${filename} ===\n\n${text}\n\n`;
            }).join('\n');

            const response = await fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: allText })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Ошибка скачивания');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'transcription_results.txt';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            showError(error.message);
        }
    });

    function resetUI() {
        progressSection.classList.add('d-none');
        resultSection.classList.add('d-none');
        errorSection.classList.add('d-none');
        transcriptionResults.innerHTML = '';
        progressBar.style.width = '0%';
        progressBar.setAttribute('aria-valuenow', 0);
    }

    function showProgress() {
        progressSection.classList.remove('d-none');
        uploadBtn.disabled = true;
    }

    function showResults(results) {
        progressSection.classList.add('d-none');
        resultSection.classList.remove('d-none');
        uploadBtn.disabled = false;

        transcriptionResults.innerHTML = '';

        results.forEach(result => {
            const resultDiv = document.createElement('div');
            resultDiv.className = 'mb-3';

            const header = document.createElement('h6');
            header.className = 'mb-2';
            header.textContent = result.filename;

            resultDiv.appendChild(header);

            if (result.error) {
                const errorAlert = document.createElement('div');
                errorAlert.className = 'alert alert-danger';
                errorAlert.textContent = result.error;
                resultDiv.appendChild(errorAlert);
            } else if (result.parts) {
                result.parts.forEach((part, index) => {
                    const textarea = document.createElement('textarea');
                    textarea.className = 'form-control transcription-text mb-2';
                    textarea.rows = 4;
                    textarea.readOnly = true;
                    textarea.value = part;
                    textarea.setAttribute('data-filename', `${result.filename}_part${index + 1}`);
                    resultDiv.appendChild(textarea);
                });
            } else {
                const textarea = document.createElement('textarea');
                textarea.className = 'form-control transcription-text';
                textarea.rows = 4;
                textarea.readOnly = true;
                textarea.value = result.text;
                textarea.setAttribute('data-filename', result.filename);
                resultDiv.appendChild(textarea);
            }

            transcriptionResults.appendChild(resultDiv);
        });
    }

    function showError(message) {
        progressSection.classList.add('d-none');
        errorSection.classList.remove('d-none');
        errorMessage.textContent = message;
        uploadBtn.disabled = false;
    }
});