import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set")

if not model:
    raise ValueError("GROQ_MODEL is not set")

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model=model,
    max_completion_tokens=200,
    messages=[
        {
            "role": "user",
            "content": "Explain what a pharmaceutical customer complaint is in one sentence."
        }
    ],
)

print("AI response:")
print(response.choices[0].message.content)