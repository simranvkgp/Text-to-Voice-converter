import os
import tempfile
import asyncio
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


st.set_page_config(page_title="TextVoice Web", page_icon="🔊", layout="wide")
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(99, 102, 241, 0.22), rgba(99, 102, 241, 0) 38%),
            radial-gradient(circle at 90% 10%, rgba(16, 185, 129, 0.20), rgba(16, 185, 129, 0) 34%),
            linear-gradient(160deg, #0b1022 0%, #111936 45%, #0e162d 100%);
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
        background: linear-gradient(130deg, rgba(99, 102, 241, 0.32), rgba(16, 185, 129, 0.26));
        border: 1px solid rgba(148, 163, 184, 0.30);
        box-shadow: 0 14px 32px rgba(15, 23, 42, 0.35);
        border-radius: 20px;
        padding: 20px 22px;
        margin-bottom: 10px;
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
        background: rgba(15, 23, 42, 0.52);
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 18px;
        box-shadow: 0 12px 28px rgba(2, 6, 23, 0.35);
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
    @media (max-width: 900px) {
        .block-container {
            padding-left: 0.7rem;
            padding-right: 0.7rem;
        }
        .hero {
            padding: 16px 16px;
            border-radius: 14px;
        }
        .hero h1 {
            font-size: 1.6rem;
        }
    }
    </style>
    <div class="hero">
      <h1>🔊 TextVoice Converter</h1>
      <p>Convert your text into natural speech with online Indian neural voices or offline system voices.</p>
    </div>
    <div class="glass-card">
      <span class="stat-chip">Fast generation</span>
      <span class="stat-chip">Online + Offline modes</span>
      <span class="stat-chip">One-click download</span>
    </div>
    """,
    unsafe_allow_html=True,
)


def _tts_to_wav_bytes(text: str, rate: int, volume: float) -> bytes:
    """Generate WAV bytes using local pyttsx3 engine."""
    engine = pyttsx3.init()
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


async def _edge_tts_save(text: str, voice: str, rate: str, volume: str, out_path: str):
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
    await communicate.save(out_path)


def _edge_tts_to_mp3_bytes(text: str, voice: str, rate_pct: int, volume_pct: int) -> bytes:
    """Generate MP3 bytes using online Edge TTS neural voices."""
    rate = f"{rate_pct:+d}%"
    volume = f"{volume_pct:+d}%"
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
        temp_path = temp.name
    try:
        asyncio.run(_edge_tts_save(text, voice, rate, volume, temp_path))
        with open(temp_path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if "tts_text" not in st.session_state:
    st.session_state["tts_text"] = ""

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
        text = st.text_area(
            "Enter text",
            placeholder="Type or paste your text here...",
            height=220,
            key="tts_text",
            label_visibility="collapsed",
        )

if engine_mode == "Online (Neerja/Neural)":
    with st.container(border=True):
        st.markdown('<p class="section-title">Online Neural Controls</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-note">Best quality Indian neural voice. Internet required.</p>', unsafe_allow_html=True)
        controls_col1, controls_col2 = st.columns(2)
        with controls_col1:
            voice = st.selectbox(
                "Online Voice",
                [
                    "en-IN-NeerjaNeural",
                    "en-IN-PrabhatNeural",
                    "hi-IN-SwaraNeural",
                    "hi-IN-MadhurNeural",
                ],
                index=0,
            )
            speed_pct = st.slider("Speed (%)", min_value=-50, max_value=80, value=0)
        with controls_col2:
            vol_pct = st.slider("Volume boost (%)", min_value=-50, max_value=50, value=0)

    if edge_tts is None:
        st.error("`edge-tts` is not installed. Run: `py -m pip install edge-tts`")
    elif st.button("Generate Voice", type="primary", width="stretch"):
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
                    )
                except Exception as exc:
                    st.error(f"Could not generate online voice: {exc}")
                else:
                    st.audio(BytesIO(mp3_bytes), format="audio/mp3")
                    st.download_button(
                        "Download MP3",
                        data=mp3_bytes,
                        file_name="textvoice_neerja_output.mp3",
                        mime="audio/mpeg",
                        width="stretch",
                    )
else:
    with st.container(border=True):
        st.markdown('<p class="section-title">Offline Voice Controls</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-note">Works offline using installed Windows voices.</p>', unsafe_allow_html=True)
        controls_col1, controls_col2 = st.columns(2)
        with controls_col1:
            speed_label = st.selectbox("Speed", ["Slow", "Normal", "Fast"], index=1)
        with controls_col2:
            volume_pct = st.slider("Volume", min_value=0, max_value=100, value=100)

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
                    wav_bytes = _tts_to_wav_bytes(text, rate=rate, volume=volume)
                except Exception as exc:
                    st.error(f"Could not generate speech: {exc}")
                else:
                    st.audio(BytesIO(wav_bytes), format="audio/wav")
                    st.download_button(
                        "Download WAV",
                        data=wav_bytes,
                        file_name="textvoice_output.wav",
                        mime="audio/wav",
                        width="stretch",
                    )
