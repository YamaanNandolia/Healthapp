# Pathway Microservice

This directory contains the **Pathway-powered Retrieval-Augmented Generation (RAG)** engine used in our **HealthAI** project.  
It ingests patient session data and medications from Supabase, embeds them using Pathway’s vector store, and retrieves the most relevant context to answer patient questions safely.

---

## What This Service Does

### **1. Loads patient data from Supabase**
For each patient session we collect:
- Session transcript  
- Summary written by clinician  
- Medications (JSON list)  
- Timestamp  

---

### **2. Builds a Pathway Vector Index**
Pathway converts:
- Medication records  
- Session summaries  
- Transcript text  

…into embeddings stored inside Pathway’s in-memory vector index.

This index enables **fast similarity search** when a patient asks a question.

---

### **3. Performs RAG (Retrieval-Augmented Generation)**

When a user sends a question:

1. Their question is embedded by Pathway  
2. Pathway searches the vector index for the most relevant text  
3. Relevant session pieces + medications are returned  
4. A safe medical prompt is constructed  
5. OpenAI generates a natural-language answer  

---

### **4. Exposes a FastAPI Endpoint**

```
GET /api/chat?patient_id=...&question=...&session_id=optional
```

This endpoint:
- Retrieves session data from Supabase  
- Performs Pathway vector search  
- Builds context for the LLM  
- Returns a safe, patient-friendly response  

Example response:

```json
{
  "patient_id": "1111-2222-3333-4444",
  "question": "Summarize my last session",
  "answer": "In your last session, you discussed..."
}
```

---

## 📁 Folder Structure

```
pathway/
│
├── chat_routes.py       # API endpoints and RAG logic
├── knowledge_base.py    # Pathway ingestion of sessions + medications
├── qa_pipeline.py       # Pathway vector search pipeline
├── config.py            # .env configuration loader
├── main.py              # FastAPI app entry point
├── requirements.txt     # Python dependencies
└── Dockerfile           # Docker container for this microservice
```

---

## Docker Deployment

### **Build the container**
```sh
docker build -t pathway-service .
```

### **Run the container**
```sh
docker run -p 8000:8000 --env-file .env pathway-service
```

### Required `.env` variables
```
SUPABASE_URL=...
SUPABASE_KEY=...
OPENAI_API_KEY=...
```

---

## How Pathway Is Used

### **Pathway Vector Store**

Pathway embeds and stores all patient-specific knowledge, including:

- Medication lists  
- Session summaries  
- Transcript chunks  

This allows the chatbot to:
- Retrieve *only* the relevant session details  
- Keep responses grounded in real medical data  
- Avoid hallucinations  
- Respond instantly  

### **Architecture Overview**

```
          Supabase
              │
              ▼
   Pathway Ingestion Layer
   (sessions + meds → embeddings)
              │
              ▼
     Pathway Vector Index
              │
              │  (similarity search)
              ▼
User Question → Embedding → Pathway Search → Best Context
              │
              ▼
        OpenAI LLM → Final Answer
```

---

## Example Request

```
curl "http://127.0.0.1:8000/api/chat?patient_id=1111-2222-3333-4444&question=Summarize%20my%20last%20session"
```

---

## Summary

This microservice combines:

- **Supabase** for structured medical data  
- **Pathway** for real-time vector search  
- **OpenAI** for natural-language responses  
- **FastAPI** for a clean HTTP interface  

Together, they create a safe, fast, and intelligent medical chatbot experience.
