import os
import tempfile
import asyncio
import re
from io import BytesIO

import streamlit as st

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import edge_tts
except ImportError:
    edge_tts = None


st.set_page_config(page_title="AwaazCraft", page_icon="🎙️", layout="wide")
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 8% 4%, rgba(56, 189, 248, 0.34), rgba(56, 189, 248, 0) 34%),
            radial-gradient(circle at 90% 10%, rgba(168, 85, 247, 0.30), rgba(168, 85, 247, 0) 36%),
            radial-gradient(circle at 50% 100%, rgba(16, 185, 129, 0.24), rgba(16, 185, 129, 0) 44%),
            linear-gradient(145deg, #040817 0%, #0c1b3a 46%, #161a48 100%);
        color: #e2e8f0;
    }
    .block-container {
        max-width: 1280px;
        padding-top: 1rem;
        padding-bottom: 1.2rem;
        padding-left: 1.2rem;
        padding-right: 1.2rem;
    }
    .hero {
        background: linear-gradient(120deg, rgba(59, 130, 246, 0.34), rgba(139, 92, 246, 0.30), rgba(16, 185, 129, 0.26));
        border: 1px solid rgba(148, 163, 184, 0.34);
        box-shadow: 0 16px 36px rgba(8, 15, 35, 0.45);
        border-radius: 20px;
        padding: 20px 22px;
        margin: 60px 0px 10px 0px;
    }
    .hero h1 {
        margin: 0;
        color: #f8fafc;
        font-size: 2.1rem;
        font-weight: 700;
    }
    .hero p {
        margin: 7px 0 0 0;
        color: #e2e8f0;
        font-size: 1rem;
        line-height: 1.45;
    }
    .glass-card {
        background: rgba(15, 23, 42, 0.60);
        border: 1px solid rgba(148, 163, 184, 0.33);
        border-radius: 18px;
        box-shadow: 0 12px 28px rgba(2, 6, 23, 0.42);
        padding: 10px 16px 12px 16px;
        margin-bottom: 10px;
    }
    .stat-chip {
        display: inline-block;
        margin-right: 8px;
        margin-top: 4px;
        border-radius: 999px;
        padding: 6px 11px;
        font-size: 0.82rem;
        border: 1px solid rgba(148, 163, 184, 0.38);
        background: rgba(30, 41, 59, 0.85);
        color: #cbd5e1;
    }
    .section-title {
        color: #f8fafc;
        font-size: 1.12rem;
        font-weight: 700;
        margin: 0 0 2px 0;
    }
    .section-note {
        color: #94a3b8;
        font-size: 0.92rem;
        margin: 0 0 8px 0;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 23, 42, 0.48);
        border: 1px solid rgba(148, 163, 184, 0.28) !important;
        border-radius: 16px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        padding-top: 0.55rem;
        padding-bottom: 0.55rem;
    }
    div[data-testid="stTextArea"] textarea {
        background: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border: 1px solid #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
    }
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stRadio"] > div,
    div[data-testid="stSlider"] > div {
        color: #e2e8f0 !important;
    }
    div[data-testid="stButton"] button, div[data-testid="baseButton-secondary"] {
        border-radius: 12px !important;
        border: 1px solid rgba(99, 102, 241, 0.45) !important;
        background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.35) !important;
    }
    div[data-testid="stDownloadButton"] button {
        border-radius: 12px !important;
        border: 1px solid rgba(16, 185, 129, 0.50) !important;
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    .app-footer {
        margin-top: 1rem;
        text-align: center;
        color: #94a3b8;
        font-size: 0.85rem;
        letter-spacing: 0.01em;
    }
    @media (max-width: 900px) {
        .block-container {
            padding-left: 0.7rem;
            padding-right: 0.7rem;
            padding-top: 0.6rem;
        }
        .hero {
            padding: 16px 16px;
            border-radius: 14px;
            margin-top: 12px;
        }
        .hero h1 {
            font-size: 1.6rem;
            line-height: 1.25;
        }
        .hero p {
            font-size: 0.92rem;
        }
        .glass-card {
            padding: 9px 10px;
            border-radius: 12px;
        }
        .stat-chip {
            display: block;
            width: fit-content;
            margin: 6px 0 0 0;
        }
        div[data-testid="stTextArea"] textarea {
            min-height: 150px !important;
            font-size: 16px !important;
        }
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 0.5rem !important;
        }
        div[data-testid="stHorizontalBlock"] > div {
            width: 100% !important;
            min-width: 100% !important;
        }
        div[data-testid="stButton"] button,
        div[data-testid="stDownloadButton"] button {
            min-height: 44px !important;
            font-size: 0.96rem !important;
        }
        .app-footer {
            margin-top: 0.7rem;
            font-size: 0.8rem;
        }
    }
    </style>
    <div class="hero">
      <h1>🎙️ AwaazCraft</h1>
      <p>Turn text into clear, natural speech with premium Indian neural voices and offline system voices.</p>
    </div>
    <div class="glass-card">
      <span class="stat-chip">Fast generation</span>
      <span class="stat-chip">Online + Offline modes</span>
      <span class="stat-chip">One-click download</span>
    </div>
    """,
    unsafe_allow_html=True,
)


def _tts_to_wav_bytes(text: str, rate: int, volume: float, voice_id: str | None = None) -> bytes:
    """Generate WAV bytes using local pyttsx3 engine."""
    engine = pyttsx3.init()
    if voice_id:
        engine.setProperty("voice", voice_id)
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
        temp_path = temp.name

    try:
        engine.save_to_file(text, temp_path)
        engine.runAndWait()
        with open(temp_path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


async def _edge_tts_save(text: str, voice: str, rate: str, volume: str, out_path: str, pitch: str = "+0Hz"):
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume, pitch=pitch)
    await communicate.save(out_path)


def _edge_tts_to_mp3_bytes(text: str, voice: str, rate_pct: int, volume_pct: int, pitch_hz: int = 0) -> bytes:
    """Generate MP3 bytes using online Edge TTS neural voices."""
    rate = f"{rate_pct:+d}%"
    volume = f"{volume_pct:+d}%"
    pitch = f"{pitch_hz:+d}Hz"
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
        temp_path = temp.name
    try:
        asyncio.run(_edge_tts_save(text, voice, rate, volume, temp_path, pitch))
        with open(temp_path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def _pick_offline_voice(language: str) -> str | None:
    """Pick a matching local voice for the selected language if possible."""
    if pyttsx3 is None:
        return None
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
    except Exception:
        return None

    hindi_tokens = ("hi", "hindi", "hin", "india", "indian")
    english_tokens = ("en", "english")
    target_tokens = hindi_tokens if language == "Hindi" else english_tokens

    for voice in voices:
        haystack_parts = [str(getattr(voice, "name", "")), str(getattr(voice, "id", ""))]
        languages = getattr(voice, "languages", None)
        if languages:
            haystack_parts.extend(str(item) for item in languages)
        haystack = " ".join(haystack_parts).lower()
        if any(token in haystack for token in target_tokens):
            return str(getattr(voice, "id", None) or "")
    return None


def _safe_file_stem(raw_name: str, fallback: str = "textvoice_output") -> str:
    """Create a filesystem-safe file stem (name without extension)."""
    stem = (raw_name or "").strip()
    if not stem:
        return fallback
    # Remove user-provided extension to avoid names like file.mp3.mp3.
    stem, _ = os.path.splitext(stem)
    stem = re.sub(r'[\\/:*?"<>|]+', "_", stem)
    stem = re.sub(r"\s+", "_", stem)
    stem = stem.strip("._")
    return stem or fallback


def _estimate_duration_seconds(text: str, words_per_minute: int = 150) -> int:
    word_count = len(text.split())
    if word_count == 0:
        return 0
    return max(1, int((word_count / words_per_minute) * 60))


if "tts_text" not in st.session_state:
    st.session_state["tts_text"] = ""

voice_preview_lines = {
    "English": "Hello, this is AwaazCraft voice preview.\nYour selected voice is clear and natural.",
    "Hindi": "नमस्ते! यह AwaazCraft का वॉइस प्रीव्यू है।\nयह आवाज़ साफ़ और प्राकृतिक है।",
    "Bengali": "নমস্কার! এটি AwaazCraft-এর ভয়েস প্রিভিউ।\nএই কণ্ঠস্বরটি স্পষ্ট এবং স্বাভাবিক।",
    "Gujarati": "નમસ્તે! આ AwaazCraft નો વોઇસ પ્રિવ્યૂ છે.\nઆ અવાજ સ્પષ્ટ અને પ્રાકૃતિક છે.",
    "Kannada": "ನಮಸ್ಕಾರ! ಇದು AwaazCraft ಧ್ವನಿ ಪೂರ್ವಾವಲೋಕನ.\nಈ ಧ್ವನಿ ಸ್ಪಷ್ಟ ಮತ್ತು ಸಹಜವಾಗಿದೆ.",
    "Malayalam": "നമസ്കാരം! ഇത് AwaazCraft ശബ്ദ പ്രിവ്യൂ ആണ്.\nഈ ശബ്ദം വ്യക്തവും സ്വാഭാവികവുമാണ്.",
    "Marathi": "नमस्कार! हा AwaazCraft चा व्हॉइस प्रीव्ह्यू आहे.\nहा आवाज स्पष्ट आणि नैसर्गिक आहे.",
    "Punjabi": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਇਹ AwaazCraft ਦੀ ਆਵਾਜ਼ ਝਲਕ ਹੈ।\nਇਹ ਆਵਾਜ਼ ਸਾਫ਼ ਅਤੇ ਕੁਦਰਤੀ ਹੈ।",
    "Tamil": "வணக்கம்! இது AwaazCraft குரல் முன்னோட்டம்.\nஇந்த குரல் தெளிவாகவும் இயல்பாகவும் உள்ளது.",
    "Telugu": "నమస్కారం! ఇది AwaazCraft వాయిస్ ప్రీవ్యూ.\nఈ స్వరం స్పష్టంగా మరియు సహజంగా ఉంది.",
}

top_left, top_right = st.columns([1, 2], gap="medium")
with top_left:
    with st.container(border=True):
        st.markdown('<p class="section-title">Voice Engine</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-note">Select a generation mode for your output audio.</p>', unsafe_allow_html=True)
        engine_mode = st.radio(
            "Voice engine",
            ["Online (Neerja/Neural)", "Offline (System voice)"],
            index=0,
            label_visibility="collapsed",
        )
with top_right:
    with st.container(border=True):
        st.markdown('<p class="section-title">Text Input</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-note">Paste script, notes, or paragraphs to convert into speech.</p>', unsafe_allow_html=True)
        _, clear_col = st.columns([4, 1])
        with clear_col:
            if st.button("Clear Text", width="stretch"):
                st.session_state["tts_text"] = ""
        text = st.text_area(
            "Enter text",
            placeholder="Type or paste your text here...",
            height=220,
            key="tts_text",
            label_visibility="collapsed",
        )
        char_count = len(text)
        word_count = len(text.split())
        est_seconds = _estimate_duration_seconds(text)
        st.caption(f"Characters: {char_count} | Words: {word_count} | Estimated duration: ~{est_seconds}s")

if engine_mode == "Online (Neerja/Neural)":
    with st.container(border=True):
        st.markdown('<p class="section-title">Online Neural Controls</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-note">Best quality Indian neural voice. Internet required.</p>', unsafe_allow_html=True)
        controls_col1, controls_col2 = st.columns(2)
        voice_options_by_language = {
            "English": ["en-IN-NeerjaNeural", "en-IN-PrabhatNeural"],
            "Hindi": ["hi-IN-SwaraNeural", "hi-IN-MadhurNeural"],
            "Bengali": ["bn-IN-BashkarNeural", "bn-IN-TanishaaNeural"],
            "Gujarati": ["gu-IN-DhwaniNeural", "gu-IN-NiranjanNeural"],
            "Kannada": ["kn-IN-GaganNeural", "kn-IN-SapnaNeural"],
            "Malayalam": ["ml-IN-MidhunNeural", "ml-IN-SobhanaNeural"],
            "Marathi": ["mr-IN-AarohiNeural", "mr-IN-ManoharNeural"],
            "Punjabi": ["pa-IN-OjasNeural", "pa-IN-VaaniNeural"],
            "Tamil": ["ta-IN-PallaviNeural", "ta-IN-ValluvarNeural"],
            "Telugu": ["te-IN-MohanNeural", "te-IN-ShrutiNeural"],
        }
        preview_voice = None
        with controls_col1:
            language = st.selectbox("Language", list(voice_options_by_language.keys()), index=0)
            voices_list = voice_options_by_language[language]
            voice = st.selectbox(
                "Online Voice",
                voices_list,
                index=0,
                format_func=lambda vid: f"🔊  {vid}",
            )
            st.caption("Tap a 🔊 below to preview that voice.")
            pv_cols = st.columns(len(voices_list))
            for idx, vid in enumerate(voices_list):
                with pv_cols[idx]:
                    if st.button(
                        "🔊",
                        key=f"pv_{language}_{vid}",
                        help=f"Preview {vid}",
                        width="stretch",
                    ):
                        preview_voice = vid
            speed_pct = st.slider("Speed (%)", min_value=-50, max_value=80, value=0)
        with controls_col2:
            vol_pct = st.slider("Volume boost (%)", min_value=-50, max_value=50, value=0)
            pitch_hz = st.slider("Pitch (Hz)", min_value=-50, max_value=50, value=0)
            online_file_stem = st.text_input("File name", value="textvoice_neerja_output")
            generate_clicked = st.button("Generate Voice", type="primary", width="stretch")

    if edge_tts is None:
        st.error("`edge-tts` is not installed. Run: `py -m pip install edge-tts`")
    elif preview_voice is not None:
        preview_text = voice_preview_lines.get(language, voice_preview_lines["English"])
        with st.spinner("Generating voice preview..."):
            try:
                preview_mp3 = _edge_tts_to_mp3_bytes(
                    text=preview_text,
                    voice=preview_voice,
                    rate_pct=speed_pct,
                    volume_pct=vol_pct,
                    pitch_hz=pitch_hz,
                )
            except Exception as exc:
                st.error(f"Could not generate preview: {exc}")
            else:
                st.caption(f"Preview for `{preview_voice}`")
                st.audio(BytesIO(preview_mp3), format="audio/mp3")
    elif generate_clicked:
        if not text.strip():
            st.warning("Please enter some text first.")
        else:
            with st.spinner("Generating online neural voice..."):
                try:
                    mp3_bytes = _edge_tts_to_mp3_bytes(
                        text=text,
                        voice=voice,
                        rate_pct=speed_pct,
                        volume_pct=vol_pct,
                        pitch_hz=pitch_hz,
                    )
                except Exception as exc:
                    st.error(f"Could not generate online voice: {exc}")
                else:
                    output_name = f"{_safe_file_stem(online_file_stem, 'textvoice_neerja_output')}.mp3"
                    st.audio(BytesIO(mp3_bytes), format="audio/mp3")
                    st.download_button(
                        "Download MP3",
                        data=mp3_bytes,
                        file_name=output_name,
                        mime="audio/mpeg",
                        width="stretch",
                    )
else:
    with st.container(border=True):
        st.markdown('<p class="section-title">Offline Voice Controls</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-note">Works offline using installed Windows voices.</p>', unsafe_allow_html=True)
        controls_col1, controls_col2 = st.columns(2)
        with controls_col1:
            language = st.selectbox("Language", ["English", "Hindi"], index=0)
            speed_label = st.selectbox("Speed", ["Slow", "Normal", "Fast"], index=1)
        with controls_col2:
            volume_pct = st.slider("Volume", min_value=0, max_value=100, value=100)
            offline_file_stem = st.text_input("File name", value="textvoice_output")

    speed_map = {"Slow": 120, "Normal": 175, "Fast": 240}
    rate = speed_map[speed_label]
    volume = volume_pct / 100.0

    if pyttsx3 is None:
        st.error("`pyttsx3` is not installed. Run: `py -m pip install pyttsx3`")
    elif st.button("Generate Voice", type="primary", width="stretch"):
        if not text.strip():
            st.warning("Please enter some text first.")
        else:
            with st.spinner("Generating offline voice..."):
                try:
                    selected_voice_id = _pick_offline_voice(language)
                    wav_bytes = _tts_to_wav_bytes(text, rate=rate, volume=volume, voice_id=selected_voice_id)
                except Exception as exc:
                    st.error(f"Could not generate speech: {exc}")
                else:
                    output_name = f"{_safe_file_stem(offline_file_stem, 'textvoice_output')}.wav"
                    if language == "Hindi" and not selected_voice_id:
                        st.info("Hindi offline voice not found in installed system voices. Using default voice.")
                    st.audio(BytesIO(wav_bytes), format="audio/wav")
                    st.download_button(
                        "Download WAV",
                        data=wav_bytes,
                        file_name=output_name,
                        mime="audio/wav",
                        width="stretch",
                    )

st.markdown('<p class="app-footer">© 2026 Developed by Simran Kaur</p>', unsafe_allow_html=True)
