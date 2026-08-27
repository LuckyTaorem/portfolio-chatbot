import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

app = FastAPI()

# --- Security: Only allow your portfolio to use this API ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://luckytaorem.github.io", "http://127.0.0.1:5500", "http://localhost:5500"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq (Fallback safely if key isn't set yet)
groq_key = os.environ.get("GROQ_API_KEY", "missing_key")
llm_client = Groq(api_key=groq_key)

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
    return {"status": "Vercel Serverless Function is Awake!"}

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
    
    # --- ROBUST MULTI-PROVIDER WATERFALL CONFIGURATION ---
    model_settings = [
        {"provider": "groq", "model": "openai/gpt-oss-120b"},
        {"provider": "groq", "model": "openai/gpt-oss-20b"},
        {"provider": "openrouter", "model": "google/gemma-4-31b-it"},
        {"provider": "gemini", "model": "gemini-2.5-flash"},
        {"provider": "cohere", "model": "command-a-03-2025"}
    ]

    answer = None

    for setting in model_settings:
        provider = setting['provider']
        model_name = setting['model']
        
        try:
            # 1. GROQ
            if provider == "groq":
                if groq_key == "missing_key": continue
                completion = llm_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": request.message}
                    ],
                    model=model_name,
                    temperature=0.7,
                    max_tokens=300, 
                )
                answer = completion.choices[0].message.content.strip()

            # 5. OPENROUTER
            elif provider == "openrouter":
                key = os.environ.get("OPENROUTER_API_KEY")
                if not key: continue
                res = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://luckytaorem.github.io", 
                        "X-Title": "LT Developer Portfolio Chat"
                    },
                    json={
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": request.message}
                        ],
                        "temperature": 0.7, "max_tokens": 300
                    },
                    timeout=10
                )
                if res.status_code == 200: answer = res.json()['choices'][0]['message']['content'].strip()

            elif provider == "gemini":
                key = os.environ.get("GEMINI_API_KEY")
                if not key:
                    continue
                res = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}",
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [
                            {"role": "system", "parts": [{"text": system_prompt}]},
                            {"role": "user", "parts": [{"text": request.message}]}
                        ],
                        "generationConfig": {
                            "maxOutputTokens": 300,
                            "temperature": 0.7
                        }
                    },
                    timeout=30
                )
                if res.status_code == 200:
                    data = res.json()
                    # Gemini responses are nested: candidates -> content -> parts -> text
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            answer = parts[0]["text"].strip()

            # 6. COHERE
            elif provider == "cohere":
                key = os.environ.get("COHERE_API_KEY")
                if not key: continue
                res = requests.post(
                    "https://api.cohere.com/v1/chat",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={
                        "model": model_name,
                        "message": request.message,
                        "preamble": system_prompt,
                        "max_tokens": 300
                    },
                    timeout=10
                )
                if res.status_code == 200: answer = res.json().get('text', '').strip()

            if answer:
                break

        except Exception as e:
            print(f"Provider Error ({provider}): {str(e)}")
            continue

    if answer:
        return {"reply": answer}
    else:
        return {"reply": "Sorry, my AI systems are currently updating. Please reach out to Lucky directly via the contact form!"}