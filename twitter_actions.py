from agent_utils import*
import time
import random

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

