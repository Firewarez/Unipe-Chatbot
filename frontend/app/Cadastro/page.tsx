import Link from "next/link"
import {Metadata} from "next";
import Image from "next/image";

export const metadata: Metadata = {
  title: 'ChatBot da Unipê v1 - Login',
  description: 'Chat para tirar dúvidas sobre a instituição.',
  openGraph:{
    title: 'ChatBot da Unipê v1',
    description: 'Chat para tirar dúvidas sobre a instituição.',
  },
  robots: {
    index: true,
    follow: true,
    nocache: true,
    googleBot: {
      index:true,
      follow: true,
      noimageindex: true,
    }
  }
}


export default function Cadastro(){
    return(
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
        <p className="text-center text-gray-400 mb-8">Crie sua conta</p>

        <form className="flex flex-col gap-4">
          <div>
            <label className="block mb-2 text-sm text-white">E-mail</label>
            <input 
              type="email" 
              placeholder="seu-email@cs.unipe.edu.br"
              className="w-full p-3 rounded bg-gray-900/50 border border-gray-600 text-white focus:outline-none focus:border-blue-500 transition"
            />
          </div>
          <div>
            <label className="block mb-2 text-sm text-white">Senha</label>
            <input type="password" 
              placeholder="••••••••"
              className="w-full p-3 rounded bg-gray-900/50 border border-gray-600 text-white focus:outline-none focus:border-blue-500 transition"
            />
          </div>

          <div>
            <label className="block mb-2 text-sm text-white">Confirmar senha</label>
            <input 
              type="password" 
              placeholder="••••••••"
              className="w-full p-3 rounded bg-gray-900/50 border border-gray-600 text-white focus:outline-none focus:border-blue-500 transition"
            />
          </div>

          <button 
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg mt-4 transition-colors"
          >
            Cadastrar
          </button>
        </form>
      </div>
    </main>
    )
}