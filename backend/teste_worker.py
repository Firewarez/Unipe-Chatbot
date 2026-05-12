import pika
import json
import uuid
from datetime import datetime

def enviar_evento_teste():
    # Configuração da conexão com o RabbitMQ no seu Zorin OS
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Garante que o exchange existe
    channel.exchange_declare(exchange='chat.events', exchange_type='topic')

    # Payload simulando o evento de "mensagem_enviada" do handler
    payload = {
        "conversa_id": str(uuid.uuid4()),
        "mensagem_id": str(uuid.uuid4()),
        "conteudo": "Olá, este é um teste de integração do Worker!",
        "remetente": "usuario",
        "usuario_id": "brenno_user",
        "timestamp": datetime.now().isoformat()
    }

    # Publica o evento
    channel.basic_publish(
        exchange='chat.events',
        routing_key='mensagem_enviada',
        body=json.dumps(payload)
    )

    print(f" [x] Evento de teste enviado: {payload['conteudo']}")
    connection.close()

if __name__ == "__main__":
    enviar_evento_teste()