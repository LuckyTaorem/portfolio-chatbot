import os
import time
import threading
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sambanova

app = FastAPI()

# --- Render Self-Ping Mechanism to prevent sleeping ---
def keep_awake():
    url = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:10000")
    while True:
        time.sleep(600)  # Ping every 10 minutes
        try:
            requests.get(url)
        except Exception:
            pass
threading.Thread(target=keep_awake, daemon=True).start()

# --- Security: Only allow your portfolio to use this API ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://luckytaorem.github.io", "http://127.0.0.1:5500", "http://localhost:5500"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load LLM and Data ---
llm_client = sambanova.SambaNova(api_key=os.environ.get("SAMBANOVA_API_KEY"))

# Read your info file into memory once when the server starts
try:
    with open("portfolio_info.txt", "r", encoding="utf-8") as f:
        portfolio_info = f.read()
except FileNotFoundError:
    portfolio_info = "Lucky is an Aspiring Web Developer and SEO Specialist."

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def keep_alive():
    return {"status": "awake"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    system_prompt = f"""You are the official AI assistant for Taorem Lucky Singh's portfolio.
    Your job is to answer questions about Lucky as if you are his personal assistant.
    Your tone should be natural, friendly, and professional—like a real person texting a recruiter or colleague.
    Keep answers concise (1 to 3 short sentences).

    CRITICAL RULE: Answer based ONLY on the following information. If the user asks something not in this text, politely say you don't know, but they can contact him directly.

    ABOUT LUCKY:
    {portfolio_info}
    """
    
    try:
        completion = llm_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            model="Meta-Llama-3.3-70B-Instruct", 
        )
        answer = completion.choices[0].message.content
        return {"reply": answer}
    except Exception as e:
        print(f"SAMBANOVA ERROR: {str(e)}") # This puts the error in your Render logs
        return {"reply": f"SYSTEM ERROR: {str(e)}"} # This prints the error in your Chat Window
