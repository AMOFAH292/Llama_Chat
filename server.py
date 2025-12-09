from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow your Flutter app to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class Prompt(BaseModel):
    prompt: str


# -----------------------------------------------------
# HOME ROUTE → fixes the 404 errors in Render logs
# -----------------------------------------------------
@app.get("/")
def home():
    return {"message": "Llama API is live 🚀"}


# -----------------------------------------------------
# NON-STREAM CHAT
# -----------------------------------------------------
@app.post("/chat")
def chat(request: Prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": request.prompt}],
            stream=False
        )

        return {
            "response": completion.choices[0].message.content
        }

    except Exception as e:
        return {"error": str(e)}


# -----------------------------------------------------
# STREAMING CHAT (for real-time responses)
# -----------------------------------------------------
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
