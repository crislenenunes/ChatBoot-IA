import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import gradio as gr
from langdetect import detect

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da API do OpenRouter
api_key = os.getenv("OPENROUTER_API_KEY", "free")
os.environ["OPENAI_API_KEY"] = api_key
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

# Inicializar modelo LLM
llm = ChatOpenAI(
    model="deepseek/deepseek-r1:free",
    temperature=0.5,
    max_tokens=1024
)

def responder(mensagem):
    try:
        prompt_inicial = (
          "Você é um assistente de uma livraria e seu papel é ajudar clientes a encontrar livros que combinem com seus gostos pessoais. "
          "Com base na descrição do cliente sobre o tipo de leitura que ele prefere (ex: gênero, autor favorito, temas, estilo), sugira livros específicos, explicando brevemente por que cada um pode ser uma boa escolha.\n\n"
          "Cliente: " + mensagem + "\n"
          "Recomendações:"
        )
        resposta = llm.invoke(prompt_inicial)
        return resposta.content
    except Exception as e:
        import traceback
        return f"❌ Erro:\n{traceback.format_exc()}"

# Saudações multilíngues
SAUDACOES = {
    'pt': ["Olá! 😊 Como posso ajudar?", "E aí! 👋 Tudo bem?", "Oi! 😄 Em que posso ajudar?"],
    'en': ["Hi! 😊 How can I help?", "Hello! 👋 How are you?", "Hey! 😄 What can I do for you?"],
    'es': ["¡Hola! 😊 ¿Cómo puedo ayudarte?", "¡Hola! 👋 ¿Qué tal?", "¡Hola! 😄 ¿En qué puedo ayudarte?"],
    'fr': ["Salut! 😊 Comment puis-je aider?", "Bonjour! 👋 Ça va?", "Coucou! 😄 Comment puis-je t'aider?"],
    'it': ["Ciao! 😊 Come posso aiutarti?", "Salve! 👋 Come stai?", "Ciao! 😄 Come posso esserti utile?"]
}

# Detectar idioma da mensagem
def detectar_idioma(texto):
    try:
        lang = detect(texto)
        return lang if lang in SAUDACOES else 'pt'
    except:
        return 'pt'

# Função principal de resposta
def responder(mensagem, historico):
    try:
        lang = detectar_idioma(mensagem.strip())

        # Se for uma saudação
        if mensagem.lower().strip() in ['oi', 'olá', 'ola', 'hi', 'hello', 'hola', 'salut', 'ciao']:
            import random
            resposta = random.choice(SAUDACOES.get(lang, SAUDACOES['pt']))
        else:
            prompt = f"Responda em {lang} para esta mensagem: {mensagem}"
            resultado = llm.invoke(prompt)
            resposta = resultado.content.strip() if resultado and resultado.content else "Desculpe, não consegui entender. Pode repetir?"

        novo_historico = historico + [
            {"role": "user", "content": mensagem},
            {"role": "assistant", "content": resposta}
        ]
        return "", novo_historico

    except Exception as e:
        print("Erro:", e)
        error_msg = {
            'pt': "⚠️ Ocorreu um erro, tente novamente.",
            'en': "⚠️ An error occurred, please try again.",
            'es': "⚠️ Ocurrió un error, intenta nuevamente.",
            'fr': "⚠️ Une erreur est survenue, veuillez réessayer.",
            'it': "⚠️ Si è verificato un errore, riprova."
        }.get(lang, "⚠️ An unexpected error occurred.")
        
        novo_historico = historico + [
            {"role": "user", "content": mensagem},
            {"role": "assistant", "content": error_msg}
        ]
        return "", novo_historico

# Interface com Gradio
with gr.Blocks(theme=gr.themes.Monochrome()) as app:
    gr.Markdown("#  📚 ChatBook")
    gr.Markdown("**Seu consultor literário inteligente, pronto para recomendar livros com base no seu gosto. 📚✨**")

    chatbot = gr.Chatbot(height=400, type="messages")

    with gr.Row():
        msg = gr.Textbox(
            label="Preferência do Cliente",
            placeholder="Ex: Gosto de thrillers psicológicos como os de Gillian Flynn.",
            container=False,
            scale=7
        )
        btn = gr.Button("Enviar", scale=1)

    btn.click(responder, [msg, chatbot], [msg, chatbot])
    msg.submit(responder, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)

