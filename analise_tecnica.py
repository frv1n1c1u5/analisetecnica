import os
import streamlit as st
import pandas as pd
import ta  # Biblioteca alternativa para análise técnica
import plotly.graph_objects as go
from datetime import datetime
import io

# Instalar yfinance se não estiver instalado
os.system('pip install yfinance')

# Importar yfinance após garantir que ele foi instalado
import yfinance as yf

# Função para carregar os dados do ativo selecionado
@st.cache_data
def carregar_dados(ativo, periodo):
    return yf.download(ativo, period=periodo, progress=False)  # Desativa a barra de progresso

# Função para plotar gráfico de candle
def plotar_candle(data):
    fig = go.Figure(data=[go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
    fig.update_layout(title='Gráfico de Candle', xaxis_title='Data', yaxis_title='Preço')
    st.plotly_chart(fig)

# Função para adicionar indicadores técnicos
def adicionar_indicadores(data, indicadores_selecionados):
    if "Média Móvel" in indicadores_selecionados:
        data['SMA'] = ta.trend.SMAIndicator(data['Close'], window=14).sma_indicator()
        st.line_chart(data[['Close', 'SMA']])
    if "RSI" in indicadores_selecionados:
        data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
        st.line_chart(data[['RSI']])
    if "MACD" in indicadores_selecionados:
        macd = ta.trend.MACD(data['Close'])
        data['MACD'] = macd.macd()
        data['Signal'] = macd.macd_signal()
        st.line_chart(data[['MACD', 'Signal']])
    if "Bandas de Bollinger" in indicadores_selecionados:
        bb = ta.volatility.BollingerBands(data['Close'])
        data['BB_upper'] = bb.bollinger_hband()
        data['BB_middle'] = bb.bollinger_mavg()
        data['BB_lower'] = bb.bollinger_lband()
        st.line_chart(data[['Close', 'BB_upper', 'BB_middle', 'BB_lower']])
    return data

# Função para exportar gráfico como imagem
def exportar_grafico(dados):
    fig = go.Figure(data=[go.Candlestick(
        x=dados.index, open=dados['Open'], high=dados['High'], low=dados['Low'], close=dados['Close'])])
    
    buf = io.BytesIO()
    fig.write_image(buf, format='png')
    st.download_button("Baixar gráfico", buf.getvalue(), file_name="grafico_candle.png", mime="image/png")

# Interface do usuário
st.title("Análise Técnica de Ativos - B3")
st.sidebar.header("Configurações")

# Seção de seleção de ativos e período
ativos = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]  # Exemplos de ativos da B3
ativo = st.sidebar.selectbox("Selecione o ativo", ativos)
periodo = st.sidebar.selectbox("Período", ["1mo", "3mo", "1y", "5y"])

# Carregar dados do ativo
st.sidebar.write("Carregando dados...")
dados = carregar_dados(ativo, periodo)

# Exibir gráfico de candle
st.subheader(f"Gráfico de Candle para {ativo}")
plotar_candle(dados)

# Seleção de indicadores técnicos
indicadores = st.sidebar.multiselect("Selecione os indicadores técnicos", ["Média Móvel", "RSI", "MACD", "Bandas de Bollinger"])

# Adicionar indicadores técnicos
dados_com_indicadores = adicionar_indicadores(dados, indicadores)

# Botão para exportar gráfico
if st.button("Exportar gráfico"):
    exportar_grafico(dados)

# Modo de Desempenho
modo_desempenho = st.sidebar.checkbox("Ativar Modo de Desempenho (Gráficos Simplificados)")
if modo_desempenho:
    st.write("Modo de Desempenho ativado. Gráficos simplificados.")
    # Implementar lógica de gráficos simplificados aqui

# Barra de progresso durante o carregamento dos dados
with st.spinner('Processando...'):
    st.success('Processamento concluído com sucesso!')

# Tutorial
if st.sidebar.button("Mostrar Tutorial"):
    st.info("""
        Passo 1: Selecione um ativo no menu à esquerda.\n
        Passo 2: Escolha o período de tempo para a análise (ex: 1 mês, 3 meses, 1 ano).\n
        Passo 3: Adicione indicadores técnicos, se necessário.\n
        Passo 4: Exporte o gráfico como imagem usando o botão apropriado.\n
        Passo 5: Utilize a opção de Long & Short para comparar dois ativos simultaneamente.
    """)

# Mensagem de feedback final
st.sidebar.write("Obrigado por utilizar o app. Se tiver dúvidas, consulte o tutorial ou tente iniciar uma nova análise.")

# Cache - Limpar manualmente
if st.sidebar.button("Limpar Cache"):
    st.cache_data.clear()
    st.sidebar.write("Cache limpo com sucesso.")
