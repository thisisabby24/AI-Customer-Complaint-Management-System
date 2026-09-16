import os
from dotenv import load_dotenv
from groq import Groq


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: GROQ_API_KEY is missing")
    raise SystemExit(1)

client = Groq(api_key=api_key)


print("Testing Groq connection...")
print("Model: openai/gpt-oss-20b")


try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: GROQ WORKS"
            }
        ],
        max_completion_tokens=50,
        reasoning_effort="low"
    )

    print("\nSUCCESS!")
    print("Response:")
    print(response.choices[0].message.content)

except Exception as e:
    print("\nGROQ ERROR:")
    print(type(e).__name__)
    print(str(e))