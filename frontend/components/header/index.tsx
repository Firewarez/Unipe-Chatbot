import Link from "next/link";
import Image from "next/image";

export default function Header() {
  return (
    <header className="flex px-3 py-4 bg-zinc-900 text-white border-b border-zinc-800">
      <div className="flex items-center justify-between w-full px-4">
        <div>
          <div className="flex items-center gap-2">
            <Image 
              src="/Logo.png" 
              alt="Logo ChatBot" 
              width={150} 
              height={150}
              className="object-contain"
            />
          </div>
        </div>
        <nav>
          <ul className="flex items-center justify-center">
            <li>
              <Link 
                href='/Login' 
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-5 py-2 rounded-full transition-all duration-200 shadow-md hover:shadow-lg active:scale-95 block text-sm"
              >
                Acessar Conta
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
}