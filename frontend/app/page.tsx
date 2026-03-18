import {Metadata} from "next";
import Link from "next/link"

export const metadata: Metadata = {
  title: 'ChatBot da Unipê v1',
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

export default function Home() {
  return (
    <main className="min-h-screen">
        <h1 className='Titulohome'>ChatBot Unipê</h1>
      <div className='Botaolinks'>
        <a href="https://novoportal.cruzeirodosul.edu.br/gfa/home" className="LinkArealuno">Acessar Área do Aluno</a>
        <a href="https://bb.cruzeirodosulvirtual.com.br/" className='linkBB' >Acessar Blackboard</a>
        <Link href="/Chat" className='comecarchat'>Iniciar conversa com o ChatBot</Link>
      </div>
    </main>
  );
}
