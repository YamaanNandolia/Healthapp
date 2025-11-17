# pathway/app/chat_routes.py

from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from supabase import create_client, Client
import os

from dotenv import load_dotenv
from pathway.xpacks.llm.embedders import OpenAIEmbedder
from pathway.xpacks.llm.llms import OpenAIChat

# ---------------------------------------------------------------------
# Environment / config
# ---------------------------------------------------------------------

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials are missing. Check your .env")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing. Check your .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter()

# ---------------------------------------------------------------------
# Pathway LLM xPack objects (embedder optional here, but ready for RAG)
# ---------------------------------------------------------------------

embedder = OpenAIEmbedder(
    model="text-embedding-3-small",
    api_key=OPENAI_API_KEY,
)

chat_llm = OpenAIChat(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    temperature=0.1,
)

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def build_session_context(row: Dict) -> str:
    """
    Turn one session row into a text block for the LLM context.
    Uses transcript, summary, and medications.
    """
    transcript = row.get("transcript") or ""
    summary = row.get("summary") or ""
    medications = row.get("medications") or []

    # medications is jsonb: expect list of {name, reason}
    med_lines: List[str] = []
    if isinstance(medications, list):
        for m in medications:
            if not isinstance(m, dict):
                continue
            name = m.get("name", "unknown")
            reason = m.get("reason", "")
            med_lines.append(f"- {name}: {reason}")

    meds_block = "\n".join(med_lines) if med_lines else "No medications recorded."

    parts = [
        "=== Session Summary ===",
        summary or "No summary available.",
        "",
        "=== Transcript ===",
        transcript or "No transcript available.",
        "",
        "=== Medications ===",
        meds_block,
    ]

    return "\n".join(parts)


def run_session_chat(patient_id: str, question: str, session_id: Optional[str] = None) -> dict:
    """
    - Fetch a session for this patient (latest or by session_id)
    - Build context from transcript + summary + medications
    - Ask LLM with that context
    """
    # 1) Select session row from Supabase
    if session_id:
        query = (
            supabase.table("session")
            .select("id, patient_id, transcript, summary, medications, created_at")
            .eq("id", session_id)
            .limit(1)
        )
    else:
        # latest session for this patient
        query = (
            supabase.table("session")
            .select("id, patient_id, transcript, summary, medications, created_at")
            .eq("patient_id", patient_id)
            .order("created_at", desc=True)
            .limit(1)
        )

    result = query.execute()

    rows = result.data or []
    if not rows:
        raise HTTPException(
            status_code=404,
            detail="No session found for this patient (and session_id, if provided).",
        )

    session_row = rows[0]
    context = build_session_context(session_row)

    # 2) Build prompt for LLM
    system_prompt = (
        "You are a helpful, empathetic healthcare assistant.\n"
        "You are answering questions about a past medical session based ONLY on the provided context.\n"
        "Do NOT invent diagnoses or treatments.\n"
        "If something is unclear or serious, tell the patient to contact their doctor or emergency services.\n"
    )

    user_prompt = (
        f"Patient question: {question}\n\n"
        f"Here is the context from their last session:\n\n{context}"
    )

    # 3) Call Pathway LLM xPack (OpenAIChat wrapper)
    answer_text = chat_llm(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    return answer_text


# ---------------------------------------------------------------------
# API endpoint: GET /api/chat
# ---------------------------------------------------------------------


@router.get("/chat")
def chat_with_patient_session(
    patient_id: str,
    question: str,
    session_id: Optional[str] = None,
):
    """
    GET /api/chat?patient_id=...&question=...&session_id=optional

    - Does NOT write to the database.
    - Reads `session` table (transcript, summary, medications).
    - Uses Pathway's OpenAIChat to answer based on that context.
    """
    try:
        result = run_session_chat(patient_id=patient_id, question=question, session_id=session_id)
        return {
            "patient_id": patient_id,
            "question": question,
            "answer": result["answer"],
            "session_id": result["session_id"],
            "context_flags": {
                "summary": result["used_summary"],
                "transcript": result["used_transcript"],
                "medications": result["used_medications"],
            },
        }
    except HTTPException:
        # re-raise specific HTTP errors
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
