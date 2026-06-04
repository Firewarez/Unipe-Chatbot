import os
import json
# Desativa os erros chatos de telemetria do ChromaDB no terminal
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings # Atualizado para evitar avisos
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM # Atualizado para a versão nova do LangChain

# 1. Carregar os dados
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
caminho_json = os.path.join(_project_root, 'data', 'unipe_knowledge.json')

with open(caminho_json, 'r', encoding='utf-8') as arquivo:
    dados = json.load(arquivo)
    if isinstance(dados, dict):
        dados = [dados]

documentos = []
for item in dados:
    doc = Document(
        page_content=item['conteudo'],
        metadata={"titulo": item['titulo'], "fonte": item['fonte'], "categoria": item['categoria']}
    )
    documentos.append(doc)

# 2. Criar a Busca Inteligente
print("Preparando a base de conhecimento...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
banco_vetorial = Chroma.from_documents(documentos, embeddings, persist_directory="./chroma_data")
buscador = banco_vetorial.as_retriever(search_kwargs={"k": 1})

# 3. Configurar o Ollama (Importação nova)
llm = OllamaLLM(model="llama3.2:1b") 

# 4. Criar o Prompt (Simplificado para modelos menores de 1B parâmetros)
prompt = ChatPromptTemplate.from_template("""
Responda à pergunta usando APENAS as informações do Texto Base.
Se a resposta não estiver no texto, diga apenas "Informação não encontrada".
Seja direto e curto.

Texto Base:
{context}

Pergunta: {input}
Resposta:
""")

# 5. Montar o Chatbot
chain_documentos = create_stuff_documents_chain(llm, prompt)
chatbot = create_retrieval_chain(buscador, chain_documentos)

# 6. Testar o bot
pergunta = "Qual é a nota do UNIPÊ no MEC?"
print(f"\nUsuário: {pergunta}")
print("Bot está pensando...\n")

resposta = chatbot.invoke({"input": pergunta})

print("🤖 Resposta:", resposta['answer'].strip())
print("📚 Fonte utilizada:", resposta['context'][0].metadata['fonte'])