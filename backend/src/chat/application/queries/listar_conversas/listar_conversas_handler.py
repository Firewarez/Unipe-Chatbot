from chat.infrastructure.data.database import SessionLocal, ConversaModel

class ListarConversasHandler:
    def handle(self, query: 'ListarConversasQuery'):
        db = SessionLocal()
        try:
            return db.query(ConversaModel).filter_by(usuario_id=query.usuario_id).all()
        finally:
            db.close()