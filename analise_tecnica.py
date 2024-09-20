import os
import streamlit as st
import pandas as pd
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# Instalar yfinance se não estiver instalado
os.system('pip install yfinance')

# Importar yfinance após garantir que ele foi instalado
import yfinance as yf

@st.cache_data
def carregar_dados(ativo, periodo):
    data = yf.download(ativo, period=periodo, interval="1d", progress=False)
    data = data[data['Volume'] > 0].dropna()
    return data

def plotar_candle_com_indicadores(data, indicadores_selecionados):
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.03, subplot_titles=('Preço e Indicadores',))

    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Candlestick'))

    if "Média Móvel" in indicadores_selecionados:
        data['SMA'] = ta.trend.SMAIndicator(data['Close'], window=14).sma_indicator()
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], mode='lines', name='Média Móvel', line=dict(color='blue')))
    
    if "RSI" in indicadores_selecionados:
        data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='green')))

    if "MACD" in indicadores_selecionados:
        macd = ta.trend.MACD(data['Close'])
        data['MACD'] = macd.macd()
        data['Signal'] = macd.macd_signal()
        fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=data.index, y=data['Signal'], mode='lines', name='Signal MACD', line=dict(color='purple')))

    if "Bandas de Bollinger" in indicadores_selecionados:
        bb = ta.volatility.BollingerBands(data['Close'])
        data['BB_upper'] = bb.bollinger_hband()
        data['BB_middle'] = bb.bollinger_mavg()
        data['BB_lower'] = bb.bollinger_lband()
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_upper'], mode='lines', name='Banda Superior', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_middle'], mode='lines', name='Banda Média', line=dict(color='yellow')))
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_lower'], mode='lines', name='Banda Inferior', line=dict(color='red')))

    fig.update_layout(
        title='Gráfico de Candle com Indicadores',
        yaxis_title='Preço / Valor do Indicador',
        xaxis_title='Data',
        height=600,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_xaxes(rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

def exportar_grafico(dados):
    fig = go.Figure(data=[go.Candlestick(
        x=dados.index, open=dados['Open'], high=dados['High'], low=dados['Low'], close=dados['Close'])])
    
    buf = io.BytesIO()
    fig.write_image(buf, format='png')
    st.download_button("Baixar gráfico", buf.getvalue(), file_name="grafico_candle.png", mime="image/png")

st.title("Análise Técnica de Ativos - B3")
st.sidebar.header("Configurações")

# Entrada de código de ativo
codigo_ativo = st.sidebar.text_input("Digite o código do ativo (ex: PETR4.SA)")

# Seção de seleção de período
periodo = st.sidebar.selectbox("Período", ["1d", "1mo", "3mo", "1y", "5y"])

if codigo_ativo:
    st.sidebar.write(f"Carregando dados para {codigo_ativo}...")
    dados = carregar_dados(codigo_ativo, periodo)

    indicadores = st.sidebar.multiselect("Selecione os indicadores técnicos", ["Média Móvel", "RSI", "MACD", "Bandas de Bollinger"])

    st.subheader(f"Gráfico de Candle com Indicadores para {codigo_ativo}")
    plotar_candle_com_indicadores(dados, indicadores)

    if st.button("Exportar gráfico"):
        exportar_grafico(dados)
else:
    st.sidebar.write("Digite o código de um ativo para começar.")

if st.sidebar.button("Limpar Cache"):
    st.cache_data.clear()
    st.sidebar.write("Cache limpo com sucesso.")
