import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Instantiating the Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

try:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say hello!",
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    print("Success! Groq says:", chat_completion.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
    