const themeToggle = document.getElementById('themeToggle');
const htmlRoot = document.documentElement;
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('imageFile');
const previewImage = document.getElementById('previewImage');
const previewCard = document.getElementById('previewCard');
const copyResult = document.getElementById('copyResult');
const downloadPdf = document.getElementById('downloadPdf');
const analysisText = document.getElementById('analysisText');

function setTheme(theme) {
  htmlRoot.dataset.theme = theme;
  localStorage.setItem('chatbotTheme', theme);
  if (theme === 'dark') {
    htmlRoot.style.background = 'linear-gradient(180deg, #03050d 0%, #0c1425 100%)';
  } else {
    htmlRoot.style.background = 'linear-gradient(180deg, #f8fbff 0%, #e9efff 100%)';
  }
}

function initTheme() {
  const storedTheme = localStorage.getItem('chatbotTheme') || 'dark';
  setTheme(storedTheme);
}

function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('show');
  }, 50);
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function handleFilePreview(file) {
  if (!file) return;
  const url = URL.createObjectURL(file);
  previewImage.src = url;
  previewImage.onload = () => URL.revokeObjectURL(url);
  const copyText = previewCard.querySelector('.preview-copy strong');
  const copyBody = previewCard.querySelector('.preview-copy p');
  if (copyText) copyText.textContent = file.name;
  if (copyBody) copyBody.textContent = `Ready for upload — ${Math.round(file.size / 1024)} KB.`;
}

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const nextTheme = htmlRoot.dataset.theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
  });
}

if (fileInput) {
  fileInput.addEventListener('change', (event) => {
    handleFilePreview(event.target.files[0]);
  });
}

if (dropzone) {
  ['dragenter', 'dragover'].forEach((eventName) => {
    dropzone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropzone.classList.add('drag-over');
    });
  });
  ['dragleave', 'drop'].forEach((eventName) => {
    dropzone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropzone.classList.remove('drag-over');
    });
  });
  dropzone.addEventListener('drop', (event) => {
    const [file] = event.dataTransfer.files;
    if (file) {
      fileInput.files = event.dataTransfer.files;
      handleFilePreview(file);
    }
  });
}

if (copyResult) {
  copyResult.addEventListener('click', () => {
    if (!analysisText) return;
    const text = analysisText.innerText;
    navigator.clipboard.writeText(text).then(() => {
      showToast('Analysis copied to clipboard');
    });
  });
}

if (downloadPdf) {
  downloadPdf.addEventListener('click', async () => {
    if (!analysisText) return;
    try {
      const { jsPDF } = window.jspdf;
      const doc = new jsPDF({ unit: 'px', format: 'a4' });
      const content = analysisText.innerText.trim();
      const pageHeight = doc.internal.pageSize.height;
      const margin = 40;
      const splitText = doc.splitTextToSize(content, 520);
      doc.setFontSize(16);
      doc.text('AI Analysis Report', margin, 60);
      doc.setFontSize(12);
      doc.text(splitText, margin, 90);
      doc.save('image-recognition-result.pdf');
      showToast('PDF downloaded successfully');
    } catch (error) {
      showToast('Unable to create PDF', 'error');
    }
  });
}

window.addEventListener('DOMContentLoaded', () => {
  initTheme();
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', (event) => {
      const targetId = anchor.getAttribute('href');
      if (targetId.length > 1) {
        event.preventDefault();
        document.querySelector(targetId)?.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
});
