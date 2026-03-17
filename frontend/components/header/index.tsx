import Link from "next/link";

export function Header(){
    return(
        <header className = "flex px-3 py-4 bg-zinc-900 text-white">
            <div className = "flex items-center justify-between w-full mx-auto max-w-7x1">
                <div>
                    <Link href='/'>
                    ChatBot
                    </Link>
                </div>
                <nav>
                    <ul className = "flex items-center justify-center gap-2">
                        <li>
                            <Link href='/Login'>
                            Login
                            </Link>
                        </li>
                        <li>
                            <Link href='/Chat'>
                            Novo Chat
                            </Link>
                        </li>
                    </ul>
                </nav>
            </div>
        </header>
    )
}