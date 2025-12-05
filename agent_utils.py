from dotenv import load_dotenv
import os

load_dotenv(override=True)

MODEL_NAME = os.getenv('model_name')

def call_agent(agent,user_message):
    try:
        response = agent.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": user_message}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip().strip('"')
    except Exception as e:
        print(f"AI Error: {e}")
        return  