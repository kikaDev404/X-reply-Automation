from agent_utils import*
import time
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from pynput import keyboard
from utils_lib import*
from twitter_actions import*
from nicegui import ui
from threading import Thread

def generate_reply(tweet_text, agent):
    """Generates a short, casual crypto-twitter reply."""
    prompt = f"""
    You are a crypto native Twitter user.
    Reply to this tweet casually, lowercase, maybe a bit witty or agreeing. 
    Keep it under 280 chars. No hashtags. Never add any hashtags or mentions. Never use any markdowns. you should keep the reply small and very precise. no yapping too much.
    
    Tweet: "{tweet_text}"
    """
    return call_agent(agent, prompt)

def type_like_human(page, text):
    """Types text with random delays to mimic human behavior."""
    for char in text:
        page.keyboard.type(char)
        time.sleep(random.uniform(0.01, 0.05))

def action_reply_current(agent,page, auto_send=False):
    try:
        print("Finding tweet...")
        page.keyboard.press("j") # I think I may need to remove this. I need to test more before confirming
        

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
        reply_text = generate_reply(tweet_text, agent)
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
            action_reply_current(agent,page, auto_send=True)
        else:
            print("Draft ready. Review and click Reply.")

    except Exception as e:
        print(f"Error in action: {e}")

