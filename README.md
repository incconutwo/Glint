# ✨ Glint AI Assistant

**Glint** is a premium, keyboard-first AI utility for Windows 11/10 designed to be your invisible text-processing companion. Highlight text in *any* application and instantly refine, answer, or summarize without ever breaking your flow.

Built for extreme speed using **Llama 3.3 70B** via **Groq**, Glint feels like a native OS feature rather than a separate application.

---

## 👻 The Ghost HUD
Glint now features the **Ghost HUD**—a sleek, non-intrusive floating "pill" that appears exactly where you are typing.

- **Context-Aware Placement**: It tracks your text caret and appears exactly where your eyes are already focused.
- **Shimmering Progress**: Visual feedback while the AI is thinking.
- **Instant Preview**: See the correction preview before you accept it.
- **Keyboard Mastery**: Press `Enter` to Accept, `Escape` to Cancel, or `↗` to open the full side-by-side Review window.

---

## 🚀 Core Features

- **🪄 Grammar Fixer (`Ctrl + Alt + G`)**: Instantly correct spelling and punctuation while preserving tone.
- **🗨️ Answer Mode (`Ctrl + Alt + A`)**: Get lightning-fast, concise answers to questions in a clean reading window.
- **📝 Summarize (`Ctrl + Alt + S`)**: Turn long text into actionable bullet points in seconds.
- **✨ Custom Prompt (`Ctrl + Alt + P`)**: Highlight text and give a custom command (e.g., "Translate to French" or "Make it funnier").

---

## 💎 Premium Experience

- **Windows 11 Native**: Beautiful **Mica** transparency, Segoe UI Variable typography, and immersive Dark Mode.
- **High-DPI Aware**: Perfectly crisp text and UI on 4K and high-resolution monitors.
- **⚡ Instant Mode**: Toggle "Instant Mode" in the tray to bypass reviews and paste corrections directly.
- **System Tray Control**: Manage settings, toggle startup behavior, or **Restart** the app instantly from the taskbar.

---

## ⌨️ Shortcuts

| Shortcut | Function | HUD Key |
| :--- | :--- | :--- |
| `Ctrl + Alt + G` | **Grammar** (Correction) | `Enter` = Accept |
| `Ctrl + Alt + A` | **Answer** (Q&A) | `Esc` = Reject |
| `Ctrl + Alt + S` | **Summarize** (Bullets) | `↗` = Full Diff |
| `Ctrl + Alt + P` | **Prompt** (Custom) | |

---

## 🛠️ Installation

### 1. Prerequisites
- **Python 3.10+**
- A **Groq API Key** ([console.groq.com](https://console.groq.com/keys))

### 2. Setup
```bash
git clone https://github.com/incconu_two/Glint.git
cd Glint
pip install -r requirements.txt
```

### 3. Run
```bash
python Glint.pyw
```
On first run, Glint will prompt for your API key. You can update this anytime via **Settings**.

---

## 📄 License
This project is licensed under the MIT License.

---
*Built with ❤️ for high-speed productivity.*
