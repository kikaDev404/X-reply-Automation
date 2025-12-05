from queue import Queue, Empty
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from pynput import keyboard
from openai import OpenAI
from utils_lib import*
from twitter_actions import*
from dotenv import load_dotenv
import os
from nicegui import ui
from threading import Thread
import threading
import sys


load_dotenv(override=True)
# --- CONFIGURATION ---
LLM_URL = os.getenv('LLM_URL')
LLM_API_KEY =  os.getenv('LLM_KEY') # Update to your specific model name

client = OpenAI(base_url=LLM_URL, api_key=LLM_API_KEY)

# Queue for thread-safe actions
task_queue = Queue()

def on_press(key):
    """Runs in background thread → signals main thread."""
    if key == keyboard.Key.f9:
        task_queue.put(("reply", False))
    elif key == keyboard.Key.f10:
        task_queue.put(("reply", True))

def start_app():
    with sync_playwright() as p:
        try:
            # Ensure this URL matches your Chrome debugger port
            browser = p.chromium.connect_over_cdp(os.getenv('HOST_ADDRESS'))
            context = browser.contexts[0]
            page = context.pages[0]

            print("Connected to Chrome!")
            print("Focus Chrome window now.")
            print("[F9]  = Write Draft")
            print("[F10] = Write + Send + Next Tweet")

            listener = keyboard.Listener(on_press=on_press)
            listener.start()

            # MAIN LOOP
            while True:
                try:
                    task, auto_send = task_queue.get(timeout=0.1)
                    if task == "reply":
                        action_reply_current(client,page, auto_send)
                except Empty:
                    continue
                except KeyboardInterrupt:
                    break

        except Exception as e:
            print(f"Connection failed: {e}", flush=True)
            print("Run browser in debug mode")

log_box = ui.log(max_lines=300).classes("w-full h-96")


def start_main():
    count = sum(1 for t in threading.enumerate() if t.name == "XAuto")
    if count == 0:
        Thread(target=start_app, daemon=True, name="XAuto").start()
        log_in_ui(log_box,"Playwright thread started")
    else:
        log_in_ui(log_box,"Existing Thread found")



ui.button("Start", on_click=start_main)
ui.run()


