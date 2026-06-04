"""Importa paginas oficiais para o ChromaDB a partir de uma lista de URLs.

Uso:
  cd backend
  $env:PYTHONPATH="src"; python -m chat.infrastructure.data_loader.ingest_urls
  $env:PYTHONPATH="src"; python -m chat.infrastructure.data_loader.ingest_urls --urls ../data/unipe_urls.txt
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Iterable

import httpx

from chat.infrastructure.external_services.chroma_service import ChromaDBService


REMOVER_TAGS = {"script", "style", "noscript", "svg", "canvas", "form"}
QUEBRAS_TAGS = {"p", "br", "li", "h1", "h2", "h3", "h4", "section", "article", "div"}


class TextoHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignorar: list[str] = []
        self._partes: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in REMOVER_TAGS:
            self._ignorar.append(tag)
        if tag in QUEBRAS_TAGS and not self._ignorar:
            self._partes.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self._ignorar and self._ignorar[-1] == tag:
            self._ignorar.pop()
        if tag in QUEBRAS_TAGS and not self._ignorar:
            self._partes.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._ignorar:
            self._partes.append(data)

    def texto(self) -> str:
        texto = html.unescape(" ".join(self._partes))
        texto = re.sub(r"[ \t\r\f\v]+", " ", texto)
        texto = re.sub(r"\n\s+", "\n", texto)
        texto = re.sub(r"\n{3,}", "\n\n", texto)
        linhas = [linha.strip() for linha in texto.splitlines()]
        linhas = [linha for linha in linhas if linha and not _parece_navegacao(linha)]
        return "\n".join(linhas).strip()


@dataclass(frozen=True)
class Documento:
    titulo: str
    conteudo: str
    fonte: str
    categoria: str


def _parece_navegacao(linha: str) -> bool:
    if len(linha) <= 2:
        return True
    lixo = {
        "menu",
        "buscar",
        "acesse",
        "entrar",
        "fechar",
        "voltar",
        "cookies",
        "accept",
        "facebook",
        "instagram",
        "linkedin",
        "youtube",
    }
    normalizada = linha.lower().strip(" .:-")
    return normalizada in lixo


def _extrair_titulo(html_texto: str, url: str) -> str:
    for pattern in (r"<h1[^>]*>(.*?)</h1>", r"<title[^>]*>(.*?)</title>"):
        match = re.search(pattern, html_texto, flags=re.IGNORECASE | re.DOTALL)
        if match:
            titulo = re.sub(r"<[^>]+>", " ", match.group(1))
            titulo = re.sub(r"\s+", " ", html.unescape(titulo)).strip()
            if titulo:
                return titulo
    return url.rstrip("/").split("/")[-1].replace("-", " ").title() or "Pagina do UNIPE"


def _inferir_categoria(url: str) -> str:
    url_lower = url.lower()
    categorias = {
        "processo-seletivo": "ingresso",
        "vestibular": "ingresso",
        "enem": "ingresso",
        "bolsa": "financeiro",
        "prouni": "financeiro",
        "fies": "financeiro",
        "curso": "cursos",
        "graduacao": "cursos",
        "pos": "pos-graduacao",
        "atendimento": "atendimento",
        "contato": "contato",
        "clinica": "servicos-comunidade",
    }
    for termo, categoria in categorias.items():
        if termo in url_lower:
            return categoria
    return "site-oficial"


def _quebrar_em_blocos(texto: str, tamanho_max: int = 1400) -> list[str]:
    paragrafos = [p.strip() for p in re.split(r"\n+", texto) if len(p.strip()) >= 40]
    blocos: list[str] = []
    atual = ""

    for paragrafo in paragrafos:
        if len(paragrafo) > tamanho_max:
            if atual:
                blocos.append(atual.strip())
                atual = ""
            frases = re.split(r"(?<=[.!?])\s+", paragrafo)
            for frase in frases:
                if len(atual) + len(frase) + 1 > tamanho_max and atual:
                    blocos.append(atual.strip())
                    atual = ""
                atual = f"{atual} {frase}".strip()
            continue

        if len(atual) + len(paragrafo) + 2 > tamanho_max and atual:
            blocos.append(atual.strip())
            atual = ""
        atual = f"{atual}\n\n{paragrafo}".strip()

    if atual:
        blocos.append(atual.strip())
    return blocos


def _ler_urls(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        urls = []
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                urls.append(linha)
        return urls


def _ler_json_manual(path: str) -> list[Documento]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        dados = json.load(f)
    return [
        Documento(
            titulo=item["titulo"],
            conteudo=item["conteudo"],
            fonte=item["fonte"],
            categoria=item["categoria"],
        )
        for item in dados
    ]


def _extrair_texto_reader(markdown: str) -> tuple[str, str]:
    titulo = "Pagina do UNIPE"
    linhas_conteudo: list[str] = []

    for linha in markdown.splitlines():
        linha = linha.strip()
        if not linha:
            linhas_conteudo.append("")
            continue
        if linha.lower().startswith("title:"):
            titulo = linha.split(":", 1)[1].strip() or titulo
            continue
        if linha.lower().startswith(("url source:", "markdown content:", "published time:")):
            continue
        if "javascript:void" in linha.lower():
            continue
        linha = re.sub(r"!\[[^\]]*]\([^)]+\)", "", linha)
        linha = re.sub(r"\[]\([^)]+\)", "", linha)
        linha = re.sub(r"\[([^\]]+)]\([^)]+\)", r"\1", linha)
        linha = re.sub(r"\s{2,}", " ", linha).strip()
        if not linha or _parece_navegacao(linha):
            continue
        linhas_conteudo.append(linha)

    texto = "\n".join(linhas_conteudo)
    texto = re.sub(r"\n{3,}", "\n\n", texto).strip()
    return titulo, texto


def _baixar_via_reader(client: httpx.Client, url: str) -> tuple[str, str] | None:
    reader_url = f"https://r.jina.ai/{url}"
    try:
        resposta = client.get(reader_url)
        resposta.raise_for_status()
    except httpx.HTTPError as exc:
        print(f"  Reader falhou: {exc}")
        return None
    return _extrair_texto_reader(resposta.text)


def _baixar_documentos(urls: Iterable[str], usar_reader: bool = True) -> list[Documento]:
    documentos: list[Documento] = []
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    with httpx.Client(headers=headers, follow_redirects=True, timeout=30) as client:
        for url in urls:
            print(f"Baixando: {url}")
            titulo: str
            texto: str
            try:
                resposta = client.get(url)
                resposta.raise_for_status()
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if not usar_reader:
                    print(f"  Ignorado: HTTP {status}. O site pode ter bloqueado acesso automatico.")
                    continue
                print(f"  HTTP {status}; tentando fallback com Jina Reader...")
                resultado_reader = _baixar_via_reader(client, url)
                if resultado_reader is None:
                    continue
                titulo, texto = resultado_reader
            except httpx.HTTPError as exc:
                if not usar_reader:
                    print(f"  Ignorado: falha ao baixar ({exc}).")
                    continue
                print(f"  Falha ao baixar direto; tentando fallback com Jina Reader...")
                resultado_reader = _baixar_via_reader(client, url)
                if resultado_reader is None:
                    continue
                titulo, texto = resultado_reader
            else:
                html_texto = resposta.text
                titulo = _extrair_titulo(html_texto, url)
                parser = TextoHTMLParser()
                parser.feed(html_texto)
                texto = parser.texto()

            blocos = _quebrar_em_blocos(texto)
            blocos = [bloco for bloco in blocos if bloco.strip()]
            categoria = _inferir_categoria(url)

            for indice, bloco in enumerate(blocos, start=1):
                documentos.append(
                    Documento(
                        titulo=f"{titulo} - Parte {indice}" if len(blocos) > 1 else titulo,
                        conteudo=bloco,
                        fonte=url,
                        categoria=categoria,
                    )
                )
            print(f"  {len(blocos)} bloco(s) extraido(s)")

    return documentos


def _documento_id(prefixo: str, doc: Documento, indice: int) -> str:
    base = f"{doc.fonte}|{doc.titulo}|{indice}".encode("utf-8")
    return f"{prefixo}_{hashlib.sha1(base).hexdigest()[:16]}"


def importar_urls(urls_path: str, json_path: str, incluir_json: bool = True, usar_reader: bool = True) -> None:
    urls = _ler_urls(urls_path)
    if not urls:
        print(f"Nenhuma URL encontrada em {urls_path}.")
        return

    documentos = _baixar_documentos(urls, usar_reader=usar_reader)
    if incluir_json:
        documentos = _ler_json_manual(json_path) + documentos

    chroma = ChromaDBService()
    chroma.limpar_documentos()

    print(f"\nCarregando {len(documentos)} documentos/blocos no ChromaDB...")
    for indice, doc in enumerate(documentos):
        chroma.adicionar_documento(
            documento_id=_documento_id("unipe_url", doc, indice),
            conteudo=f"{doc.titulo}\n\n{doc.conteudo}",
            metadata={"titulo": doc.titulo, "fonte": doc.fonte, "categoria": doc.categoria},
        )
    print(f"Sucesso! {chroma.contar_documentos()} documentos/blocos carregados.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Importa paginas do site oficial do UNIPE para o ChromaDB.")
    parser.add_argument("--urls", default=os.path.normpath(os.path.join(os.getcwd(), "..", "data", "unipe_urls.txt")))
    parser.add_argument("--json", default=os.path.normpath(os.path.join(os.getcwd(), "..", "data", "unipe_knowledge.json")))
    parser.add_argument("--sem-json", action="store_true", help="Nao inclui os documentos manuais do JSON.")
    parser.add_argument("--sem-reader", action="store_true", help="Nao usa Jina Reader como fallback para sites bloqueados.")
    args = parser.parse_args()

    importar_urls(
        urls_path=args.urls,
        json_path=args.json,
        incluir_json=not args.sem_json,
        usar_reader=not args.sem_reader,
    )


if __name__ == "__main__":
    main()
