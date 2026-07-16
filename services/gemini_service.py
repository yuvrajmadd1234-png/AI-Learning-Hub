import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def ask_ai(prompt):

    system_prompt = """
    You are an AI Study Assistant for an E-Learning Platform.

    Rules:
    - Explain concepts in simple language.
    - Use headings.
    - Use bullet points.
    - Give one real-life example.
    - End with a short summary.
    - If appropriate, provide 3-5 key takeaways.
    - Keep answers educational, accurate, and concise.
    - If the user asks non-academic questions, politely answer briefly and guide back to learning.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{system_prompt}\n\nStudent Question:\n{prompt}"
    )

    return response.text