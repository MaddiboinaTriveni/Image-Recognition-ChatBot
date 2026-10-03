# Image Recognition Chatbot

A premium AI web application built with Flask, HTML5, CSS3, JavaScript, and Google Gemini-compatible AI.

## Project Structure

```
image_recognition_chatbot/
│
├── app.py
├── requirements.txt
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   ├── images/
│   │   ├── hero.svg
│   │   └── logo.svg
│   └── icons/
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── dashboard.html
│   ├── result.html
│   ├── navbar.html
│   └── footer.html
├── uploads/
└── README.md
```

## Built With

- Python
- Flask
- HTML5 & CSS3
- JavaScript
- Google Gemini AI (via OpenRouter-compatible API)

## Getting Started

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment

Create a `.env` file in the project root with:

```env
GOOGLE_GEMINI_API_KEY=your_api_key_here
FLASK_SECRET=your_secret_key
```

### Run the application

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Routes

- `/` → redirects to login or dashboard
- `/login` → login page
- `/home` → landing page
- `/dashboard` → secure upload dashboard
- `/upload` → analyze uploaded image
- `/logout` → logout endpoint

## Features

- Responsive glassmorphism interface
- Smooth landing page animations
- Secure login workflow
- Drag-and-drop image upload
- Live preview before upload
- AI-powered image recognition and chatbot summary
- Result copy and PDF download
- Dark mode toggle and toast notifications

## Notes

- The `uploads/` folder is ignored by `.gitignore`.
- Supported image types: PNG, JPG, JPEG, WEBP.
- Add your API key to `.env` before running.

## License

This project is available under the included license file.
