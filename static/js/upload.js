document.addEventListener('DOMContentLoaded', function() {
    const audioFileInput = document.getElementById('audioFile');
    const uploadBtn = document.getElementById('uploadBtn');
    const progressSection = document.getElementById('progressSection');
    const resultSection = document.getElementById('resultSection');
    const errorSection = document.getElementById('errorSection');
    const transcriptionText = document.getElementById('transcriptionText');
    const downloadBtn = document.getElementById('downloadBtn');
    const errorMessage = document.getElementById('errorMessage');

    // Enable upload button only when a file is selected
    audioFileInput.addEventListener('change', function() {
        uploadBtn.disabled = !this.files.length;
        resetUI();
    });

    // Handle file upload and transcription
    uploadBtn.addEventListener('click', async function() {
        const file = audioFileInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        resetUI();
        showProgress();

        try {
            const response = await fetch('/transcribe', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Transcription failed');
            }

            showResult(data.text);
        } catch (error) {
            showError(error.message);
        }
    });

    // Handle download functionality
    downloadBtn.addEventListener('click', async function() {
        const text = transcriptionText.value;
        if (!text) return;

        try {
            const response = await fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Download failed');
            }

            // Create a blob from the response and download it
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'transcription.txt';
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
        transcriptionText.value = '';
    }

    function showProgress() {
        progressSection.classList.remove('d-none');
        uploadBtn.disabled = true;
    }

    function showResult(text) {
        progressSection.classList.add('d-none');
        resultSection.classList.remove('d-none');
        transcriptionText.value = text;
        uploadBtn.disabled = false;
    }

    function showError(message) {
        progressSection.classList.add('d-none');
        errorSection.classList.remove('d-none');
        errorMessage.textContent = message;
        uploadBtn.disabled = false;
    }
});
