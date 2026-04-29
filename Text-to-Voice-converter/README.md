# TextVoice Pro — Text-to-Speech Desktop App
### Complete Setup & Usage Guide

---

## 📋 What This App Does

TextVoice Pro is a **fully offline** desktop application that converts written text into spoken audio.
Built with Python, it works without any internet connection and is designed for everyday office use.

**Features at a glance:**
- Type or paste text → hear it spoken aloud
- Switch between available system voices (male/female depends on OS)
- Control speed: Slow / Normal / Fast
- Adjust volume with a slider
- Load any `.txt` file and read it aloud
- Save your speech as a `.wav` file (or `.mp3` if pydub is installed)
- Keyboard shortcuts for power users

---

## 🖥️ System Requirements

| Item | Requirement |
|------|-------------|
| OS | Windows 10/11, macOS 10.14+, or Linux |
| Python | 3.8 or higher |
| Internet | Not required (fully offline) |

---

## ⚙️ Step-by-Step Installation

### Step 1 — Install Python

1. Go to https://www.python.org/downloads/
2. Download Python 3.10 or newer
3. During installation, **check the box** that says "Add Python to PATH"
4. Verify the install — open a terminal/command prompt and type:
   ```
   python --version
   ```
   You should see something like `Python 3.11.4`

---

### Step 2 — Install Required Libraries

Open a terminal (or Command Prompt on Windows) and run:

```bash
pip install pyttsx3
```

That's the only **required** library. Everything else (tkinter) comes with Python.

---

### Step 3 — (Optional) Enable MP3 Export

By default the app saves audio as **WAV**. To also support **MP3**, install:

```bash
pip install pydub
```

You also need **FFmpeg** installed on your system:
- **Windows**: Download from https://ffmpeg.org/download.html → extract → add the `bin` folder to your PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

Without pydub/ffmpeg the app still works perfectly — it just saves as WAV.

---

### Step 4 — Linux: Install espeak (if needed)

On Linux, pyttsx3 uses `espeak` as its backend. Install it with:

```bash
sudo apt-get install espeak
```

Windows and macOS have built-in TTS engines — no extra step needed.

---

## ▶️ How to Run the App

1. Save `tts_app.py` anywhere on your computer (e.g., Desktop)
2. Open a terminal in that folder
3. Run:

```bash
python tts_app.py
```

The app window will open immediately.

---

## 🌐 Web Version (Text-to-Voice)

If you want a clean browser page for text-to-speech:

1. Install dependencies:
   ```bash
   py -m pip install streamlit pyttsx3 edge-tts
   ```
2. Run:
   ```bash
   streamlit run web_app.py
   ```
3. Open the local URL shown in terminal (usually `http://localhost:8501`)

This web page supports:
- Text-to-speech generation (offline + online neural voices)
- Online Indian neural voices including `en-IN-NeerjaNeural`
- Download generated audio files (MP3/WAV)

---

## 🎮 Using the App

| What you want to do | How to do it |
|---------------------|--------------|
| Type text | Click the big white text area and start typing |
| Paste text | Ctrl+V inside the text area |
| Speak the text | Click **▶ Speak Text** or press **Ctrl+Enter** |
| Stop speech | Click **■ Stop** |
| Change voice | Use the **VOICE** dropdown in the left sidebar |
| Change speed | Click **Slow / Normal / Fast** radio buttons |
| Adjust volume | Drag the **VOLUME** slider |
| Open a .txt file | Click **📂 Load .txt File** or press **Ctrl+O** |
| Save audio | Click **💾 Save as Audio File** or press **Ctrl+S** |
| Clear text | Click **🗑 Clear** |

---

## 💡 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Enter` | Speak text |
| `Ctrl + S` | Save audio |
| `Ctrl + O` | Open .txt file |
| `Ctrl + Z` | Undo typing |

---

## 🎤 About Voices

The voices available depend on what's installed on your operating system:

- **Windows** — comes with voices like "Microsoft David" (male) and "Microsoft Zira" (female). You can install more via **Settings → Time & Language → Speech → Add voices**.
- **macOS** — many voices available in **System Settings → Accessibility → Spoken Content → System Voice**.
- **Linux** — espeak voices (limited). Install `espeak-ng` for more options.

---

## 📦 Optional: Convert to a Standalone .EXE (Windows)

You can package the app into a single `.exe` file that runs without Python installed.

### Step 1 — Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2 — Build the EXE

Navigate to the folder containing `tts_app.py`, then run:

```bash
pyinstaller --onefile --windowed --name "TextVoicePro" tts_app.py
```

Flags explained:
- `--onefile` → packages everything into a single `.exe`
- `--windowed` → hides the terminal/console window
- `--name` → sets the output filename

### Step 3 — Find Your EXE

After building, look inside the `dist/` folder:
```
dist/
  TextVoicePro.exe   ← this is your standalone app
```

You can copy this `.exe` to any Windows machine and run it directly.

> **Note**: Your antivirus may flag newly built EXEs. This is a common false positive with PyInstaller. You can whitelist the file.

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: pyttsx3` | Run `pip install pyttsx3` |
| App opens but no sound | Check system volume; check that a voice is selected |
| No voices in dropdown | On Linux: `sudo apt install espeak` |
| MP3 save falls back to WAV | Install pydub and ffmpeg (see Step 3 above) |
| App crashes on macOS | Try `pip install pyobjc` (needed by pyttsx3 on some macOS versions) |
| `python` not recognized | Use `python3` instead: `python3 tts_app.py` |

---

## 📁 File Structure

```
your-folder/
│
├── tts_app.py          ← The main application (this is the only file needed)
│
└── README.md           ← This guide
```

---

## 🔒 Privacy

This app is **100% offline**. No text, audio, or usage data is ever sent anywhere.
All processing happens locally on your machine.

---

*TextVoice Pro — Built with Python 3 / pyttsx3 / Tkinter*
