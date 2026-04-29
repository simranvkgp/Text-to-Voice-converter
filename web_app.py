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

try:
    from gtts import gTTS
except ImportError:
    gTTS = None


st.set_page_config(page_title="TextVoice Web", page_icon="🔊", layout="wide")
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap" rel="stylesheet">
    <style>

    /* ── Base ── */
    .stApp {
        background-color: #0d0a06;
        background-image:
            radial-gradient(ellipse 70% 40% at 15% 0%, rgba(214,158,46,0.13) 0%, transparent 60%),
            radial-gradient(ellipse 50% 30% at 85% 5%,  rgba(214,158,46,0.07) 0%, transparent 55%),
            repeating-linear-gradient(
                0deg,
                transparent,
                transparent 39px,
                rgba(255,255,255,0.018) 39px,
                rgba(255,255,255,0.018) 40px
            );
        color: #e8dcc8;
        font-family: 'DM Sans', sans-serif;
    }

    .block-container {
        max-width: 1260px;
        padding-top: 0.6rem;
        padding-bottom: 2rem;
        padding-left: 1.4rem;
        padding-right: 1.4rem;
    }

    /* ── Hero ── */
    .hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(118deg, #1a1208 0%, #201508 60%, #160f04 100%);
        border: 1px solid rgba(214,158,46,0.30);
        border-radius: 4px;
        padding: 28px 32px 24px 32px;
        margin-bottom: 2px;
    }
    .hero::before {
        content: '';
        position: absolute;
        inset: 0;
        background: repeating-linear-gradient(
            90deg,
            transparent,
            transparent 3px,
            rgba(214,158,46,0.025) 3px,
            rgba(214,158,46,0.025) 4px
        );
        pointer-events: none;
    }
    .hero-inner {
        position: relative;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .hero-waveform {
        flex-shrink: 0;
        display: flex;
        align-items: center;
        gap: 3px;
        height: 52px;
    }
    .hero-waveform span {
        display: inline-block;
        width: 4px;
        border-radius: 2px;
        background: linear-gradient(180deg, #d69e2e, #b7791f);
        animation: wave 1.4s ease-in-out infinite;
    }
    .hero-waveform span:nth-child(1)  { height: 14px; animation-delay: 0.0s; }
    .hero-waveform span:nth-child(2)  { height: 28px; animation-delay: 0.1s; }
    .hero-waveform span:nth-child(3)  { height: 40px; animation-delay: 0.2s; }
    .hero-waveform span:nth-child(4)  { height: 52px; animation-delay: 0.3s; }
    .hero-waveform span:nth-child(5)  { height: 34px; animation-delay: 0.4s; }
    .hero-waveform span:nth-child(6)  { height: 20px; animation-delay: 0.5s; }
    .hero-waveform span:nth-child(7)  { height: 44px; animation-delay: 0.15s; }
    .hero-waveform span:nth-child(8)  { height: 30px; animation-delay: 0.25s; }
    .hero-waveform span:nth-child(9)  { height: 18px; animation-delay: 0.35s; }
    .hero-waveform span:nth-child(10) { height: 10px; animation-delay: 0.45s; }
    @keyframes wave {
        0%, 100% { transform: scaleY(1);   opacity: 0.85; }
        50%       { transform: scaleY(0.4); opacity: 0.45; }
    }
    .hero-text {}
    .hero-eyebrow {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.72rem;
        font-weight: 500;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #d69e2e;
        margin: 0 0 6px 0;
    }
    .hero h1 {
        font-family: 'DM Serif Display', serif;
        font-size: 2.4rem;
        font-weight: 400;
        line-height: 1.1;
        margin: 0 0 8px 0;
        color: #f5e8c8;
        letter-spacing: -0.01em;
    }
    .hero h1 em {
        font-style: italic;
        color: #d69e2e;
    }
    .hero p {
        font-size: 0.9rem;
        color: #a89070;
        margin: 0;
        line-height: 1.55;
        font-weight: 300;
    }

    /* ── Feature strip ── */
    .feature-strip {
        display: flex;
        gap: 0;
        margin-bottom: 16px;
        border: 1px solid rgba(214,158,46,0.20);
        border-top: none;
        border-radius: 0 0 4px 4px;
        overflow: hidden;
    }
    .feature-item {
        flex: 1;
        padding: 9px 14px;
        background: rgba(20,14,4,0.85);
        font-size: 0.76rem;
        color: #8a7055;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        font-weight: 500;
        text-align: center;
        border-right: 1px solid rgba(214,158,46,0.14);
        transition: background 0.2s, color 0.2s;
    }
    .feature-item:last-child { border-right: none; }
    .feature-item strong {
        color: #c8a060;
        font-weight: 600;
        display: block;
        font-size: 0.9rem;
        text-transform: none;
        letter-spacing: 0;
        margin-bottom: 1px;
    }

    /* ── Section cards (Streamlit border containers) ── */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(16, 10, 2, 0.70) !important;
        border: 1px solid rgba(214,158,46,0.22) !important;
        border-radius: 4px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        padding-top: 0.6rem;
        padding-bottom: 0.65rem;
    }

    /* ── Labels ── */
    .section-title {
        font-family: 'DM Serif Display', serif;
        font-size: 1.05rem;
        font-weight: 400;
        color: #f0ddb0;
        margin: 0 0 1px 0;
        letter-spacing: 0.01em;
    }
    .section-note {
        font-size: 0.82rem;
        color: #7a6045;
        margin: 0 0 10px 0;
        font-weight: 300;
        line-height: 1.45;
    }

    /* ── Streamlit widget overrides ── */
    div[data-testid="stTextArea"] textarea {
        background: #0a0700 !important;
        color: #e8dcc8 !important;
        border: 1px solid rgba(214,158,46,0.28) !important;
        border-radius: 4px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.92rem !important;
        line-height: 1.6 !important;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border: 1px solid rgba(214,158,46,0.65) !important;
        box-shadow: 0 0 0 2px rgba(214,158,46,0.12) !important;
    }
    div[data-testid="stTextArea"] textarea::placeholder {
        color: #4a3820 !important;
    }

    /* Selectbox, radio, slider text */
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stRadio"] > div,
    div[data-testid="stSlider"] > div,
    .stRadio label,
    label {
        color: #c8a878 !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* Slider track */
    div[data-testid="stSlider"] [data-baseweb="slider"] [role="progressbar"] {
        background-color: #d69e2e !important;
    }
    div[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
        background-color: #d69e2e !important;
        border-color: #d69e2e !important;
    }

    /* Radio selected */
    div[data-testid="stRadio"] [data-baseweb="radio"] [data-checked="true"] div {
        background-color: #d69e2e !important;
        border-color: #d69e2e !important;
    }

    /* ── Primary button ── */
    div[data-testid="stButton"] button,
    div[data-testid="baseButton-primary"] {
        border-radius: 3px !important;
        border: 1px solid rgba(214,158,46,0.55) !important;
        background: linear-gradient(135deg, #c8891a 0%, #a06810 100%) !important;
        color: #fdf3de !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        box-shadow: 0 4px 16px rgba(180,120,20,0.28), inset 0 1px 0 rgba(255,220,120,0.15) !important;
        transition: all 0.18s !important;
    }
    div[data-testid="stButton"] button:hover {
        background: linear-gradient(135deg, #d69e2e 0%, #b7791f 100%) !important;
        box-shadow: 0 6px 24px rgba(214,158,46,0.40) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Download button ── */
    div[data-testid="stDownloadButton"] button {
        border-radius: 3px !important;
        border: 1px solid rgba(214,158,46,0.35) !important;
        background: rgba(20,14,4,0.9) !important;
        color: #d69e2e !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        box-shadow: inset 0 0 0 1px rgba(214,158,46,0.18) !important;
    }
    div[data-testid="stDownloadButton"] button:hover {
        background: rgba(214,158,46,0.12) !important;
        border-color: rgba(214,158,46,0.55) !important;
    }

    /* ── Audio player ── */
    audio {
        width: 100%;
        border-radius: 4px;
        filter: sepia(0.4) hue-rotate(-10deg);
    }

    /* ── Alert/warning overrides ── */
    div[data-testid="stAlert"] {
        border-radius: 4px !important;
        border-left: 3px solid #d69e2e !important;
        background: rgba(214,158,46,0.08) !important;
    }

    @media (max-width: 900px) {
        .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
        .hero { padding: 20px 18px; }
        .hero h1 { font-size: 1.8rem; }
        .hero-waveform { display: none; }
        .feature-strip { flex-wrap: wrap; }
        .feature-item { flex: 1 1 33%; }
    }
    </style>

    <div class="hero">
      <div class="hero-inner">
        <div class="hero-waveform">
          <span></span><span></span><span></span><span></span><span></span>
          <span></span><span></span><span></span><span></span><span></span>
        </div>
        <div class="hero-text">
          <p class="hero-eyebrow">Text-to-Speech Studio</p>
          <h1>TextVoice <em>Converter</em></h1>
          <p>Transform written text into natural-sounding speech — with Indian neural voices online, or system voices offline.</p>
        </div>
      </div>
    </div>

    <div class="feature-strip">
      <div class="feature-item"><strong>⚡ Fast</strong>generation</div>
      <div class="feature-item"><strong>🌐 Online</strong>neural voices</div>
      <div class="feature-item"><strong>💻 Offline</strong>system voices</div>
      <div class="feature-item"><strong>⬇ Download</strong>one-click</div>
    </div>
    """,
    unsafe_allow_html=True,
)


def _tts_to_wav_bytes(text: str, rate: int, volume: float, voice_id: str = None) -> bytes:
    """Generate WAV bytes using local pyttsx3 engine."""
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)
    if voice_id:
        # Some installed voices may not match the requested language; fail gracefully.
        try:
            engine.setProperty("voice", voice_id)
        except Exception:
            pass

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


def _looks_like_hindi(text: str) -> bool:
    """Best-effort Hindi detection (checks for Devanagari characters)."""
    if not text:
        return False
    for ch in text:
        if "\u0900" <= ch <= "\u097F":  # Devanagari block
            return True
    return False


def _get_offline_voice_options():
    """Return offline pyttsx3 voices as a list of (display_name, voice_id)."""
    engine = pyttsx3.init()
    voices = engine.getProperty("voices") or []

    options = []
    for v in voices:
        name = str(getattr(v, "name", "") or "")
        display = name.split("\\")[-1] if "\\" in name else name
        options.append((display, str(getattr(v, "id", "") or "")))
    return options


def _voice_looks_hindi(display_name: str, voice_id: str) -> bool:
    haystack = f"{display_name} {voice_id}".lower()
    return any(k in haystack for k in ["hindi", "hi-in", "hi_", "hi-"])


async def _edge_tts_save(text: str, voice: str, rate: str, volume: str, out_path: str):
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
    await communicate.save(out_path)


def _edge_rate_volume_strings(rate_pct: int, volume_pct: int) -> tuple[str, str]:
    """edge-tts expects strings like '+10%' or '0%'. Avoid '+0%'."""
    rate = "0%" if rate_pct == 0 else f"{rate_pct:+d}%"
    volume = "0%" if volume_pct == 0 else f"{volume_pct:+d}%"
    return rate, volume


def _edge_tts_to_mp3_bytes(text: str, voice: str, rate_pct: int, volume_pct: int) -> bytes:
    """Generate MP3 bytes using online Edge TTS neural voices."""
    rate, volume = _edge_rate_volume_strings(rate_pct, volume_pct)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
        temp_path = temp.name
    try:
        asyncio.run(_edge_tts_save(text, voice, rate, volume, temp_path))
        with open(temp_path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def _chunk_text_for_edge_tts(text: str, max_chars: int = 450):
    """
    Edge TTS can fail with "No audio was received" on long inputs.
    Chunk into smaller parts to improve reliability.
    """
    text = (text or "").strip()
    if not text:
        return []

    # Split on common sentence boundaries (including Hindi "।" danda) and new lines.
    parts = re.split(r"(?<=[\.\!\?\u0964\u0965])\s+|\n+", text)
    if not parts:
        parts = [text]

    chunks = []
    current = ""

    for part in parts:
        if not part:
            continue
        part = part.strip()
        if not part:
            continue

        if len(current) + len(part) <= max_chars:
            current = f"{current} {part}".strip() if current else part
            continue

        if current:
            chunks.append(current.strip())
            current = ""

        if len(part) <= max_chars:
            current = part
        else:
            # Hard split very long segments.
            for i in range(0, len(part), max_chars):
                chunks.append(part[i : i + max_chars].strip())

    if current:
        chunks.append(current.strip())

    # Remove empties.
    return [c for c in chunks if c]


def _edge_tts_to_mp3_bytes_chunked(
    text: str,
    voice: str,
    rate_pct: int,
    volume_pct: int,
    max_chars: int = 450,
) -> bytes:
    """Generate MP3 bytes by chunking the input text and concatenating MP3 frames."""
    chunks = _chunk_text_for_edge_tts(text, max_chars=max_chars)
    if not chunks:
        return _edge_tts_to_mp3_bytes("", voice=voice, rate_pct=rate_pct, volume_pct=volume_pct)

    combined = b""
    for chunk in chunks:
        combined += _edge_tts_to_mp3_bytes(
            text=chunk,
            voice=voice,
            rate_pct=rate_pct,
            volume_pct=volume_pct,
        )
    return combined


def _gtts_to_mp3_bytes(text: str, lang: str) -> bytes:
    """Fallback online TTS using gTTS."""
    if gTTS is None:
        raise RuntimeError("gTTS is not installed")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
        temp_path = temp.name
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(temp_path)
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
            auto_hindi = st.checkbox("Auto Hindi detection", value=True)
            vol_pct = st.slider("Volume boost (%)", min_value=-50, max_value=50, value=0)

    if edge_tts is None:
        st.error("`edge-tts` is not installed. Run: `py -m pip install edge-tts`")
    elif st.button("Generate Voice", type="primary", width="stretch"):
        if not text.strip():
            st.warning("Please enter some text first.")
        else:
            with st.spinner("Generating online neural voice..."):
                try:
                    voice_used = voice
                    if auto_hindi and _looks_like_hindi(text) and not str(voice).startswith("hi-IN-"):
                        # If the user typed Hindi, switch to a Hindi neural voice automatically.
                        voice_used = "hi-IN-SwaraNeural"

                    voice_candidates = [voice_used]
                    if _looks_like_hindi(text):
                        # If one Hindi voice fails, fall back to the other.
                        for v in ["hi-IN-SwaraNeural", "hi-IN-MadhurNeural"]:
                            if v not in voice_candidates:
                                voice_candidates.append(v)

                    # Smaller chunks improve reliability for longer Hindi paragraphs.
                    max_chars = 300
                    use_chunking = len(text) > max_chars
                    chunks_count = len(_chunk_text_for_edge_tts(text, max_chars=max_chars)) if use_chunking else 1
                    if use_chunking:
                        st.info(f"Long text detected. Splitting into {chunks_count} parts for Edge TTS...")

                    mp3_bytes = None
                    last_exc = None
                    for candidate_voice in voice_candidates:
                        try:
                            if use_chunking:
                                mp3_bytes = _edge_tts_to_mp3_bytes_chunked(
                                    text=text,
                                    voice=candidate_voice,
                                    rate_pct=speed_pct,
                                    volume_pct=vol_pct,
                                    max_chars=max_chars,
                                )
                            else:
                                mp3_bytes = _edge_tts_to_mp3_bytes(
                                    text=text,
                                    voice=candidate_voice,
                                    rate_pct=speed_pct,
                                    volume_pct=vol_pct,
                                )
                            if mp3_bytes:
                                voice_used = candidate_voice
                                break
                        except Exception as exc:
                            last_exc = exc
                            # Edge TTS sometimes fails specifically on parameter combinations.
                            # If so, retry once with neutral rate/volume.
                            if "No audio was received" in str(exc) and (speed_pct != 0 or vol_pct != 0):
                                try:
                                    if use_chunking:
                                        mp3_bytes = _edge_tts_to_mp3_bytes_chunked(
                                            text=text,
                                            voice=candidate_voice,
                                            rate_pct=0,
                                            volume_pct=0,
                                            max_chars=max_chars,
                                        )
                                    else:
                                        mp3_bytes = _edge_tts_to_mp3_bytes(
                                            text=text,
                                            voice=candidate_voice,
                                            rate_pct=0,
                                            volume_pct=0,
                                        )
                                    if mp3_bytes:
                                        voice_used = candidate_voice
                                        break
                                except Exception:
                                    pass

                    if not mp3_bytes:
                        raise RuntimeError(f"Edge TTS returned no audio. Last error: {last_exc}")
                except Exception as exc:
                    # Cloud fallback: if edge-tts fails, try gTTS for Hindi/English.
                    try:
                        fallback_lang = "hi" if _looks_like_hindi(text) else "en"
                        mp3_bytes = _gtts_to_mp3_bytes(text=text, lang=fallback_lang)
                    except Exception as gtts_exc:
                        st.error(
                            "Could not generate online voice. "
                            f"Edge TTS error: {exc} | gTTS fallback error: {gtts_exc}"
                        )
                    else:
                        st.warning("Edge TTS failed, used gTTS fallback.")
                        st.audio(BytesIO(mp3_bytes), format="audio/mp3")
                        st.download_button(
                            "Download MP3",
                            data=mp3_bytes,
                            file_name="textvoice_fallback_output.mp3",
                            mime="audio/mpeg",
                            width="stretch",
                        )
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
        st.markdown('<p class="section-note">Works offline using installed Windows voices (Hindi works if you have a Hindi voice installed).</p>', unsafe_allow_html=True)
        controls_col1, controls_col2 = st.columns(2)
        with controls_col1:
            speed_label = st.selectbox("Speed", ["Slow", "Normal", "Fast"], index=1)
        with controls_col2:
            volume_pct = st.slider("Volume", min_value=0, max_value=100, value=100)
            offline_voice_id = None
            if pyttsx3 is not None:
                voice_options = _get_offline_voice_options()
                voice_displays = [d if d else vid for d, vid in voice_options]
                display_to_voice_id = {
                    (display if display else voice_id): voice_id for display, voice_id in voice_options
                }

                default_index = 0
                if _looks_like_hindi(text) and voice_options:
                    for i, (display, vid) in enumerate(voice_options):
                        if _voice_looks_hindi(display, vid):
                            default_index = i
                            break

                if voice_displays:
                    offline_voice_display = st.selectbox(
                        "Offline Voice",
                        voice_displays,
                        index=default_index,
                    )
                    # Map the selected display string back to its voice_id.
                    offline_voice_id = display_to_voice_id.get(offline_voice_display)

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
                    wav_bytes = _tts_to_wav_bytes(
                        text,
                        rate=rate,
                        volume=volume,
                        voice_id=offline_voice_id,
                    )
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
