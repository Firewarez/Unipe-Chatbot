import Link from "next/link";
import { Metadata } from "next";
import Image from "next/image";

export const metadata: Metadata = {
  title: 'ChatBot da Unipê v1 - Login',
  description: 'Chat para tirar dúvidas sobre a instituição.',
  openGraph: {
    title: 'ChatBot da Unipê v1',
    description: 'Chat para tirar dúvidas sobre a instituição.',
  },
  robots: {
    index: true,
    follow: true,
    nocache: true,
    googleBot: {
      index: true,
      follow: true,
      noimageindex: true,
    }
  }
};

export default function Cadastro() {
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
        <p className="auth-subtitle">Crie sua conta</p>

        <form className="auth-form">
          <div className="form-group">
            <label>E-mail</label>
            <input 
              type="email" 
              placeholder="seu-email@cs.unipe.edu.br"
              className="form-input"
            />
          </div>
          <div className="form-group">
            <label>Senha</label>
            <input 
              type="password" 
              placeholder="••••••••"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Confirmar senha</label>
            <input 
              type="password" 
              placeholder="••••••••"
              className="form-input"
            />
          </div>

          <button type="submit" className="auth-button">
            Cadastrar
          </button>
        </form>
      </div>
    </main>
  );
}