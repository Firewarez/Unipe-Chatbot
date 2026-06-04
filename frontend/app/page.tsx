import { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import Header from "@/components/header";

export const metadata: Metadata = {
  title: 'ChatBot da Unipê v1',
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
}

export default function Home() {
  return (
    <div className="home-wrapper">
      <Header />
      
      <main className="home-main">
        <div className="home-title-container">
          <Image 
            src="/Logo2.png" 
            alt="Logo Unipê"
            width={150}          
            height={150}
            className="home-title-logo"
          />
          <h1 className="home-title">ChatBot Unipê</h1>
        </div>
        
        <div className="home-grid">
          <a 
            href="https://novoportal.cruzeirodosul.edu.br/gfa/home" 
            className="home-card"
          >
            <span>Acessar Área do Aluno</span>
          </a>

          <a 
            href="https://bb.cruzeirodosulvirtual.com.br/" 
            className="home-card"
          >
            <span>Acessar Blackboard</span>
          </a>

          <Link 
            href="/Chat" 
            className="home-card"
          >
            <span>Iniciar conversa com o ChatBot</span>
          </Link>
        </div>
      </main>
    </div>
  );
}