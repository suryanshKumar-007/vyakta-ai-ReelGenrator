Vyakta — AI Reel Generator 🎬

An AI-powered reel generator that converts your text and images into cinematic short videos automatically.

**Live Demo:** vyakta-ai-reelgenrator.onrender.com

---

## What it does

You type something, upload an image — and get a ready-to-post 9:16 vertical video with AI voiceover in return. No editing software, no manual work.

---

## How it works

```
User types text + uploads image
        ↓
gTTS converts text → audio.mp3
        ↓
FFmpeg combines image + audio → reel.mp4
        ↓
Reel appears in Gallery
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite + Flask-SQLAlchemy |
| Audio Generation | gTTS |
| Video Processing | FFmpeg |
| Frontend | HTML, CSS, Jinja2 |

---

## Project Structure

```
Vyakta/
├── main.py                 # Flask app
├── generate_process.py     # Background worker
├── text_to_audio.py        # Text to speech
├── config.py               # Config (not tracked)
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── create.html
│   └── gallery.html
├── static/
└── user_uploads/           # Generated reels
```

---

## Getting Started

**1. Clone the repo**
```bash
git clone https://github.com/suryanshKumar-007/vyakta-ai-ReelGenrator.git
cd vyakta-ai-ReelGenrator
```

**2. Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Install FFmpeg**
```bash
# macOS
brew install ffmpeg
```

**5. Run the app**

Terminal 1:
```bash
python3 main.py
```

Terminal 2:
```bash
python3 generate_process.py
```

**6. Open in browser**
```
http://localhost:5000
```

---

## Coming Soon

- User authentication
- Background music support
- Download reel option
- Multiple image slideshow

---

Made by Suryansh
