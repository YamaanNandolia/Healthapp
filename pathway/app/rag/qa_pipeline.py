from typing import Dict
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_rag_query(question: str, context: Dict) -> str:
    """Combines DB context + model response"""

    system_prompt = f"""
    You are a clinical assistant AI. Use only the context provided.
    --- CONTEXT ---
    Transcript: {context.get("transcript", "")}
    Summary: {context.get("summary", "")}
    Medications: {context.get("medications", "")}
    ----------------
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0.2
    )

    return completion.choices[0].message.content
