from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class Prompt(BaseModel):
    prompt: str

async def generate(prompt: str):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        for chunk in completion:
            text = chunk.choices[0].delta.content or ""
            if text:
                yield f"data: {text}\n\n"
    except Exception as e:
        yield f"data: Error: {str(e)}\n\n"

@app.post("/stream")
async def stream(request: Prompt):
    return StreamingResponse(
        generate(request.prompt),
        media_type="text/event-stream"
    )
