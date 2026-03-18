export default function Chat(){
    return(
        <div className="chat">
            <input 
                type="text" 
                placeholder="Digite sua dúvida..." 
                className="chat-input"
            />
            <button className="enviar">Enviar</button>
        </div>
    )
}