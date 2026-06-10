import pdfplumber
import re
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

def extrair_dados_siclom(pdf_file):
    registros = []
    re_data = re.compile(r"Data:\s+(\d{2}/\d{2}/\d{4})")
    re_dias = re.compile(r"Dias Trat\.:\s+(\d+)")
    re_peso = re.compile(r"Peso:\s+([^\n\r]+)")

    with pdfplumber.open(pdf_file) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if not texto:
                continue

            blocos = re.split(r"(?=(?:Data:\s+\d{2}/\d{2}/\d{4}))", texto)

            for bloco in blocos:
                data_match = re_data.search(bloco)
                dias_match = re_dias.search(bloco)
                peso_match = re_peso.search(bloco)

                if data_match and dias_match:
                    data_retirada = datetime.strptime(data_match.group(1), "%d/%m/%Y")
                    dias_trat = int(dias_match.group(1))
                    peso = peso_match.group(1).strip() if peso_match else "N/A"

                    registros.append({
                        "data": data_retirada,
                        "dias_recebidos": dias_trat,
                        "peso": peso
                    })

    registros.sort(key=lambda x: x["data"])
    return registros

def analisar_gaps(registros):
    analise = []
    estoque_atual = 0
    data_fim_estoque = None
    sobra_na_retirada_anterior = 0
    dias_recebidos_anterior = 0

    for i in range(len(registros)):
        reg = registros[i]
        data_atual = reg["data"]

        if data_fim_estoque:
            sobra = (data_fim_estoque - data_atual).days
            if sobra < 0:
                inicio_gap = data_fim_estoque
                fim_gap = data_atual
                dias_sem = abs(sobra)

                if dias_sem > 10:
                    analise.append({
                        "Inicio":   inicio_gap.strftime("%d/%m/%Y"),
                        "Fim":      fim_gap.strftime("%d/%m/%Y"),
                        "Dias":     dias_sem,
                        "Retirada": data_anterior,
                        "Qtd":      dias_recebidos_anterior,
                        "Reserva":  sobra_na_retirada_anterior,
                    })
                estoque_atual = reg["dias_recebidos"]
                sobra_na_retirada_anterior = 0
            else:
                estoque_atual = sobra + reg["dias_recebidos"]
                sobra_na_retirada_anterior = sobra
        else:
            estoque_atual = reg["dias_recebidos"]
            sobra_na_retirada_anterior = 0

        dias_recebidos_anterior = reg["dias_recebidos"]
        data_anterior = data_atual.strftime("%d/%m/%Y")
        data_fim_estoque = data_atual + timedelta(days=estoque_atual)

    hoje = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    if data_fim_estoque and data_fim_estoque < hoje:
        dias_sem = (hoje - data_fim_estoque).days
        if dias_sem > 10:
            analise.append({
                "Inicio":   data_fim_estoque.strftime("%d/%m/%Y"),
                "Fim":      hoje.strftime("%d/%m/%Y"),
                "Dias":     dias_sem,
                "Retirada": data_anterior,
                "Qtd":      dias_recebidos_anterior,
                "Reserva":  sobra_na_retirada_anterior,
            })

    return pd.DataFrame(analise)

# --- Streamlit UI ---
st.markdown("""<style>div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button { background-color: #2a9d8f !important; border-color: #2a9d8f !important; color: white !important; } div[data-testid="stButton"] button:hover, div[data-testid="stDownloadButton"] button:hover { background-color: #21867a !important; border-color: #21867a !important; }</style>""", unsafe_allow_html=True)
st.title("Análise de Gaps - Histórico Terapêutico")

uploaded_file = st.file_uploader("Selecione o PDF do histórico terapêutico", type="pdf")

if uploaded_file is not None:
    dados = extrair_dados_siclom(uploaded_file)
    df_gaps = analisar_gaps(dados)

    if df_gaps.empty:
        st.info("Nenhum gap maior que 10 dias encontrado.")
    else:
        st.write(f"**{len(df_gaps)} interrupções encontradas**")
        df_gaps.index = range(1, len(df_gaps) + 1)
        df_display = df_gaps.iloc[::-1]
        styled = df_display.style.map(
            lambda _: "text-align: center",
            subset=["Dias", "Qtd", "Reserva"]
        )
        st.dataframe(styled, use_container_width=True)
