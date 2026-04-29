"""
============================================================
  TextVoice Pro - Text-to-Speech Desktop Application
  Built with Python, pyttsx3, and Tkinter
  Designed for Office Use
============================================================
"""

# ── Standard Library Imports ──────────────────────────────
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import threading
import os
import sys
from typing import List, Tuple

# ── Third-Party Imports ───────────────────────────────────
try:
    import pyttsx3
except ImportError:
    messagebox.showerror(
        "Missing Library",
        "pyttsx3 is not installed.\nRun: pip install pyttsx3"
    )
    sys.exit(1)


# ══════════════════════════════════════════════════════════
#  TTS Engine Wrapper
#  Handles all text-to-speech operations safely
# ══════════════════════════════════════════════════════════
class TTSEngine:
    """Wraps pyttsx3 to provide a clean, thread-safe interface."""

    # Speech rate presets (words per minute)
    SPEED_PRESETS = {"Slow": 120, "Normal": 175, "Fast": 240}
    INDIAN_VOICE_MARKERS = (
        "india", "indian", "hindi", "hi-in", "en-in",
        "bn-in", "ta-in", "te-in", "mr-in", "gu-in",
        "kn-in", "ml-in", "pa-in", "ur-in"
    )

    def __init__(self):
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty("voices")
        self._speaking = False

    # ── Voice helpers ──────────────────────────────────────
    @staticmethod
    def _decode_locale(raw_locale):
        """Best-effort decode for pyttsx3 voice language fields."""
        if isinstance(raw_locale, bytes):
            # SAPI voices sometimes prefix locale bytes with a control byte.
            raw_locale = raw_locale.lstrip(b"\x00\x01\x02\x05")
            return raw_locale.decode("utf-8", errors="ignore")
        return str(raw_locale or "")

    def _is_indian_voice(self, voice):
        """Return True if voice metadata looks Indian."""
        parts = [str(voice.name), str(voice.id)]
        for locale in getattr(voice, "languages", []) or []:
            parts.append(self._decode_locale(locale))
        combined = " ".join(parts).lower()
        return any(marker in combined for marker in self.INDIAN_VOICE_MARKERS)

    def get_voice_options(self):
        """Return list of (display_name, voice_id) tuples."""
        options: List[Tuple[str, str, bool]] = []
        for v in self.voices:
            name = v.name
            # Simplify long names for the UI
            display = name.split("\\")[-1] if "\\" in name else name
            is_indian = self._is_indian_voice(v)
            if is_indian:
                display = f"{display}  🇮🇳"
            options.append((display, v.id, is_indian))

        # Put Indian voices first, then keep a stable alphabetical order.
        options.sort(key=lambda row: (not row[2], row[0].lower()))
        return [(display, vid) for display, vid, _ in options]

    def set_voice(self, voice_id):
        self.engine.setProperty("voice", voice_id)

    # ── Rate / Volume ──────────────────────────────────────
    def set_rate(self, label: str):
        wpm = self.SPEED_PRESETS.get(label, 175)
        self.engine.setProperty("rate", wpm)

    def set_volume(self, value: float):
        """value: 0.0 – 1.0"""
        self.engine.setProperty("volume", float(value))

    # ── Speak ──────────────────────────────────────────────
    def speak(self, text: str):
        """Speak text synchronously (call from a thread)."""
        if not text.strip():
            return
        self._speaking = True
        self.engine.say(text)
        self.engine.runAndWait()
        self._speaking = False

    def stop(self):
        """Interrupt current speech."""
        self.engine.stop()
        self._speaking = False

    # ── Save to WAV then convert ───────────────────────────
    def save_audio(self, text: str, filepath: str):
        """
        Save speech to a file.
        pyttsx3 natively saves as WAV.
        If the user chose .mp3, we try pydub; fallback to .wav.
        """
        if not text.strip():
            raise ValueError("No text to save.")

        # Always save WAV first
        wav_path = filepath
        if filepath.lower().endswith(".mp3"):
            wav_path = filepath[:-4] + "_temp.wav"

        self.engine.save_to_file(text, wav_path)
        self.engine.runAndWait()

        # Attempt MP3 conversion
        if filepath.lower().endswith(".mp3"):
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_wav(wav_path)
                audio.export(filepath, format="mp3")
                os.remove(wav_path)          # clean up temp WAV
                return filepath
            except Exception:
                # pydub unavailable → rename temp WAV, inform caller
                final_wav = filepath[:-4] + ".wav"
                os.rename(wav_path, final_wav)
                return final_wav             # caller will show a note

        return filepath


# ══════════════════════════════════════════════════════════
#  Main Application Window
# ══════════════════════════════════════════════════════════
class TextVoiceApp(tk.Tk):
    """Main application class – assembles all UI widgets."""

    # ── Color palette (modern vibrant theme) ──────────────
    CLR = {
        "bg":        "#EEF2FF",
        "sidebar":   "#0F172A",
        "sidebar2":  "#1E293B",
        "card":      "#FFFFFF",
        "accent":    "#6366F1",
        "accent2":   "#10B981",
        "danger":    "#F43F5E",
        "text":      "#0F172A",
        "muted":     "#64748B",
        "border":    "#CBD5E1",
        "highlight": "#E0E7FF",
        "sidebar_text": "#E2E8F0",
        "sidebar_muted": "#94A3B8",
        "ink":       "#334155",
    }

    def __init__(self):
        super().__init__()
        self.tts = TTSEngine()
        self._speak_thread = None

        self._build_window()
        self._configure_styles()
        self._build_sidebar()
        self._build_main_area()
        self._populate_voices()
        self._bind_shortcuts()

    # ══════════════════════════════════════════════════════
    #  Window Setup
    # ══════════════════════════════════════════════════════
    def _build_window(self):
        self.title("TextVoice Pro")
        self.geometry("980x680")
        self.minsize(820, 580)
        self.configure(bg=self.CLR["bg"])
        self.resizable(True, True)

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 980) // 2
        y = (self.winfo_screenheight() - 680) // 2
        self.geometry(f"+{x}+{y}")

        # Custom fonts
        self.font_title  = font.Font(family="Segoe UI", size=14, weight="bold")
        self.font_label  = font.Font(family="Segoe UI", size=10)
        self.font_button = font.Font(family="Segoe UI", size=10, weight="bold")
        self.font_small  = font.Font(family="Segoe UI", size=8)
        self.font_mono   = font.Font(family="Consolas",  size=10)
        self.font_subtitle = font.Font(family="Segoe UI", size=9)
        self.font_title_big = font.Font(family="Segoe UI", size=16, weight="bold")

    def _configure_styles(self):
        """Central ttk styling for a cleaner, consistent look."""
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "TVP.TCombobox",
            fieldbackground=self.CLR["sidebar2"],
            background=self.CLR["sidebar2"],
            foreground=self.CLR["sidebar_text"],
            bordercolor="#475569",
            lightcolor="#475569",
            darkcolor="#475569",
            arrowcolor=self.CLR["sidebar_text"],
            padding=6,
        )
        style.map(
            "TVP.TCombobox",
            fieldbackground=[("readonly", self.CLR["sidebar2"])],
            foreground=[("readonly", self.CLR["sidebar_text"])],
            selectbackground=[("readonly", self.CLR["sidebar2"])],
            selectforeground=[("readonly", self.CLR["sidebar_text"])],
        )
        style.configure(
            "Vertical.TScrollbar",
            troughcolor="#F1F5F9",
            background="#C7D2FE",
            bordercolor="#F1F5F9",
            arrowcolor="#475569",
        )

    # ══════════════════════════════════════════════════════
    #  Sidebar (Controls Panel)
    # ══════════════════════════════════════════════════════
    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=self.CLR["sidebar"], width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # ── Logo / Title ───────────────────────────────────
        logo_frame = tk.Frame(sidebar, bg=self.CLR["sidebar"])
        logo_frame.pack(fill="x", padx=20, pady=(24, 16))

        tk.Label(
            logo_frame, text="🔊", font=("Segoe UI Emoji", 22),
            bg=self.CLR["sidebar"], fg="#FFFFFF"
        ).pack(side="left")

        title_frame = tk.Frame(logo_frame, bg=self.CLR["sidebar"])
        title_frame.pack(side="left", padx=(10, 0))
        tk.Label(
            title_frame, text="TextVoice Pro",
            font=self.font_title, bg=self.CLR["sidebar"], fg="#FFFFFF"
        ).pack(anchor="w")
        tk.Label(
            title_frame, text="Text-to-Speech Tool",
            font=self.font_subtitle, bg=self.CLR["sidebar"], fg=self.CLR["sidebar_muted"]
        ).pack(anchor="w")

        # Divider
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill="x", padx=20, pady=6)

        voice_section = self._sidebar_section(sidebar)
        speed_section = self._sidebar_section(sidebar)
        volume_section = self._sidebar_section(sidebar)
        file_section = self._sidebar_section(sidebar)

        # ── Voice Selection ────────────────────────────────
        self._sidebar_label(voice_section, "VOICE")

        self.voice_var = tk.StringVar()
        self.voice_combo = ttk.Combobox(
            voice_section, textvariable=self.voice_var,
            state="readonly", font=self.font_label, width=24,
            style="TVP.TCombobox"
        )
        self.voice_combo.pack(padx=14, pady=(6, 12), fill="x")
        self.voice_combo.bind("<<ComboboxSelected>>", self._on_voice_change)

        # ── Speed Selection ────────────────────────────────
        self._sidebar_label(speed_section, "SPEED")

        self.speed_var = tk.StringVar(value="Normal")
        speed_frame = tk.Frame(speed_section, bg=self.CLR["sidebar2"])
        speed_frame.pack(padx=14, pady=(6, 12), anchor="w")

        for label in ("Slow", "Normal", "Fast"):
            rb = tk.Radiobutton(
                speed_frame, text=label, variable=self.speed_var,
                value=label, command=self._on_speed_change,
                bg=self.CLR["sidebar2"], fg=self.CLR["sidebar_text"],
                selectcolor=self.CLR["sidebar2"],
                activebackground=self.CLR["sidebar2"],
                activeforeground="#FFFFFF",
                font=self.font_label, cursor="hand2"
            )
            rb.pack(side="left", padx=(0, 12))

        # ── Volume Slider ──────────────────────────────────
        self._sidebar_label(volume_section, "VOLUME")

        vol_row = tk.Frame(volume_section, bg=self.CLR["sidebar2"])
        vol_row.pack(padx=14, pady=(6, 12), fill="x")

        self.vol_label = tk.Label(
            vol_row, text="100%", width=4,
            bg=self.CLR["sidebar2"], fg=self.CLR["sidebar_text"],
            font=self.font_small
        )
        self.vol_label.pack(side="right")

        self.vol_var = tk.DoubleVar(value=1.0)
        vol_slider = tk.Scale(
            vol_row, from_=0.0, to=1.0, orient="horizontal",
            resolution=0.05, variable=self.vol_var,
            command=self._on_volume_change,
            bg=self.CLR["sidebar2"], fg=self.CLR["sidebar_muted"],
            troughcolor="#2E3F55", highlightthickness=0,
            activebackground=self.CLR["accent"],
            showvalue=False, length=160
        )
        vol_slider.pack(side="left", fill="x", expand=True)

        # ── File Actions ───────────────────────────────────
        self._sidebar_label(file_section, "FILE")

        self._sidebar_btn(
            file_section, "📂  Load .txt File",
            self._load_file, self.CLR["accent"]
        )
        self._sidebar_btn(
            file_section, "💾  Save as Audio File",
            self._save_audio, self.CLR["accent2"]
        )

        # ── Spacer + version ───────────────────────────────
        tk.Frame(sidebar, bg=self.CLR["sidebar"]).pack(fill="y", expand=True)
        tk.Label(
            sidebar, text="v1.0  •  Offline TTS",
            font=self.font_small, bg=self.CLR["sidebar"], fg="#4A6070"
        ).pack(pady=12)

    def _sidebar_section(self, parent):
        panel = tk.Frame(
            parent, bg=self.CLR["sidebar2"],
            highlightbackground="#334155", highlightthickness=1
        )
        panel.pack(fill="x", padx=14, pady=(8, 0))
        return panel

    def _sidebar_label(self, parent, text):
        tk.Label(
            parent, text=text, font=self.font_small,
            bg=self.CLR["sidebar2"], fg=self.CLR["sidebar_muted"]
        ).pack(anchor="w", padx=14, pady=(10, 0))

    def _sidebar_btn(self, parent, text, command, color):
        btn = tk.Button(
            parent, text=text, command=command,
            bg=color, fg="#FFFFFF", relief="flat",
            font=self.font_button, cursor="hand2",
            padx=12, pady=8, bd=0, activeforeground="#FFFFFF",
            activebackground=self._darken(color, 0.80)
        )
        btn.pack(padx=14, pady=(6, 4), fill="x")
        # Hover effect
        btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=self._darken(c)))
        btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))

    @staticmethod
    def _darken(hex_color, factor=0.85):
        """Return a slightly darker version of a hex colour."""
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return "#{:02x}{:02x}{:02x}".format(
            int(r * factor), int(g * factor), int(b * factor)
        )

    # ══════════════════════════════════════════════════════
    #  Main Content Area
    # ══════════════════════════════════════════════════════
    def _build_main_area(self):
        main = tk.Frame(self, bg=self.CLR["bg"])
        main.pack(side="left", fill="both", expand=True)

        # ── Top header bar ─────────────────────────────────
        header = tk.Frame(main, bg=self.CLR["card"], height=66)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="Enter or paste your text below",
            font=self.font_title_big, bg=self.CLR["card"],
            fg=self.CLR["text"]
        ).pack(side="left", padx=24, pady=(8, 2), anchor="s")
        tk.Label(
            header, text="Craft natural speech in one click",
            font=self.font_subtitle, bg=self.CLR["card"], fg=self.CLR["muted"]
        ).pack(side="left", padx=(0, 24), pady=(34, 8), anchor="s")

        # Character counter (right-aligned)
        self.char_count_var = tk.StringVar(value="0 characters")
        tk.Label(
            header, textvariable=self.char_count_var,
            font=self.font_small, bg=self.CLR["card"],
            fg=self.CLR["muted"]
        ).pack(side="right", padx=24)

        # Thin shadow line
        tk.Frame(main, bg=self.CLR["border"], height=1).pack(fill="x")

        # ── Text editor card ───────────────────────────────
        editor_frame = tk.Frame(main, bg=self.CLR["bg"], padx=20, pady=16)
        editor_frame.pack(fill="both", expand=True)

        card = tk.Frame(
            editor_frame, bg="#F8FAFC",
            highlightbackground=self.CLR["border"],
            highlightthickness=2
        )
        card.pack(fill="both", expand=True)

        # Text widget + scrollbar
        self.text_area = tk.Text(
            card, wrap="word", font=self.font_mono,
            bg="#F8FAFC", fg=self.CLR["text"],
            insertbackground=self.CLR["accent"],
            relief="flat", padx=16, pady=14,
            undo=True, selectbackground=self.CLR["highlight"],
            selectforeground=self.CLR["text"]
        )
        scrollbar = ttk.Scrollbar(card, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.text_area.pack(fill="both", expand=True)
        self.text_area.bind("<KeyRelease>", self._update_char_count)

        # Placeholder text
        self._set_placeholder()

        # ── Status bar ─────────────────────────────────────
        status_bar = tk.Frame(main, bg=self.CLR["card"], height=32)
        status_bar.pack(fill="x")
        status_bar.pack_propagate(False)
        tk.Frame(main, bg=self.CLR["border"], height=1).pack(fill="x", before=status_bar)

        self.status_var = tk.StringVar(value="Ready")
        self.status_dot = tk.Label(
            status_bar, text="●", font=self.font_small,
            bg=self.CLR["card"], fg=self.CLR["accent2"]
        )
        self.status_dot.pack(side="left", padx=(16, 4))
        tk.Label(
            status_bar, textvariable=self.status_var,
            font=self.font_small, bg=self.CLR["card"],
            fg=self.CLR["muted"]
        ).pack(side="left")

        # Shortcut hint
        tk.Label(
            status_bar, text="Ctrl+Enter  Speak  │  Ctrl+S  Save  │  Ctrl+O  Open",
            font=self.font_small, bg=self.CLR["card"], fg=self.CLR["muted"]
        ).pack(side="right", padx=16)

        # ── Action buttons row ─────────────────────────────
        btn_row = tk.Frame(main, bg=self.CLR["bg"], padx=20, pady=14)
        btn_row.pack(fill="x")

        self.speak_btn = self._action_btn(
            btn_row, "▶  Speak Text", self._speak,
            self.CLR["accent"], width=18
        )
        self.speak_btn.pack(side="left", padx=(0, 10))

        self.stop_btn = self._action_btn(
            btn_row, "■  Stop", self._stop_speech,
            self.CLR["danger"], width=10
        )
        self.stop_btn.pack(side="left", padx=(0, 10))

        self._action_btn(
            btn_row, "🗑  Clear", self._clear_text,
            self.CLR["muted"], width=10
        ).pack(side="left")

    def _action_btn(self, parent, text, command, bg, width=14):
        btn = tk.Button(
            parent, text=text, command=command,
            bg=bg, fg="#FFFFFF", relief="flat",
            font=self.font_button, cursor="hand2",
            padx=14, pady=10, width=width, bd=0,
            activebackground=self._darken(bg, 0.80),
            activeforeground="#FFFFFF"
        )
        btn.bind("<Enter>", lambda e, b=btn, c=bg: b.config(bg=self._darken(c)))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))
        return btn

    # ══════════════════════════════════════════════════════
    #  Placeholder Helpers
    # ══════════════════════════════════════════════════════
    PLACEHOLDER = "Type or paste your text here…"

    def _set_placeholder(self):
        self.text_area.insert("1.0", self.PLACEHOLDER)
        self.text_area.config(fg="#B0BAC8")
        self.text_area.bind("<FocusIn>",  self._clear_placeholder)
        self.text_area.bind("<FocusOut>", self._restore_placeholder)

    def _clear_placeholder(self, _=None):
        if self.text_area.get("1.0", "end-1c") == self.PLACEHOLDER:
            self.text_area.delete("1.0", "end")
            self.text_area.config(fg=self.CLR["text"])

    def _restore_placeholder(self, _=None):
        if not self.text_area.get("1.0", "end-1c").strip():
            self.text_area.insert("1.0", self.PLACEHOLDER)
            self.text_area.config(fg="#B0BAC8")

    def _get_text(self):
        """Return actual text (ignoring placeholder)."""
        content = self.text_area.get("1.0", "end-1c")
        return "" if content == self.PLACEHOLDER else content

    # ══════════════════════════════════════════════════════
    #  Control Events
    # ══════════════════════════════════════════════════════
    def _populate_voices(self):
        """Fill voice dropdown from available system voices."""
        options = self.tts.get_voice_options()
        if not options:
            messagebox.showwarning("No Voices", "No TTS voices found on this system.")
            return

        # Ensure duplicate display names do not overwrite each other.
        display_names = []
        self._voice_map = {}
        duplicates = {}
        for name, vid in options:
            count = duplicates.get(name, 0) + 1
            duplicates[name] = count
            label = name if count == 1 else f"{name} ({count})"
            display_names.append(label)
            self._voice_map[label] = vid

        self.voice_combo["values"] = display_names
        self.voice_combo.current(0)
        self.tts.set_voice(self._voice_map[display_names[0]])

    def _on_voice_change(self, _=None):
        selected = self.voice_var.get()
        vid = self._voice_map.get(selected)
        if vid:
            self.tts.set_voice(vid)
            self._set_status(f"Voice: {selected}", "blue")

    def _on_speed_change(self):
        label = self.speed_var.get()
        self.tts.set_rate(label)
        self._set_status(f"Speed: {label}", "blue")

    def _on_volume_change(self, _=None):
        val = self.vol_var.get()
        self.tts.set_volume(val)
        self.vol_label.config(text=f"{int(val * 100)}%")

    def _update_char_count(self, _=None):
        text = self._get_text()
        n = len(text)
        words = len(text.split()) if text else 0
        self.char_count_var.set(f"{n} characters  •  {words} words")

    # ══════════════════════════════════════════════════════
    #  Speak / Stop
    # ══════════════════════════════════════════════════════
    def _speak(self, _=None):
        """Start speaking in a background thread."""
        text = self._get_text()
        if not text.strip():
            messagebox.showinfo("Empty Text", "Please enter some text first.")
            return

        if self._speak_thread and self._speak_thread.is_alive():
            self._stop_speech()

        self._set_status("Speaking…", "green")
        self.speak_btn.config(state="disabled")

        def _run():
            try:
                self.tts.speak(text)
            finally:
                self.after(0, self._on_speak_done)

        self._speak_thread = threading.Thread(target=_run, daemon=True)
        self._speak_thread.start()

    def _stop_speech(self):
        self.tts.stop()
        self._set_status("Stopped", "orange")
        self.speak_btn.config(state="normal")

    def _on_speak_done(self):
        self._set_status("Ready", "green")
        self.speak_btn.config(state="normal")

    # ══════════════════════════════════════════════════════
    #  File Operations
    # ══════════════════════════════════════════════════════
    def _load_file(self):
        """Open a .txt file and load its content into the editor."""
        path = filedialog.askopenfilename(
            title="Open Text File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self._clear_placeholder()
            self.text_area.delete("1.0", "end")
            self.text_area.insert("1.0", content)
            self.text_area.config(fg=self.CLR["text"])
            self._update_char_count()
            self._set_status(f"Loaded: {os.path.basename(path)}", "green")
        except Exception as e:
            messagebox.showerror("File Error", f"Could not read file:\n{e}")

    def _save_audio(self):
        """Save current text as an audio file (WAV or MP3)."""
        text = self._get_text()
        if not text.strip():
            messagebox.showinfo("Empty Text", "Nothing to save. Enter some text first.")
            return

        path = filedialog.asksaveasfilename(
            title="Save Audio File",
            defaultextension=".mp3",
            filetypes=[
                ("MP3 Audio", "*.mp3"),
                ("WAV Audio", "*.wav"),
            ]
        )
        if not path:
            return

        self._set_status("Saving audio…", "blue")
        self.update()

        try:
            saved_path = self.tts.save_audio(text, path)
            if saved_path != path:
                # MP3 conversion failed; saved as WAV instead
                messagebox.showinfo(
                    "Saved as WAV",
                    f"MP3 conversion requires pydub + ffmpeg.\n"
                    f"File saved as WAV instead:\n{saved_path}"
                )
            else:
                messagebox.showinfo("Saved", f"Audio saved to:\n{saved_path}")
            self._set_status(f"Saved: {os.path.basename(saved_path)}", "green")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save audio:\n{e}")
            self._set_status("Save failed", "red")

    # ══════════════════════════════════════════════════════
    #  Utility
    # ══════════════════════════════════════════════════════
    def _clear_text(self):
        self.text_area.delete("1.0", "end")
        self._restore_placeholder()
        self.char_count_var.set("0 characters  •  0 words")
        self._set_status("Cleared", "blue")

    def _set_status(self, msg: str, color: str = "green"):
        colors = {
            "green":  "#17C37B",
            "blue":   "#2E7CF6",
            "orange": "#F5A623",
            "red":    "#E74C3C",
        }
        self.status_var.set(msg)
        self.status_dot.config(fg=colors.get(color, "#17C37B"))

    def _bind_shortcuts(self):
        self.bind("<Control-Return>", self._speak)
        self.bind("<Control-s>",      lambda _: self._save_audio())
        self.bind("<Control-o>",      lambda _: self._load_file())


# ══════════════════════════════════════════════════════════
#  Entry Point
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = TextVoiceApp()
    app.mainloop()
