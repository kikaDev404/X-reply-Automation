import sys
import threading

def process_ai_response(response):
    if "<think>" in response and "</think>" in response:
        # Extract everything cleanly
        before_think = response.split("<think>")[0]
        think_content = response.split("<think>")[1].split("</think>")[0]
        after_think = response.split("</think>")[1]

        # Format the think block for display
        formatted_think = f"> 💭 *{think_content.strip()}*"

        # Combine all parts
        return after_think.strip()
    else:
        return response

def log_in_ui(log_box,msg):
    log_box.push(msg)
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()

def get_thread_count(process_name : str):
    count = sum(1 for t in threading.enumerate() if t.name == process_name)
    return count
    