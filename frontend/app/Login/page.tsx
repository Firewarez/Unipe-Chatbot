"use client"
import { useState } from "react";
import Link from "next/link"
import Image from "next/image";

export default function Login() {
    const [email, setEmail] = useState("");
    const [senha, setSenha] = useState("");

    function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    console.log("Enviando para o Python:", { email, senha });
  }
  return (
    <main className="relative flex min-h-screen items-center justify-center p-4">
      <div className="fixed inset-0 -z-10">
        <Image
          src="/TOPO_estrela.jpg"
          alt="Background Unipê"
          fill
          priority
          className="object[0%_0%_35%] brightness-[0.3]"
        />
      </div>
      <div className="w-full max-w-md bg-gray-800/80 backdrop-blur-sm p-8 rounded-2xl shadow-xl border border-gray-700">
        <h1 className="text-3xl font-bold text-center mb-6 text-yellow-500">Unipê ChatBot</h1>
        <p className="text-center text-gray-400 mb-8">Faça login para continuar</p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block mb-2 text-sm text-white">E-mail</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="seu-email@cs.unipe.edu.br"
              required
              className="w-full p-3 rounded bg-gray-900/50 border border-gray-600 text-white focus:outline-none focus:border-blue-500 transition"
            />
          </div>

          <div>
            <label className="block mb-2 text-sm text-white">Senha</label>
            <input 
              type="password" 
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              placeholder="••••••••"
              required
              className="w-full p-3 rounded bg-gray-900/50 border border-gray-600 text-white focus:outline-none focus:border-blue-500 transition"
            />
          </div>

          <button 
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg mt-4 transition-colors"
          >
            Entrar
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-400">
          Não tem uma conta? <Link href="/Cadastro" className="text-blue-500 hover:underline">Cadastre-se</Link>
        </p>
      </div>
    </main>
  );
}