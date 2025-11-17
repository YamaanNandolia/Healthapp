from fastapi import FastAPI
from app.chat_routes import router as chat_router

app = FastAPI()

# include routes
app.include_router(chat_router, prefix="/api")

@app.get("/")
def root():
    return {"status": "running", "message": "ML API is live"}
