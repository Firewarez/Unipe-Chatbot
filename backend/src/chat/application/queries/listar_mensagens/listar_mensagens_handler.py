from chat.infrastructure.data.database import SessionLocal, MensagemModel

class ListarMensagensHandler:
    def handle(self, query: 'ListarMensagensQuery'):
        db = SessionLocal()
        try:
            return db.query(MensagemModel).filter_by(conversa_id=query.conversa_id).all()
        finally:
            db.close()