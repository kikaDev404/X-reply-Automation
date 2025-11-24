from queue import Queue, Empty
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from pynput import keyboard
from openai import OpenAI
from utils_lib import*
from twitter_actions import*
from dotenv import load_dotenv
import os

load_dotenv(override=True)
# --- CONFIGURATION ---
LLM_URL = os.getenv('LLM_URL')
LLM_API_KEY =  os.getenv('LLM_KEY') # Update to your specific model name

client = OpenAI(base_url=LLM_URL, api_key=LLM_API_KEY)

# Queue for thread-safe actions
task_queue = Queue()

def action_reply_current(page, auto_send=False):
    try:
        print("Finding tweet...")
        page.keyboard.press("j")
        

        # 1. Smart Focus Detection
        # If you clicked inside a tweet, the active element might be a span/div.
        # look for the closest PARENT that is a tweet.
        active = page.evaluate_handle("document.activeElement")
        is_tweet = active.evaluate("el => el.closest('article[data-testid=\"tweet\"]') !== null")

        if is_tweet:
            # Get the text from the tweet container
            tweet_element = active.evaluate_handle("el => el.closest('article[data-testid=\"tweet\"]')")
            tweet_text = tweet_element.inner_text()
        else:
            # Fallback: Pick first visible tweet
            print("No specific tweet focused. Picking top one.")
            tweet = page.locator('article[data-testid="tweet"]').first
            tweet.scroll_into_view_if_needed()
            tweet_text = tweet.inner_text()
            tweet.click() # Click it so 'j' works next time

        print(f"Generating reply for: {tweet_text[:40]}...")

        # 2. Open Reply Box
        page.keyboard.press("r")
        
        # Robust wait for the box to appear (max 2 sec)
        try:
            reply_box = page.get_by_role("textbox", name="Post text")
            reply_box.wait_for(state="visible", timeout=3000)
        except PlaywrightTimeout:
            print("Reply box didn't open. Press 'j' to select a tweet first.")
            return

        # 3. Generate & Type
        reply_text = generate_reply(tweet_text, client)
        print(f"Typing: {reply_text}")
        
        reply_box.click()
        type_like_human(page, process_ai_response(reply_text))

        # 4. Auto-send logic
        if auto_send:
            print("Sending...")
            page.wait_for_timeout(10_000)
            reply_box.click()
            send_button = page.locator('[data-testid="tweetButton"]')
            send_button.click()

            # Wait for the reply box to disappear (confirmation it was sent)
            # instead of a hard sleep
            try:
                reply_box.wait_for(state="hidden", timeout=5000)
                print("Reply sent.")
            except PlaywrightTimeout:
                print("Warning: Reply box still open? Check for errors.")

            print("Moving to next...")
            page.keyboard.press("j")
            action_reply_current(page, auto_send=True)
        else:
            print("Draft ready. Review and click Reply.")

    except Exception as e:
        print(f"Error in action: {e}")

def on_press(key):
    """Runs in background thread → signals main thread."""
    if key == keyboard.Key.f9:
        task_queue.put(("reply", False))
    elif key == keyboard.Key.f10:
        task_queue.put(("reply", True))

def main():
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
                        action_reply_current(page, auto_send)
                except Empty:
                    continue
                except KeyboardInterrupt:
                    break

        except Exception as e:
            print(f"Connection failed: {e}")
            print("Run browser in debug mode")

if __name__ == "__main__":
    main()
