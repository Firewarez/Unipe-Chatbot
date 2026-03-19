"""main.py - Equiv. Program.cs. Ponto de entrada FastAPI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chat.api.controllers.chat_controller import router as chat_router
from chat.infrastructure.data.database import criar_tabelas

criar_tabelas()

app = FastAPI(title="ChatBot UNIPÊ", description="API do chatbot com IA para o UNIPÊ", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(chat_router)


@app.get("/")
def root():
    return {"status": "online", "message": "ChatBot UNIPÊ API v1.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
