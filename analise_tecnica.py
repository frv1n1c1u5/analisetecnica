import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Função para carregar e validar dados
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    required_columns = [
        'Assessor', 'Cliente', 'Receita no Mês', 'Receita Bovespa', 
        'Receita Futuros', 'Receita RF Bancários', 'Receita RF Privados', 
        'Receita RF Públicos', 'Captação Bruta em M', 'Resgate em M', 'Captação Líquida em M'
    ]
    if not all(col in df.columns for col in required_columns):
        st.error("A planilha deve conter as colunas necessárias.")
        return None
    return df

# Função para exibir ranking por receita
def display_ranking(df, filter_assessor, filter_produto):
    if filter_assessor:
        df = df[df['Assessor'] == filter_assessor]
    if filter_produto:
        df = df[['Assessor', filter_produto]].groupby('Assessor').sum()
    else:
        df = df.groupby('Assessor')['Receita no Mês'].sum()
    
    df = df.sort_values(ascending=False)
    df = df.apply(lambda x: f"R$ {x:,.2f}")  # Formatação de moeda
    st.write(df)
    return df

# Função para exportar o ranking como PDF
def export_to_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Ranking de Desempenho dos Assessores", ln=True, align='C')
    pdf.ln(10)
    
    for index, value in data.items():
        pdf.cell(200, 10, txt=f"{index}: {value}", ln=True)
    
    output_path = "/tmp/ranking.pdf"
    pdf.output(output_path)
    return output_path

# Interface principal do aplicativo
st.title("Ranking de Desempenho dos Assessores")
uploaded_file = st.file_uploader("Faça o upload da planilha", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        # Filtros na barra lateral
        st.sidebar.subheader("Filtros")
        filter_assessor = st.sidebar.selectbox("Selecione o Assessor", options=[None] + list(df['Assessor'].unique()))
        filter_produto = st.sidebar.selectbox("Selecione o Tipo de Produto", options=[None, 'Receita Bovespa', 'Receita Futuros', 'Receita RF Bancários', 'Receita RF Privados', 'Receita RF Públicos'])

        # Mostrar ranking e gráfico em abas
        tab1, tab2 = st.tabs(["Tabela de Ranking", "Gráfico de Desempenho"])
        
        with tab1:
            st.subheader("Ranking por Receita")
            ranking_data = display_ranking(df, filter_assessor, filter_produto)

            if st.button("Exportar Ranking para PDF"):
                pdf_path = export_to_pdf(ranking_data)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(label="Baixar PDF", data=pdf_file, file_name="ranking.pdf", mime="application/pdf")
        
        with tab2:
            st.subheader("Gráfico de Desempenho")
            if filter_produto:
                fig = px.bar(df, x=df.index, y=filter_produto, labels={'y': filter_produto})
            else:
                fig = px.bar(df, x=df.index, y='Receita no Mês', labels={'y': 'Receita no Mês'})
            fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')
            st.plotly_chart(fig)
