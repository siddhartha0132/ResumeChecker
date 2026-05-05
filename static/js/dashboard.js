const resumeInput = document.querySelector('#resumes');
const helpText = document.querySelector('.help-text');
const form = document.querySelector('.score-form');

if (resumeInput && helpText) {
    resumeInput.addEventListener('change', () => {
        const count = resumeInput.files.length;
        helpText.textContent = count
            ? `${count} resume${count === 1 ? '' : 's'} selected. Upload 5-10 PDF, TXT, or DOCX resumes.`
            : 'Supported formats: PDF, TXT, DOCX. Use 5 mock resumes from sample_resumes/ for a quick demo.';
    });
}

if (form) {
    form.addEventListener('submit', () => {
        const button = form.querySelector('.primary-button');
        if (button) {
            button.textContent = 'Scoring...';
            button.disabled = true;
        }
    });
}
