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

# Função para gerar respostas
def responder(materia, ano, pergunta):
    try:
        if detect(pergunta) != 'pt':
            return "Por favor, envie a pergunta em português."

        prompt = f"Você é um professor especialista em {materia} para o {ano} do ensino fundamental. " \
                 "Sua missão é explicar o conceito de maneira clara e simples, com exemplos práticos e apropriados para a idade. " \
                 "Nunca use jargões complicados e sempre considere o nível de compreensão dos alunos dessa série.\n\n" \
                 f"Aluno: {pergunta}\n" \
                 "Resposta do professor:"

        resposta = llm.invoke(prompt)
        return resposta.content

    except Exception as e:
        return f"Ocorreu um erro: {str(e)}"

# Interface com Gradio
with gr.Blocks(theme=gr.themes.Citrus()) as app:
    gr.Markdown("# 📚 Tutor Escolar 🧑‍🏫")
    gr.Markdown("**Seu assistente virtual para ajudar nas disciplinas do ensino fundamental!**")

    with gr.Row():
        # Coluna da esquerda (entrada)
        with gr.Column(scale=1):
            materia = gr.Dropdown(
                label="Matéria",
                choices=["Português", "Inglês", "Matemática", "Geografia", "História", "Ciências",
                         "Educação Física", "Artes", "Tecnologia", "Psicologia, Cidadania, Educação Financeira"],
                value="Português"
            )

            ano = gr.Dropdown(
                label="Ano/Série Escolar",
                choices=["1º Ano", "2º Ano", "3º Ano", "4º Ano", "5º Ano"],
                value="1º Ano"
            )

            pergunta = gr.Textbox(
                label="Pergunta",
                placeholder="Digite sua dúvida aqui...",
                lines=4
            )

            btn = gr.Button("Enviar")

        # Coluna da direita (resposta)
        with gr.Column(scale=1):
            resposta = gr.Textbox(
                label="Resposta do Tutor",
                placeholder="A resposta aparecerá aqui...",
                lines=12,
                interactive=False
            )

    # Clique do botão
    btn.click(fn=responder, inputs=[materia, ano, pergunta], outputs=resposta)

# Rodar o app
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
