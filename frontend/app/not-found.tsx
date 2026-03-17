import Link from "next/link";

export default function NotFound(){
    return(
        <div className="flex flex-col items-center justify-center">
            <h1 className="text-center font-bold mt-9 text-6xl">Erro 404 Essa página não existe</h1>
            <p className="mt-5">essa página que você tentou acessar não existe</p>
            <Link href='/'>
                Voltar para a página inicial
            </Link>
        </div>
    )
}