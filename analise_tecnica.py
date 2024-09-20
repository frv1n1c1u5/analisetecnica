import os
import streamlit as st
import pandas as pd
import ta  # Biblioteca alternativa para análise técnica
import plotly.graph_objects as go
import io

# Instalar yfinance se não estiver instalado
os.system('pip install yfinance')

# Importar yfinance após garantir que ele foi instalado
import yfinance as yf

# Função para carregar os dados do ativo selecionado e remover dias sem pregão
@st.cache_data
def carregar_dados(ativo, periodo):
    # Baixar dados do yfinance
    data = yf.download(ativo, period=periodo, interval="1d", progress=False)
    
    # Remover dias sem pregão (linhas onde 'Volume' é 0, indicando ausência de negociações)
    data = data[data['Volume'] > 0]
    
    return data

# Função para plotar gráfico de candle com todos os indicadores sobrepostos
def plotar_candle_com_indicadores(data, indicadores_selecionados):
    fig = go.Figure()

    # Gráfico de candle
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Candlestick'))

    # Adiciona os indicadores selecionados sobre o gráfico de candle
    if "Média Móvel" in indicadores_selecionados:
        data['SMA'] = ta.trend.SMAIndicator(data['Close'], window=14).sma_indicator()
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], mode='lines', name='Média Móvel', line=dict(color='blue')))
    
    if "RSI" in indicadores_selecionados:
        data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
        # O RSI é plotado em outro eixo, mas sobreposto
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', yaxis="y2", line=dict(color='green')))

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

    # Atualiza layout para permitir o uso de eixos duplos (exemplo com RSI)
    fig.update_layout(
        title='Gráfico de Candle com Indicadores',
        yaxis_title='Preço',
        xaxis_title='Data',
        yaxis2=dict(title='RSI', overlaying='y', side='right', range=[0, 100], showgrid=False),
        xaxis_rangeslider_visible=False  # Desativa o range slider
    )

    st.plotly_chart(fig)

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
ativos = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "USIM5.SA", "CSNA3.SA", "EMBR3.SA", "BRKM5.SA"]  # Adiciona mais empresas da B3
ativo = st.sidebar.selectbox("Selecione o ativo", ativos)
periodo = st.sidebar.selectbox("Período", ["1d", "1mo", "3mo", "1y", "5y"])

# Carregar dados do ativo
st.sidebar.write("Carregando dados...")
dados = carregar_dados(ativo, periodo)

# Seleção de indicadores técnicos
indicadores = st.sidebar.multiselect("Selecione os indicadores técnicos", ["Média Móvel", "RSI", "MACD", "Bandas de Bollinger"])

# Exibir gráfico de candle com indicadores sobrepostos
st.subheader(f"Gráfico de Candle com Indicadores para {ativo}")
plotar_candle_com_indicadores(dados, indicadores)

# Botão para exportar gráfico
if st.button("Exportar gráfico"):
    exportar_grafico(dados)

# Cache - Limpar manualmente
if st.sidebar.button("Limpar Cache"):
    st.cache_data.clear()
    st.sidebar.write("Cache limpo com sucesso.")
