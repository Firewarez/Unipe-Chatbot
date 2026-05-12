import pika
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from chat.infrastructure.data.database import (
    SessionLocal, 
    ConversaModel,
    MensagemModel
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CLASSE UNIFICADA E CORRIGIDA ---
class ChatProjector:
    def __init__(self, db: Session):
        self.db = db

    def projetar_mensagem(self, payload: dict):
        """Atualiza o banco com base no payload do RabbitMQ"""
        event_id = payload.get('event_id')
        conversa_id = payload.get('conversa_id')
        conteudo = payload.get('conteudo')
        
        logger.info(f"Processando evento: {event_id} para Conversa: {conversa_id}")

        # 1. Inserir a mensagem
        nova_mensagem = MensagemModel(
            id=payload.get('mensagem_id'),
            conversa_id=conversa_id,
            conteudo=conteudo,
            remetente=payload.get('remetente'),
            timestamp=datetime.now()
        )
        self.db.add(nova_mensagem)

        # 2. Atualizar a conversa
        conversa = self.db.query(ConversaModel).filter_by(id=conversa_id).first()
        if conversa:
            conversa.ultima_mensagem = conteudo
            conversa.atualizado_em = datetime.now()
        
        self.db.commit()

# --- LÓGICA DO WORKER ---
def callback(ch, method, properties, body):
    payload = json.loads(body)
    routing_key = method.routing_key
    db = SessionLocal()
    try:
        projector = ChatProjector(db)
        projector.projetar_mensagem(payload)
        logger.info(f" [x] Evento {routing_key} processado com sucesso!")
    except Exception as e:
        db.rollback()
        logger.error(f" [!] Erro no processamento: {e}")
    finally:
        db.close()

def iniciar():
    print("--- BACKEND CHATBOT UNIPÊ: WORKER INICIADO ---")
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.exchange_declare(exchange='chat.events', exchange_type='topic')
        result = channel.queue_declare(queue='chat_read_model_queue', durable=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange='chat.events', queue=queue_name, routing_key="mensagem_enviada")
        channel.queue_bind(exchange='chat.events', queue=queue_name, routing_key="resposta_gerada")

        print(' [*] Aguardando eventos no Zorin OS. Pressione CTRL+C para sair.')
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
    except Exception as e:
        print(f" [!] Erro ao conectar no RabbitMQ: {e}")

if __name__ == "__main__":
    iniciar()