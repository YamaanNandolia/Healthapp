from typing import List, Dict


def form_to_text(questions: List[str], answers: List[str]) -> str:
    if not questions or not answers:
        return ""
    pairs = zip(questions, answers)
    return "\n".join(f"Q: {q}\nA: {a}" for q, a in pairs)


def session_to_text(summary: str, medications: List[Dict]) -> str:
    meds_lines = []
    for m in medications or []:
        name = m.get("name", "unknown")
        reason = m.get("reason", "")
        meds_lines.append(f"- {name}: {reason}")
    meds_block = "\n".join(meds_lines)
    return f"Summary:\n{summary or ''}\n\nMedications:\n{meds_block}"
