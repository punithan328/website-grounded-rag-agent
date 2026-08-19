import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

response = client.chat.completions.create(
    model=os.environ["OPENROUTER_MODEL"],
    messages=[
        {
            "role": "user",
            "content": "What is RAG?"
        }
    ],
    max_tokens=500,
)


print(response.choices[0].message.content)