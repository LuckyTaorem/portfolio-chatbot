# Portfolio AI Assistant API 🤖

A lightweight, serverless-ready FastAPI backend that powers the AI chat assistant for my developer portfolio. 

This chatbot acts as a personalized assistant, answering questions about my experience, projects, and skills based strictly on a curated knowledge base. To ensure maximum uptime and zero cost, it utilizes a custom multi-provider LLM waterfall strategy to instantly failover if an API rate limit is hit.

## 🚀 Key Features

* **Multi-Provider LLM Waterfall:** High availability through automatic failover routing across 5 distinct models (Groq → OpenRouter → Gemini → Cohere).
* **Context-Strict (RAG):** Ingests `portfolio_info.txt` on cold start and strictly anchors the AI's identity. It automatically refuses out-of-scope questions (like coding requests or unrelated topics) and drives users to the contact form.
* **Security & CORS Restriction:** Hardened to only accept requests from the official GitHub Pages domain and local development servers, protecting API quotas.
* **Serverless Optimized:** Designed to deploy seamlessly as a Vercel Serverless Function.

## 🛠️ Tech Stack

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) & Pydantic
* **LLM Clients:** Groq SDK, standard HTTP Requests
* **Providers:** 
  * Groq (`openai/gpt-oss-20b`, `openai/gpt-oss-120b`)
  * OpenRouter (`google/gemma-4-31b-it`)
  * Google Gemini (`gemini-2.5-flash`)
  * Cohere (`command-a-03-2025`)

## 📂 Project Structure

```text
├── main.py                # FastAPI application & LLM waterfall routing logic
├── portfolio_info.txt     # The static RAG knowledge base & system instructions
├── requirements.txt       # Python dependencies
└── README.md
```
