# ✨ Glint AI Assistant

**Glint** is a lightweight, high-speed AI text-processing utility for Windows 11. It lives in your system tray and empowers your clipboard with the world's most advanced language models (Llama 3.3 70B via Groq) using simple, global hotkeys.

![Glint Preview](https://github.com/user-attachments/assets/069f7e5d-ff86-437e-802e-58313dc7ca70)

---

## 🚀 Core Features

- **🪄 Grammar Fixer (`Ctrl + Alt + G`)**: Instantly correct spelling, grammar, and punctuation while preserving your original tone and formatting (including HTML).
- **🗨️ Answer Mode (`Ctrl + Alt + A`)**: Highlight a question or a prompt and get a lightning-fast, concise answer in a dedicated reading window.
- **📝 Summarize (`Ctrl + Alt + S`)**: Turn long emails or articles into 3-5 concise bullet points in seconds.
- **✨ Custom Prompt (`Ctrl + Alt + P`)**: The ultimate power tool. Highlight text and type a custom instruction—like "Make this sound more professional" or "Translate this to Spanish."

---

## 💎 Windows 11 Native Experience

Glint isn't just functional; it's designed to feel like part of the OS:

- **Mica Backdrop**: Uses the official Windows 11 "frosted glass" effect for all windows.
- **Immersive Dark Mode**: Follows your system theme with high-contrast, premium visuals.
- **Segoe UI Variable**: Optimized for the modern Windows 11 typography.

---

## ⚡ Instant Mode & Persistence

- **Instant Mode**: Trust the AI? Enable "Instant Mode" in the tray to bypass the preview window and paste corrections directly into your active app.
- **Persistent Settings**: Your preferences (Enabled/Disabled, Instant Mode) are automatically saved to `config.json` and restored whenever you restart.

---

## 🛠️ Installation

### 1. Prerequisites

- **Python 3.10+**
- A **Groq API Key** (Get one for free at [console.groq.com](https://console.groq.com/keys))

### 2. Setup

Clone the repository and install the dependencies:

```bash
git clone https://github.com/your-username/Glint.git
cd Glint
pip install -r requirements.txt
```

### 3. Run

Simply run the script:

```bash
python Glint.pyw
```

On the first run, Glint will automatically prompt you to enter your **Groq API Key**.

---

## ⌨️ Global Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + Alt + G` | **Grammar Fixer** (Correct text) |
| `Ctrl + Alt + A` | **Answer Mode** (Get clean AI answers) |
| `Ctrl + Alt + S` | **Summarize** (Bullet point summary) |
| `Ctrl + Alt + P` | **Custom Prompt** (AI instruction popup) |

---

## 🤝 Contributing

Feel free to fork this project and submit pull requests! Whether it's a new feature, a UI improvement, or a bug fix, all contributions are welcome.

## 📄 License

This project is licensed under the MIT License.

---
*Built with ❤️ for high-speed productivity.*
