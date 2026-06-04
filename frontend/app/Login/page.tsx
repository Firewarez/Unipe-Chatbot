"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";

export default function Login() {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    console.log("Enviando para o Python:", { email, senha });
  }

  return (
    <main className="auth-main">
      <div className="auth-bg-wrapper">
        <Image
          src="/TOPO_estrela.jpg"
          alt="Background Unipê"
          fill
          priority
          className="auth-bg-image"
        />
      </div>
      <div className="auth-card">
        <h1 className="auth-title">Unipê ChatBot</h1>
        <p className="auth-subtitle">Faça login para continuar</p>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>E-mail</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="seu-email@cs.unipe.edu.br"
              required
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Senha</label>
            <input 
              type="password" 
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              placeholder="••••••••"
              required
              className="form-input"
            />
          </div>

          <button type="submit" className="auth-button">
            Entrar
          </button>
        </form>

        <p className="auth-footer-text">
          Não tem uma conta? <Link href="/Cadastro" className="auth-link">Cadastre-se</Link>
        </p>
      </div>
    </main>
  );
}