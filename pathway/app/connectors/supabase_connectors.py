import pathway as pw
from config import POSTGRES_DSN


def read_forms() -> pw.Table:
    """
    Stream 'form' table from Supabase (Postgres).
    Schema (example):
      id: uuid
      patient_id: uuid
      doctor_id: uuid
      questions: json/array
      answers: json/array
      created_at: timestamp
    """
    return pw.io.sql.read(
        dsn=POSTGRES_DSN,
        table="form",
        mode="streaming",  # treat inserts/updates as events
    )


def read_sessions() -> pw.Table:
    """
    Stream 'session' table:
      id, patient_id, doctor_id, transcript, summary, medications (json), created_at
    """
    return pw.io.sql.read(
        dsn=POSTGRES_DSN,
        table="session",
        mode="streaming",
    )


def read_chat_questions() -> pw.Table:
    """
    Stream patient chat questions.
    Table 'chat_messages' schema example:
      id: uuid
      patient_id: uuid
      role: 'patient' | 'bot'
      text: string
      created_at: timestamp
    We filter to role == 'patient' in the pipeline.
    """
    return pw.io.sql.read(
        dsn=POSTGRES_DSN,
        table="chat_messages",
        mode="streaming",
    )


def write_bot_answers(bot_msgs: pw.Table):
    """
    Persist bot answers back to Supabase / Postgres into 'chat_messages' table.
    You can also write to another table like 'chat_answers' if you prefer.
    """
    # Map Pathway columns → DB columns
    pw.io.sql.write(
        bot_msgs,
        dsn=POSTGRES_DSN,
        table="chat_messages",
    )
