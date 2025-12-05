from nicegui import ui
from threading import Thread
import threading
import sys
from app import main

log_box = ui.log(max_lines=300).classes("w-full h-96")

def log_in_ui(msg):
    log_box.push(msg)
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()

def get_logger():
    return log

def start_main():
    count = sum(1 for t in threading.enumerate() if t.name == "XAuto")
    if count == 0:
        Thread(target=main, daemon=True, name="XAuto").start()
        log("Playwright thread started")
    else:
        log("Existing Thread found")

ui.button("Start", on_click=start_main)

ui.run()
