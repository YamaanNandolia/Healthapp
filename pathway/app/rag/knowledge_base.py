import pathway as pw
from pathway.xpacks.llm.embedders import OpenAIEmbedder
from app.config import OPENAI_API_KEY, EMBEDDING_MODEL
from app.utils.text_utils import form_to_text, session_to_text


def build_knowledge_base(forms: pw.Table, sessions: pw.Table) -> pw.Table:
    """
    Takes raw 'form' and 'session' tables and produces a unified
    `knowledge_chunks` table with text + embeddings.
    """
    embedder = OpenAIEmbedder(
        model=EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY,
    )

    # --- FORM TEXT ---
    form_text = forms.select(
        patient_id=forms.patient_id,
        source_type=pw.literal("form"),
        source_ref=forms.id,
        text=pw.apply(form_to_text, forms.questions, forms.answers),
    ).filter(lambda row: row.text != "")

    # --- SESSION TEXT ---
    session_text = sessions.select(
        patient_id=sessions.patient_id,
        source_type=pw.literal("session"),
        source_ref=sessions.id,
        text=pw.apply(session_to_text, sessions.summary, sessions.medications),
    ).filter(lambda row: row.text != "")

    # Combine
    raw_knowledge = form_text.concat_rows(session_text)

    # Add embeddings
    knowledge_chunks = raw_knowledge.select(
        "*",
        embedding=embedder(raw_knowledge.text),
    )

    return knowledge_chunks
