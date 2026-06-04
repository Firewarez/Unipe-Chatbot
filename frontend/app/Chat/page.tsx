"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";

interface Mensagem {
  id: string;
  conteudo: string;
  remetente: "usuario" | "bot";
  timestamp: string;
}

export default function Chat() {
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [input, setInput] = useState("");
  const [carregando, setCarregando] = useState(false);

  const usuarioId = "brenno_user";
  const conversaId = "conversa_central_unipe_01"; 

  const URL_API = "http://127.0.0.1:8000/api/chat";
  const fimDasMensagensRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function carregarHistorico() {
      try {
        const res = await fetch(`${URL_API}/conversa/${conversaId}/mensagens`);
        if (res.ok) {
          const dados = await res.json();
          setMensagens(dados);
        }
      } catch (err) {
        console.error(err);
      }
    }
    carregarHistorico();
  }, [conversaId]);

  useEffect(() => {
    fimDasMensagensRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [mensagens]);

  async function handleEnviar(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || carregando) return;

    const textoUsuario = input;
    setInput("");
    setCarregando(true);

    const mensagemProvisoriaUsuario: Mensagem = {
      id: crypto.randomUUID(),
      conteudo: textoUsuario,
      remetente: "usuario",
      timestamp: new Date().toISOString()
    };
    setMensagens((prev) => [...prev, mensagemProvisoriaUsuario]);

    try {
      const res = await fetch(`${URL_API}/mensagem`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversa_id: conversaId,
          conteudo: textoUsuario,
          usuario_id: usuarioId
        })
      });

      if (!res.ok) throw new Error();

      const dadosJson = await res.json();

      setMensagens((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          conteudo: dadosJson.resposta,
          remetente: "bot",
          timestamp: new Date().toISOString()
        }
      ]);
    } catch (err) {
      console.error(err);
      setMensagens((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          conteudo: "⚠️ Ops, falha ao conectar com o servidor local. O Ollama e o backend Python estão rodando?",
          remetente: "bot",
          timestamp: new Date().toISOString()
        }
      ]);
    } finally {
      setCarregando(false);
    }
  }

  return (
    <main className="chat-container">
      <header className="chat-header">
        <Link href="/" className="chat-back-link">
          ← Voltar para Home
        </Link>
        <span className="chat-header-title">Unipê Assistant v1</span>
        <div className="chat-header-spacer"></div>
      </header>

      <div className="chat-messages-area">
        {mensagens.length === 0 ? (
          <div className="chat-empty-state">
            <p className="chat-empty-title">Como posso ajudar hoje?</p>
            <p className="chat-empty-subtitle">Envie uma mensagem abaixo para iniciar a consulta inteligente.</p>
          </div>
        ) : (
          mensagens.map((msg) => (
            <div
              key={msg.id}
              className={`message-row ${msg.remetente === "usuario" ? "message-row-user" : "message-row-bot"}`}
            >
              <div className="message-wrapper">
                <div className={`message-avatar ${msg.remetente === "usuario" ? "avatar-user" : "avatar-bot"}`}>
                  {msg.remetente === "usuario" ? "U" : "AI"}
                </div>
                <p className="message-text">{msg.conteudo}</p>
              </div>
            </div>
          ))
        )}
        
        {carregando && (
          <div className="message-row message-row-bot">
            <div className="message-wrapper">
              <div className="message-avatar avatar-bot">AI</div>
              <div className="chat-loading-wrapper">
                <span>●</span><span>●</span><span>●</span>
                <span style={{ fontSize: "13px", marginLeft: "8px" }}>Consultando RAG...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={fimDasMensagensRef} />
      </div>

      <div className="chat-form-container">
        <form onSubmit={handleEnviar} className="chat">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite sua dúvida sobre a Unipê..."
            className="chat-input"
            disabled={carregando}
          />
          <button type="submit" className="enviar" disabled={carregando || !input.trim()}>
            {carregando ? "..." : "➔"}
          </button>
        </form>
      </div>
    </main>
  );
}