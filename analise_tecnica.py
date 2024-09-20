import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import ta

@st.cache_data
def carregar_dados(ativo, periodo):
    data = yf.download(ativo, period=periodo, interval="1d", progress=False)
    return data[data['Volume'] > 0].dropna()

def plotar_candle_com_indicadores(data, indicadores_selecionados):
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, subplot_titles=('Preço e Indicadores',))

    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Candlestick'))

    if "Média Móvel" in indicadores_selecionados:
        data['SMA'] = ta.trend.SMAIndicator(data['Close'], window=14).sma_indicator()
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], mode='lines', name='Média Móvel', line=dict(color='blue')))
    
    if "RSI" in indicadores_selecionados:
        data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', yaxis="y2", line=dict(color='green')))

    if "MACD" in indicadores_selecionados:
        macd = ta.trend.MACD(data['Close'])
        data['MACD'] = macd.macd()
        data['Signal'] = macd.macd_signal()
        fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', yaxis="y3", line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=data.index, y=data['Signal'], mode='lines', name='Signal MACD', yaxis="y3", line=dict(color='purple')))

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
        yaxis_title='Preço',
        xaxis_title='Data',
        height=600,
        yaxis2=dict(title='RSI', overlaying='y', side='right', showgrid=False),
        yaxis3=dict(title='MACD', overlaying='y', side='right', showgrid=False),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_xaxes(rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

st.title("Análise Técnica de Ativos - B3")

codigo_ativo = st.text_input("Digite o código do ativo (ex: PETR4.SA)")
periodo = st.selectbox("Período", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])

if codigo_ativo:
    st.write(f"Carregando dados para {codigo_ativo}...")
    dados = carregar_dados(codigo_ativo, periodo)

    if not dados.empty:
        indicadores = st.multiselect("Selecione os indicadores técnicos", ["Média Móvel", "RSI", "MACD", "Bandas de Bollinger"])
        plotar_candle_com_indicadores(dados, indicadores)
    else:
        st.error("Não foi possível obter dados para o ativo especificado. Verifique se o código está correto.")
else:
    st.write("Digite o código de um ativo para começar.")

if st.button("Limpar Cache"):
    st.cache_data.clear()
    st.success("Cache limpo com sucesso.")
