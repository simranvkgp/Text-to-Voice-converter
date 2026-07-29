import os
import tempfile
import asyncio
import re
import textwrap
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
st.html(
    textwrap.dedent(
        """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700&display=swap" rel="stylesheet">
    <style>
    /* ============================================================
       DESIGN TOKENS — bold gradient palette: violet primary, pink
       secondary, amber accent (download/success), graduated neutral
       scale for text/surfaces.
       ============================================================ */
    :root {
        --primary: #6d28d9;
        --primary-light: #8b5cf6;
        --primary-dark: #4c1d95;
        --primary-soft: rgba(109, 40, 217, 0.08);
        --primary-tint: #ede9fe;

        --secondary: #be185d;
        --secondary-light: #db2777;
        --secondary-dark: #9d174d;

        --accent: #b45309;
        --accent-light: #d97706;
        --accent-soft: rgba(180, 83, 9, 0.10);

        --surface: #faf9ff;
        --surface-card: rgba(255, 255, 255, 0.90);
        --surface-card-strong: rgba(255, 255, 255, 0.98);

        --ink-900: #211a3d;
        --ink-700: #3c3260;
        --ink-500: #6c6390;
        --ink-400: #948bb3;

        --line: rgba(124, 58, 237, 0.16);
        --line-strong: rgba(124, 58, 237, 0.30);

        --shadow-soft: 0 10px 28px rgba(76, 29, 149, 0.10);
        --shadow-lift: 0 16px 36px rgba(76, 29, 149, 0.20);
        --radius-lg: 20px;
        --radius-md: 16px;
        --radius-sm: 12px;
    }
    .stApp {
        background:
            radial-gradient(circle at 8% 8%, rgba(109, 40, 217, 0.08), transparent 38%),
            radial-gradient(circle at 92% 6%, rgba(190, 24, 93, 0.06), transparent 36%),
            radial-gradient(circle at 50% 100%, rgba(6, 182, 212, 0.05), transparent 42%),
            linear-gradient(160deg, #fbfaff 0%, var(--surface) 50%, #f7f5ff 100%);
        color: var(--ink-900);
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
        color: var(--ink-900);
    }
    div[data-testid="stCaptionContainer"], div[data-testid="stCaptionContainer"] p {
        color: var(--ink-400) !important;
    }
    div[data-testid="stTextInput"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSlider"] label,
    div[data-testid="stRadio"] label {
        color: var(--ink-700) !important;
        font-weight: 600 !important;
    }
    .hero {
        background: linear-gradient(120deg, var(--primary-dark) 0%, var(--secondary-dark) 100%);
        border: 1px solid var(--line-strong);
        box-shadow: 0 16px 34px rgba(76, 29, 149, 0.20);
        border-radius: var(--radius-lg);
        padding: 24px 26px;
        margin: 60px 0px 12px 0px;
        position: relative;
        overflow: hidden;
    }
    .hero::after {
        content: "";
        position: absolute;
        inset: 0;
        background:
            radial-gradient(circle at 14% 92%, rgba(255,255,255,0.14), transparent 40%),
            radial-gradient(circle at 88% 15%, rgba(255,255,255,0.16), transparent 45%);
        pointer-events: none;
    }
    .hero h1 {
        margin: 0;
        color: #ffffff;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.15rem;
        font-weight: 700;
        letter-spacing: -0.01em;
        position: relative;
        text-shadow: 0 2px 18px rgba(0, 0, 0, 0.15);
    }
    .hero p {
        margin: 7px 0 0 0;
        color: rgba(255, 255, 255, 0.92);
        font-size: 1rem;
        line-height: 1.45;
        position: relative;
    }
    .glass-card {
        background: var(--surface-card);
        border: 1px solid var(--line);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-soft);
        padding: 12px 18px 14px 18px;
        margin-bottom: 16px;
        backdrop-filter: blur(8px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-lift);
    }
    .stat-chip {
        display: inline-block;
        margin-right: 8px;
        margin-top: 4px;
        border-radius: 999px;
        padding: 6px 13px;
        font-size: 0.82rem;
        border: none;
        background: #9c76d8;
        color: #ffffff;
        font-weight: 700;
        box-shadow: 0 6px 14px rgba(76, 29, 149, 0.16);
    }
    .section-title {
        color: var(--primary-dark);
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.12rem;
        font-weight: 700;
        margin: 0 0 2px 0;
    }
    .section-note {
        color: var(--ink-500);
        font-size: 0.92rem;
        margin: 0 0 8px 0;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--surface-card-strong);
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-soft);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lift);
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        padding-top: 0.75rem;
        padding-bottom: 0.75rem;
    }
    div[data-testid="stTextArea"] textarea {
        background: #ffffff !important;
        color: var(--ink-900) !important;
        caret-color: var(--primary-dark) !important;
        border: 1px solid var(--line-strong) !important;
        border-radius: var(--radius-sm) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stTextArea"] textarea::placeholder {
        color: var(--ink-400) !important;
        opacity: 1 !important;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border: 1px solid var(--primary) !important;
        box-shadow: 0 0 0 3px var(--primary-soft) !important;
    }
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stRadio"] > div,
    div[data-testid="stSlider"] > div {
        color: var(--ink-900) !important;
    }
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] span {
        color: var(--ink-900) !important;
    }
    div[data-baseweb="select"] input {
        color: var(--ink-900) !important;
    }
    input, textarea {
        caret-color: var(--primary-dark) !important;
    }
    div[data-baseweb="select"] > div {
        background: var(--primary-tint) !important;
        border-radius: var(--radius-sm) !important;
        border: 2px solid var(--primary) !important;
        font-weight: 700 !important;
        box-shadow: 0 6px 14px rgba(76, 29, 149, 0.06);
    }
    div[data-baseweb="select"] > div:hover {
        border: 2px solid var(--primary-dark) !important;
    }
    div[data-baseweb="select"] svg {
        fill: var(--primary) !important;
    }
    div[data-testid="stSelectbox"] [role="listbox"] {
        background: #ffffff !important;
        border: 1.5px solid var(--primary) !important;
    }
    div[data-testid="stSlider"] [data-baseweb="slider"] [role="progressbar"] {
        background: var(--primary) !important;
    }
    div[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
        background-color: var(--primary) !important;
        border-color: var(--primary) !important;
    }
    div[data-testid="stRadio"] [data-baseweb="radio"] [data-checked="true"] div {
        background-color: var(--primary) !important;
        border-color: var(--primary) !important;
    }
    div[data-testid="stButton"] button, div[data-testid="baseButton-secondary"] {
        border-radius: var(--radius-sm) !important;
        border: 2px solid var(--primary) !important;
        background: var(--primary-tint) !important;
        color: var(--primary-dark) !important;
        font-weight: 700 !important;
        box-shadow: var(--shadow-soft) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease, color 0.18s ease;
        white-space: nowrap !important;
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }
    div[data-testid="stButton"] button:hover, div[data-testid="baseButton-secondary"]:hover {
        transform: translateY(-1px);
        background: var(--primary) !important;
        color: #ffffff !important;
        border-color: var(--primary-dark) !important;
        box-shadow: var(--shadow-lift) !important;
    }
    div[data-testid="stButton"] button[kind="primary"],
    div[data-testid="baseButton-primary"] {
        border-radius: var(--radius-sm) !important;
        border: none !important;
        background: #9c76d8 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 22px rgba(76, 29, 149, 0.24) !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background: var(--primary) !important;
        box-shadow: 0 12px 24px rgba(76, 29, 149, 0.30) !important;
        transform: translateY(-1px);
    }
    div[data-testid="stDownloadButton"] button {
        border-radius: var(--radius-sm) !important;
        border: none !important;
        background: var(--accent-light) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 22px rgba(180, 83, 9, 0.22) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
    }
    div[data-testid="stDownloadButton"] button:hover {
        background: var(--accent) !important;
        transform: translateY(-1px);
        box-shadow: 0 12px 24px rgba(180, 83, 9, 0.30) !important;
    }
    div[data-testid="stAlert"] {
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--line) !important;
        border-left: 3px solid var(--primary) !important;
        background: var(--primary-soft) !important;
        color: var(--ink-900) !important;
    }
    /* Tooltips (fix dark tooltip text) */
    div[role="tooltip"],
    div[role="tooltip"] *,
    [data-baseweb="tooltip"],
    [data-baseweb="tooltip"] * {
        color: #ffffff !important;
    }
    [data-baseweb="tooltip"] {
        background: var(--ink-900) !important;
        border: 1px solid var(--primary-light) !important;
        box-shadow: var(--shadow-lift) !important;
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
        color: var(--ink-900);
        font-size: 1.02rem;
    }
    .side-panel-sub {
        margin: 2px 0 0 0;
        color: var(--ink-500);
        font-size: 0.86rem;
    }
    .side-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 12px;
        border-radius: 999px;
        border: 1px solid var(--line-strong);
        background: var(--primary-soft);
        color: var(--primary-dark);
        font-weight: 700;
        font-size: 0.84rem;
    }
    .side-divider {
        height: 1px;
        background: var(--line);
        margin: 10px 0;
        border-radius: 99px;
    }
    .app-footer {
        margin-top: 1rem;
        text-align: center;
        color: var(--ink-500) !important;
        font-size: 0.85rem;
        letter-spacing: 0.01em;
        background: transparent !important;
        border: none !important;
        padding: 10px 14px;
        border-radius: var(--radius-sm);
        box-shadow: none !important;
    }
    .app-footer, .app-footer * {
        color: var(--ink-500) !important;
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
      <span class="stat-chip">⚡ Fast generation</span>
      <span class="stat-chip">🌐 Online + Offline modes</span>
      <span class="stat-chip">⬇️ One-click download</span>
    </div>
    """
    )
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


layout_ratio = [0.22, 0.58, 0.20] if st.session_state["show_side_panel"] else [0.06, 0.66, 0.28]
left_strip_col, main_col, right_strip_col = st.columns(layout_ratio, gap="large")

with left_strip_col:
    if st.session_state["show_side_panel"]:
        with st.container(border=True):
            h1, h2 = st.columns([2.2, 1])
            with h1:
                st.markdown(
                    textwrap.dedent(
                        """
                    <div class="side-panel-header">
                      <div>
                        <p class="side-panel-title">🎛️ Controls</p>
                        <p class="side-panel-sub">Voice Engine + Quick Options</p>
                      </div>
                    </div>
                    """
                    ),
                    unsafe_allow_html=True,
                )
            with h2:
                if st.button("Hide", width="stretch"):
                    st.session_state["show_side_panel"] = False

            st.markdown('<p class="section-title">🎚️ Voice Engine</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-note">Select a generation mode for your output audio.</p>', unsafe_allow_html=True)
            st.radio(
                "Voice engine",
                ["Online (Neerja/Neural)", "Offline (System voice)"],
                index=0,
                label_visibility="collapsed",
                key="engine_mode",
            )

            st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)

            st.markdown('<p class="section-title">⚙️ Quick Options</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-note">Small tweaks to shape your output.</p>', unsafe_allow_html=True)
            tone_mode = st.selectbox("Tone", ["Balanced", "Professional", "Warm"], index=0)
            delivery_mode = st.selectbox("Delivery", ["Natural", "Narration", "Expressive"], index=0)
            pacing_mode = st.selectbox("Pacing", ["Standard", "Slightly Slow", "Slightly Fast"], index=0)
            output_focus = st.selectbox("Focus", ["Clarity", "Smoothness", "Energy"], index=0)

            st.markdown(
                textwrap.dedent(
                    f"""
                <div class="side-chip">Selected: {tone_mode} • {delivery_mode} • {pacing_mode} • {output_focus}</div>
                """
                ),
                unsafe_allow_html=True,
            )
    else:
        if st.button("☰", width="stretch"):
            st.session_state["show_side_panel"] = True

engine_mode = st.session_state.get("engine_mode", "Online (Neerja/Neural)")

with main_col:
    with st.container(border=True):
        st.markdown('<p class="section-title">📝 Text Input</p>', unsafe_allow_html=True)
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

with right_strip_col:
    with st.container(border=True):
        if engine_mode == "Online (Neerja/Neural)":
            st.markdown('<p class="section-title">🌐 Online Neural Controls</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-note">Best quality Indian neural voice. Internet required.</p>', unsafe_allow_html=True)
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
            language = st.selectbox("Language", list(voice_options_by_language.keys()), index=0)
            voices_list = voice_options_by_language[language]
            voice = st.selectbox("Online Voice", voices_list, index=0)
            speed_pct = st.slider("Speed (%)", min_value=-50, max_value=80, value=0)
            vol_pct = st.slider("Volume boost (%)", min_value=-50, max_value=50, value=0)
            pitch_hz = st.slider("Pitch (Hz)", min_value=-50, max_value=50, value=0)
            online_file_stem = st.text_input("File name", value="textvoice_neerja_output")
        else:
            st.markdown('<p class="section-title">💻 Offline Voice Controls</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-note">Works offline using installed Windows voices.</p>', unsafe_allow_html=True)
            language = st.selectbox("Language", ["English", "Hindi"], index=0)
            speed_label = st.selectbox("Speed", ["Slow", "Normal", "Fast"], index=1)
            volume_pct = st.slider("Volume", min_value=0, max_value=100, value=100)
            offline_file_stem = st.text_input("File name", value="textvoice_output")

if engine_mode == "Online (Neerja/Neural)":
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

st.markdown('<p class="app-footer">© 2026 Developed by Simran Kaur · design-fix-v3</p>', unsafe_allow_html=True)
