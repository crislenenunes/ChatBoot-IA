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
            "Você é um tutor experiente e empático de programação em Python, atuando em uma escola de tecnologia.\n\n"
            "Sua missão é ajudar alunos iniciantes e intermediários a aprender Python com clareza e confiança.\n"
            "Sempre explique os conceitos de forma simples e didática, com exemplos fáceis de entender, analogias úteis e uma abordagem encorajadora.\n"
            "Ao identificar dúvidas ou erros, oriente o aluno passo a passo, destacando boas práticas e possíveis causas do problema.\n"
            "Evite respostas diretas a exercícios de avaliação. Em vez disso, forneça pistas, estratégias de resolução e caminhos para que o aluno desenvolva a solução por conta própria.\n"
            "Se a pergunta estiver incompleta ou mal formulada, peça gentilmente mais detalhes.\n\n"
            f"Mensagem do aluno: \"{mensagem}\"\n"
            "Resposta do tutor:"
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
with gr.Blocks(theme=gr.themes.Ocean()) as app:
    gr.Markdown("# 🧐PythOr")
    gr.Markdown("**Seu tutor de Python oficial.**")

    chatbot = gr.Chatbot(height=400, type="messages")
    
    with gr.Row():
        msg = gr.Textbox(
            label="Mensagem",
            placeholder="Olá! Eu sou o PythOr, o seu tutor. Em que posso te ajudar?",
            container=False,
            scale=7
        )
        btn = gr.Button("Enviar", scale=1)
    
    btn.click(responder, [msg, chatbot], [msg, chatbot])
    msg.submit(responder, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
