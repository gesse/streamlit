import pytz
import datetime
import streamlit as st
import pandas as pd
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph
import reportlab.platypus as rlplt
from reportlab.lib.units import mm
from io import BytesIO
import base64

from openai import OpenAI

fuso_horario_desejado = 'America/Sao_Paulo'
custo_input_per_token = 0.0010 / 1000
custo_output_per_token = 0.0020 / 1000

# armazenando o total de tokens utilizado no chat
contador_tokens = {
    'prompt_tokens': 0,
    'completion_tokens': 0
}
# Obtendo a chave da openai
chave = st.sidebar.text_input('Chave da API OpenAI', type = 'password')
client = OpenAI(api_key=chave)

st.title('Assistente pessoal')

# input para a criatividade das respostas
opcao_criatividade = st.sidebar.slider(
    label="Grau de criatividade da resposta",
    min_value=0.0,
    max_value=2.0,
    step=0.01
)

def traduzir_tamanho_resposta(tamanho: int) -> str:
    if tamanho == 300:
        return "pequeno"
    elif tamanho == 600:
        return "médio"
    elif tamanho == 900:
        return "grande"
    else:
        return 0

opcao_tamanho_resposta = st.sidebar.select_slider(
    label="Tamanho da resposta (tokens)",
    options=[300,600,900],
    format_func=traduzir_tamanho_resposta
)

opcao_estilo_resposta = st.sidebar.selectbox(
    label="Estilo da resposta",
    options=["expositivo", "rebuscado", "expositivo","narrativo", "criativo", "objetivo", "pragmático", "sistemático", "debochado","soteropolitano"]
)
    
def finalizar_conversa():
    
    data_hora_atual = datetime.datetime.now(pytz.timezone(fuso_horario_desejado))
    # Criar estrutura dos dados a serem apresentados no dataframe
    dados = {
        'data_hora': [data_hora_atual],
        'qtde_tokens': [contador_tokens['prompt_tokens'] + contador_tokens['completion_tokens']],
        'custo': [(contador_tokens['prompt_tokens'] * custo_input_per_token) + (contador_tokens['completion_tokens'] * custo_output_per_token)],
        'histórico': [st.session_state.mensagens]
    }

    # Criar DataFrame
    df = pd.DataFrame(dados)
    st.dataframe(df)

    pdf_buffer = criar_pdf(st.session_state.mensagens)

    # Cria um link para download do PDF
    st.markdown(download_arquivo(pdf_buffer, 'hist_conversa.pdf', 'Download Histórico da Conversa'), unsafe_allow_html=True)

    
btn_finalizar_conversa = st.sidebar.button(
    label="Finalizar conversa",
    on_click=finalizar_conversa
)

# Função para ler o conteúdo de um arquivo de texto (.txt)
def ler_arquivo_texto(arquivo_txt):
    with open(arquivo_txt, 'r', encoding='utf-8') as arquivo:
        conteudo = arquivo.read()
    return conteudo
    
if not btn_finalizar_conversa:

    # Área para fazer upload do arquivo PDF
    arquivo_txt = st.file_uploader("Faça o upload do arquivo text:", type=["txt"])

    if arquivo_txt: 
        # inicializando a variável
        txt_conteudo = ""
        # Ler o conteúdo do arquivo de texto se um arquivo foi carregado
        txt_conteudo = arquivo_txt.getvalue().decode("utf-8")

        contexto = f'''
                Você é um assistente pessoal com objetivo de responder as 
                perguntas do usuário com um estilo de escrita {opcao_estilo_resposta}. 
                Limite o tamanho da resposta para {opcao_tamanho_resposta} palavras no máximo.
                '''
        if txt_conteudo and len(txt_conteudo) > 0:
            contexto += "Para responder as interações do usuário, considere o seguinte conteúdo: \n\n\n\n"
            contexto += f" {txt_conteudo}\n"

        # criando e inicializando o histório do chat
        if "mensagens" not in st.session_state:
            st.session_state.mensagens = [{
                "role": 'system', 
                "content": contexto}]


        # Aparecer o Historico do Chat na tela
        for mensagens in st.session_state.mensagens[1:]:
            with st.chat_message(mensagens["role"]):
                st.markdown(mensagens["content"])

        # React to user input
        prompt = st.chat_input("Digite alguma coisa")
        if prompt:
            with st.chat_message("user"):
                st.markdown(prompt)

            # TODO: incluir código da moderação do prompt
            response_moderation = client.moderations.create(input=prompt)

            df = pd.DataFrame(dict(response_moderation.results[0].category_scores).items(), columns=['Category', 'Value'])
            df.sort_values(by = 'Value', ascending = False, inplace=True)

            if (df.iloc[0,1] > 0.01):
                with st.chat_message("system"):
                    st.markdown("Acho que o que você falou se enquadra em algumas categorias que eu não posso falar sobre:")
                    for category in df.head(5)['Category']:
                        st.markdown(f'{category}')
                    st.markdown("Que tal falarmos sobre outra coisa?")
            else:
                # Display user message in chat message container
                
                # Add user message to chat history
                st.session_state.mensagens.append({"role": "user", "content": prompt})

                chamada = client.chat.completions.create(
                    model = 'gpt-3.5-turbo',
                    temperature = opcao_criatividade,
                    messages = st.session_state.mensagens
                )

                contador_tokens['prompt_tokens'] += chamada.usage.prompt_tokens
                contador_tokens['completion_tokens'] += chamada.usage.completion_tokens

                resposta = chamada.choices[0].message.content

                # Mostrar resposta do assistente no container do chat
                with st.chat_message("system"):
                    st.markdown(resposta)

                # Adiciona a resposta do assistente ao histórico do chat
                st.session_state.mensagens.append({"role": "system", "content": resposta})



def criar_pdf(mensagens_chat):
    buffer = BytesIO()

    # Estilos para negrito e itálico
    estilos = getSampleStyleSheet()
    estilo_negrito = estilos['BodyText']
    estilo_negrito.fontName = 'Helvetica-Bold'
    estilo_italico = estilos['BodyText']
    estilo_italico.fontName = 'Helvetica-Oblique'

    left_margin = 5 * mm
    right_margin = 5 * mm
    top_margin = 5 * mm
    bottom_margin = 5 * mm

    doc = SimpleDocTemplate(buffer, pagesize=(landscape(A4)),
                        leftMargin=left_margin, rightMargin=right_margin,
                        topMargin=top_margin, bottomMargin=bottom_margin)

    # Criar a tabela
    tabela_dados = []

    for msg in mensagens_chat:

        usuario = msg.get('role', '')
        mensagem = msg.get('content', '')

        linha_tabela = [Paragraph(usuario), Paragraph(mensagem)]
        tabela_dados.append(linha_tabela)
    
    # Crie a tabela com os dados
    tabela = rlplt.Table(tabela_dados, colWidths=(15*mm, 40*mm), splitInRow=1)

    # Estilo da tabela
    estilo_tabela = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ])

    # Criar a instância da tabela
    tabela = Table(tabela_dados)

    # Aplicar o estilo à tabela
    tabela.setStyle(estilo_tabela)

    doc.build([tabela])

    # Move o ponteiro de leitura/escrita para o início do buffer
    buffer.seek(0)

    return buffer

def download_arquivo(bin_file, file_label='File', button_label='Download'):
    with bin_file as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_label}.pdf">{button_label}</a>'
    return href