import {Metadata} from "next";
import Image from "next/image";

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
    <div>
      <h1>Pagina do chat</h1>
    </div>
  );
}
