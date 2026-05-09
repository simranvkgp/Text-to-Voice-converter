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
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700&display=swap" rel="stylesheet">
    <style>
    :root {
        --teal: #428892;
        --sage: #82a88e;
        --olive: #b4c08f;
        --cream: #d0d8b6;
        --surface: rgba(248, 251, 242, 0.75);
        --surface-strong: rgba(245, 249, 238, 0.92);
        --text-main: #102426;
        --text-soft: #1f3d3f;
        --text-muted: #355557;
        --line: rgba(73, 118, 109, 0.24);
        --shadow-soft: 0 10px 30px rgba(62, 98, 97, 0.14);
    }
    .stApp {
        background:
            radial-gradient(circle at 12% 8%, rgba(66, 136, 146, 0.22), transparent 34%),
            radial-gradient(circle at 88% 12%, rgba(130, 168, 142, 0.2), transparent 32%),
            linear-gradient(140deg, #edf3ea 0%, #e7efe3 45%, #dee8d6 100%);
        color: var(--text-main);
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        max-width: 1280px;
        padding-top: 1rem;
        padding-bottom: 1.2rem;
        padding-left: 1.2rem;
        padding-right: 1.2rem;
    }
    p, span, label, li, .stMarkdown, div[data-testid="stMarkdownContainer"] p {
        color: var(--text-main);
    }
    div[data-testid="stCaptionContainer"], div[data-testid="stCaptionContainer"] p {
        color: var(--text-muted) !important;
    }
    div[data-testid="stTextInput"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSlider"] label,
    div[data-testid="stRadio"] label {
        color: var(--text-soft) !important;
        font-weight: 600 !important;
    }
    .hero {
        background: linear-gradient(120deg, rgba(66, 136, 146, 0.92), rgba(130, 168, 142, 0.86), rgba(180, 192, 143, 0.8));
        border: 1px solid rgba(66, 136, 146, 0.32);
        box-shadow: var(--shadow-soft);
        border-radius: 22px;
        padding: 22px 24px;
        margin: 60px 0px 10px 0px;
    }
    .hero h1 {
        margin: 0;
        color: #ffffff;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.15rem;
        font-weight: 700;
        letter-spacing: -0.01em;
    }
    .hero p {
        margin: 7px 0 0 0;
        color: #f7fbf1;
        font-size: 1rem;
        line-height: 1.45;
    }
    .glass-card {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 18px;
        box-shadow: var(--shadow-soft);
        padding: 10px 16px 12px 16px;
        margin-bottom: 10px;
        backdrop-filter: blur(8px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 30px rgba(54, 89, 86, 0.18);
    }
    .stat-chip {
        display: inline-block;
        margin-right: 8px;
        margin-top: 4px;
        border-radius: 999px;
        padding: 6px 11px;
        font-size: 0.82rem;
        border: 1px solid rgba(70, 114, 106, 0.34);
        background: rgba(208, 216, 182, 0.85);
        color: #183234;
    }
    .section-title {
        color: var(--text-main);
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.12rem;
        font-weight: 700;
        margin: 0 0 2px 0;
    }
    .section-note {
        color: var(--text-soft);
        font-size: 0.92rem;
        margin: 0 0 8px 0;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--surface-strong);
        border: 1px solid var(--line) !important;
        border-radius: 18px !important;
        box-shadow: 0 8px 24px rgba(67, 104, 96, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 28px rgba(63, 100, 91, 0.16);
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        padding-top: 0.55rem;
        padding-bottom: 0.55rem;
    }
    div[data-testid="stTextArea"] textarea {
        background: #f7faef !important;
        color: #102426 !important;
        caret-color: #000000 !important;
        border: 1px solid rgba(84, 133, 125, 0.55) !important;
        border-radius: 12px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stTextArea"] textarea::placeholder {
        color: #4f6d6f !important;
        opacity: 1 !important;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border: 1px solid #428892 !important;
        box-shadow: 0 0 0 1px #428892 !important;
    }
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stRadio"] > div,
    div[data-testid="stSlider"] > div {
        color: var(--text-main) !important;
    }
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] span {
        color: var(--text-main) !important;
    }
    div[data-baseweb="select"] input {
        color: var(--text-main) !important;
    }
    input, textarea {
        caret-color: #000000 !important;
    }
    div[data-baseweb="select"] > div {
        background: #f7faef !important;
        border-radius: 12px !important;
        border: 1px solid rgba(84, 133, 125, 0.55) !important;
        box-shadow: 0 6px 14px rgba(72, 110, 103, 0.08);
    }
    div[data-baseweb="select"] > div:hover {
        border: 1px solid rgba(66, 136, 146, 0.65) !important;
    }
    div[data-baseweb="select"] svg {
        fill: rgba(31, 61, 63, 0.8) !important;
    }
    div[data-testid="stSelectbox"] [role="listbox"] {
        background: #f6f9ee !important;
        border: 1px solid rgba(84, 133, 125, 0.35) !important;
    }
    div[data-testid="stButton"] button, div[data-testid="baseButton-secondary"] {
        border-radius: 14px !important;
        border: 1px solid rgba(58, 110, 108, 0.48) !important;
        background: linear-gradient(135deg, var(--teal), var(--sage)) !important;
        color: #f5f8ec !important;
        font-weight: 600 !important;
        box-shadow: 0 8px 18px rgba(66, 136, 146, 0.2) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
    }
    div[data-testid="stButton"] button:hover, div[data-testid="baseButton-secondary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 22px rgba(66, 136, 146, 0.26) !important;
        filter: saturate(1.05);
    }
    div[data-testid="stDownloadButton"] button {
        border-radius: 14px !important;
        border: 1px solid rgba(77, 115, 95, 0.50) !important;
        background: linear-gradient(135deg, var(--sage), var(--olive)) !important;
        color: #f5f8ec !important;
        font-weight: 600 !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    div[data-testid="stDownloadButton"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 20px rgba(108, 132, 106, 0.24);
    }
    /* Tooltips (fix dark tooltip text) */
    div[role="tooltip"],
    div[role="tooltip"] *,
    [data-baseweb="tooltip"],
    [data-baseweb="tooltip"] * {
        color: #ffffff !important;
    }
    [data-baseweb="tooltip"] {
        background: rgba(16, 36, 38, 0.92) !important;
        border: 1px solid rgba(130, 168, 142, 0.35) !important;
        box-shadow: 0 10px 22px rgba(20, 40, 40, 0.22) !important;
    }
    .side-panel-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 10px;
    }
    .side-panel-title {
        margin: 0;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        letter-spacing: -0.01em;
        color: var(--text-main);
        font-size: 1.02rem;
    }
    .side-panel-sub {
        margin: 2px 0 0 0;
        color: var(--text-muted);
        font-size: 0.86rem;
    }
    .side-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 10px;
        border-radius: 999px;
        border: 1px solid rgba(78, 123, 113, 0.22);
        background: rgba(247, 250, 239, 0.9);
        color: var(--text-main);
        font-weight: 600;
        font-size: 0.84rem;
    }
    .side-divider {
        height: 1px;
        background: rgba(73, 118, 109, 0.18);
        margin: 10px 0;
        border-radius: 99px;
    }
    .nav-strip {
        background: linear-gradient(180deg, rgba(16, 36, 38, 0.88), rgba(31, 61, 63, 0.82));
        border: 1px solid rgba(66, 136, 146, 0.26);
        border-radius: 18px;
        padding: 10px 10px;
        box-shadow: 0 14px 30px rgba(20, 40, 40, 0.18);
        position: sticky;
        top: 12px;
    }
    .nav-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 10px 12px 10px;
        border-bottom: 1px solid rgba(208, 216, 182, 0.14);
        margin-bottom: 10px;
    }
    .nav-logo {
        width: 34px;
        height: 34px;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(66, 136, 146, 0.92), rgba(130, 168, 142, 0.86));
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: rgba(255, 255, 255, 0.95);
        font-weight: 800;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .nav-name {
        color: rgba(247, 251, 241, 0.98);
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        font-size: 0.98rem;
        margin: 0;
        line-height: 1.1;
    }
    .nav-sub {
        color: rgba(247, 251, 241, 0.72);
        font-size: 0.78rem;
        margin: 2px 0 0 0;
    }
    .nav-item {
        padding: 10px 10px;
        border-radius: 14px;
        border: 1px solid rgba(208, 216, 182, 0.12);
        background: rgba(245, 249, 238, 0.06);
        color: rgba(247, 251, 241, 0.92);
        font-weight: 650;
        font-size: 0.86rem;
        margin-bottom: 8px;
        transition: transform 0.18s ease, background 0.18s ease, border-color 0.18s ease;
    }
    .nav-item:hover {
        transform: translateY(-1px);
        background: rgba(245, 249, 238, 0.1);
        border-color: rgba(208, 216, 182, 0.22);
    }
    .nav-item-active {
        background: linear-gradient(135deg, rgba(66, 136, 146, 0.45), rgba(130, 168, 142, 0.28));
        border-color: rgba(130, 168, 142, 0.42);
    }
    .nav-mini {
        color: rgba(247, 251, 241, 0.62);
        font-size: 0.76rem;
        padding: 6px 10px 2px 10px;
    }
    .app-footer {
        margin-top: 1rem;
        text-align: center;
        color: #ffffff !important;
        font-size: 0.85rem;
        letter-spacing: 0.01em;
        background: linear-gradient(135deg, rgba(66, 136, 146, 0.72), rgba(130, 168, 142, 0.68));
        border: 1px solid rgba(66, 136, 146, 0.22);
        padding: 10px 14px;
        border-radius: 14px;
        box-shadow: 0 8px 18px rgba(48, 88, 86, 0.16);
    }
    .app-footer, .app-footer * {
        color: #ffffff !important;
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
      <p>Turn text into clear, natural speech with premium Indian neural voices.</p>
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
if "show_side_panel" not in st.session_state:
    st.session_state["show_side_panel"] = True


panel_ratio = [0.30, 0.70] if st.session_state["show_side_panel"] else [0.08, 0.92]
side_col, main_col = st.columns(panel_ratio, gap="medium")

with side_col:
    if st.session_state["show_side_panel"]:
        with st.container(border=True):
            h1, h2 = st.columns([3, 1])
            with h1:
                st.markdown(
                    """
                    <div class="side-panel-header">
                      <div>
                        <p class="side-panel-title">Controls</p>
                        <p class="side-panel-sub">Voice Engine + Quick Options</p>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with h2:
                if st.button("Hide", width="stretch"):
                    st.session_state["show_side_panel"] = False

            st.markdown('<p class="section-title">Voice Engine</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-note">Select a generation mode for your output audio.</p>', unsafe_allow_html=True)
            engine_mode = st.radio(
                "Voice engine",
                ["Online (Neerja/Neural)", "Offline (System voice)"],
                index=0,
                label_visibility="collapsed",
            )

            st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)

            st.markdown('<p class="section-title">Quick Options</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-note">Small tweaks to shape your output.</p>', unsafe_allow_html=True)
            tone_mode = st.selectbox("Tone", ["Balanced", "Professional", "Warm"], index=0)
            delivery_mode = st.selectbox("Delivery", ["Natural", "Narration", "Expressive"], index=0)
            pacing_mode = st.selectbox("Pacing", ["Standard", "Slightly Slow", "Slightly Fast"], index=0)
            output_focus = st.selectbox("Focus", ["Clarity", "Smoothness", "Energy"], index=0)

            st.markdown(
                f"""
                <div class="side-chip">Selected: {tone_mode} • {delivery_mode} • {pacing_mode} • {output_focus}</div>
                """,
                unsafe_allow_html=True,
            )
    else:
        if st.button("☰", width="stretch"):
            st.session_state["show_side_panel"] = True

with main_col:
    with st.container(border=True):
        st.markdown('<p class="section-title">Text Input</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-note">Paste script, notes, or paragraphs to convert into speech.</p>', unsafe_allow_html=True)
        _, clear_col, generate_col = st.columns([3, 1, 1])
        with clear_col:
            if st.button("Clear Text", width="stretch"):
                st.session_state["tts_text"] = ""
        with generate_col:
            generate_clicked = st.button("Generate Voice", type="primary", width="stretch")
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

    # Keep controls visually grouped under Text Input (like the reference layout)
    if "engine_mode" not in locals():
        engine_mode = "Online (Neerja/Neural)"

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
            with controls_col1:
                language = st.selectbox("Language", list(voice_options_by_language.keys()), index=0)
                voices_list = voice_options_by_language[language]
                voice = st.selectbox(
                    "Online Voice",
                    voices_list,
                    index=0,
                )
                speed_pct = st.slider("Speed (%)", min_value=-50, max_value=80, value=0)
            with controls_col2:
                vol_pct = st.slider("Volume boost (%)", min_value=-50, max_value=50, value=0)
                pitch_hz = st.slider("Pitch (Hz)", min_value=-50, max_value=50, value=0)
                online_file_stem = st.text_input("File name", value="textvoice_neerja_output")

        if edge_tts is None:
            st.error("`edge-tts` is not installed. Run: `py -m pip install edge-tts`")
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
        elif generate_clicked:
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
