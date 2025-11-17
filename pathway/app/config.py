import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Supabase 
POSTGRES_DSN = os.getenv("POSTGRES_DSN")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LLM + embedding model names
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")

# RAG parameters
TOP_K = int(os.getenv("RAG_TOP_K", "3"))
