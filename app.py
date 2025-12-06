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
stop_event = threading.Event()


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
            while not stop_event.is_set():
                try:
                    task, auto_send = task_queue.get(timeout=0.1)
                    if task == "reply":
                        action_reply_current(client,page, auto_send)
                except Empty:
                    continue
                except KeyboardInterrupt:
                    break
                
            listener.stop()
            log_in_ui(log_box, "XAuto thread stopped.")

        except Exception as e:
            print(f"Connection failed: {e}", flush=True)
            print("Run browser in debug mode")

log_box = ui.log(max_lines=300).classes("w-full h-96")


def start_main():
    count = get_thread_count("XAuto")
    if count == 0:
        stop_event.clear()
        Thread(target=start_app, daemon=True, name="XAuto").start()
        log_in_ui(log_box,"XAuto thread started")
    else:
        log_in_ui(log_box,"Existing Thread found")

def stop_main():
    thread_count = get_thread_count("XAuto")
    if thread_count == 0 :
        log_in_ui(log_box,"Application is not running")
    else:
        stop_event.set()
        log_in_ui(log_box, "Stop signal sent to XAuto thread")

def start_auto_reply():
    if get_thread_count("XAuto") != 0:
        log_in_ui(log_box, "Application is now running in Auto reply mode")
        task_queue.put(("reply", True))
    else:
        log_in_ui(log_box, "Start the application before starting auto replying")


ui.button("Start", on_click=start_main)
ui.button("Stop", on_click=stop_main)
ui.button("Start Auto Reply", on_click=start_auto_reply)
ui.run(native=True)


