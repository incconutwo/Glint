import os
import re
import gc
import time
import queue
import threading
import pyperclip
import keyboard
from groq import Groq
import config
from src.clipboard.manager import get_clipboard_html

correction_queue = queue.Queue()

client = None

def init_client():
    global client
    if config.GROQ_API_KEY:
        try:
            client = Groq(api_key=config.GROQ_API_KEY)
        except Exception as e:
            print(f"Groq setup err: {e}")

def update_api_key(new_key):
    global client
    config.GROQ_API_KEY = new_key.strip()
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.env")
    with open(env_path, "w") as f:
        f.write(f"GROQ_API_KEY={config.GROQ_API_KEY}\n")
    try:
        client = Groq(api_key=config.GROQ_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}")

def _clean_response(text):
    text = text.strip()
    if (text.startswith('"') and text.endswith('"')) or \
       (text.startswith("'") and text.endswith("'")):
        text = text[1:-1]
    text = re.sub(r'^```\w*\n', '', text)
    text = re.sub(r'```$', '', text)
    return text.strip()

def _capture_clipboard():
    pyperclip.copy('')
    keyboard.press_and_release('ctrl+c')
    for _ in range(10):
        html_text, is_html = get_clipboard_html()
        if is_html and html_text:
            return html_text, True
        plain_text = pyperclip.paste()
        if plain_text:
            return plain_text, False
        time.sleep(0.05)
    return "", False

def process_text_and_api(mode="correction"):
    if not config.APP_ENABLED:
        return
    if not config.GROQ_API_KEY or not client:
        correction_queue.put((None, None, None, False, "api_key_missing"))
        return

    original_clipboard_content = pyperclip.paste()
    keyboard.release('ctrl')
    keyboard.release('alt')
    keyboard.release('shift')
    time.sleep(0.1)

    text, is_html = _capture_clipboard()

    if not text.strip():
        keyboard.press_and_release('ctrl+a')
        time.sleep(0.1)
        text, is_html = _capture_clipboard()

    if not text.strip():
        pyperclip.copy(original_clipboard_content)
        return

    if mode == "ask_prompt":
        correction_queue.put((original_clipboard_content, text, None, is_html, "ask_prompt"))
        return

    try:
        if mode == "summarize":
            messages = [
                {"role": "system", "content": config.SUMMARIZE_SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ]
        elif mode == "answer":
            messages = [
                {"role": "system", "content": config.ANSWER_SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ]
        else:
            messages = [
                {"role": "system", "content": config.SYSTEM_PROMPT},
                {"role": "user", "content": f'Input: "{text}"\nOutput:'}
            ]

        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            temperature=0.0,
            timeout=10
        )
        corrected_text = _clean_response(response.choices[0].message.content)
        correction_queue.put((original_clipboard_content, text, corrected_text, is_html, mode))
    except Exception as e:
        print(f"Error during correction: {e}")
        pyperclip.copy(original_clipboard_content)
    finally:
        gc.collect()

def run_custom_api(original_clipboard, text, is_html, user_prompt):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant. Return ONLY the modified text."},
            {"role": "user", "content": f"Request: {user_prompt}\n\nText: {text}"}
        ]
        response = client.chat.completions.create(
            model=config.MODEL, messages=messages, temperature=0.2, timeout=15
        )
        corrected_text = _clean_response(response.choices[0].message.content)
        correction_queue.put((original_clipboard, text, corrected_text, is_html, "custom"))
    except Exception as e:
        print(f"Error during custom prompt: {e}")
        pyperclip.copy(original_clipboard)
    finally:
        gc.collect()