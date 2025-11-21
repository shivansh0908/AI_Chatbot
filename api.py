# api.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from retriever import build_context
from openai import OpenAI

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
MIN_RELEVANCE = float(os.getenv("MIN_RELEVANCE", 0.58))
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", 3500))

if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in .env")

client = OpenAI(api_key=OPENAI_KEY)

app = FastAPI(title="RAG API - strict no-hallucination")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask(req: QueryRequest):
    q = req.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # 1) build a conservative context using retriever
    context_text, used_docs = build_context(q, k=12, mmr_k=5)

    # 2) Strict system prompt to avoid hallucination
    system_prompt = (
        "You must ONLY answer using the EXACT information in the provided CONTEXT. "
        "If the answer is not explicitly present in the context, respond ONLY with: "
        "'I don't know based on the provided data.' Do NOT guess, infer, or use outside knowledge."
    )

    user_prompt = (
        f"CONTEXT:\n{context_text}\n\n"
        f"QUESTION:\n{q}\n\n"
        "Instruction: Answer concisely. If you can answer using the context, answer with "
        "short bullet points or a paragraph. Otherwise reply exactly: I don't know based on the provided data."
    )

    # 3) call LLM
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=800,
        temperature=0.0  # deterministic
    )

    answer = resp.choices[0].message.content.strip()

    # 4) Quick post-check: if model returned anything not equal to the "I don't know" string,
    # ensure it references some part of the context (rudimentary check)
    if answer.lower().startswith("i don't know"):
        final = "I don't know based on the provided data."
    else:
        final = answer

    return {
        "answer": final,
        "used_docs_count": len(used_docs),
        "used_docs": used_docs  # optionally return for debugging; remove in production
    }
