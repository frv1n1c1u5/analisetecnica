import os
import streamlit as st
import pandas as pd
import numpy as np
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import requests

# Instalar bibliotecas necessárias
os.system('pip install yfinance pandas numpy scikit-learn requests')

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

def obter_dados_fundamentalistas(ativo):
    ticker = yf.Ticker(ativo)
    info = ticker.info
    return {
        "P/L": info.get('trailingPE', 'N/A'),
        "Dividend Yield": info.get('dividendYield', 'N/A'),
        "Valor de Mercado": info.get('marketCap', 'N/A'),
        "Receita": info.get('totalRevenue', 'N/A'),
        "Lucro Líquido": info.get('netIncomeToCommon', 'N/A'),
    }

def realizar_previsao(data):
    df = data.copy()
    df['Predict'] = df['Close'].shift(-1)
    df = df.dropna()
    X = np.array(df.index.astype(int).values).reshape(-1, 1)
    y = np.array(df['Predict'])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    last_date = df.index[-1]
    next_date = last_date + timedelta(days=1)
    next_date_int = int(next_date.timestamp())
    predicted_price = model.predict([[next_date_int]])[0]
    
    return predicted_price, model.score(X_test, y_test)

def exportar_dados(data):
    csv = data.to_csv().encode('utf-8')
    st.download_button(
        label="Baixar dados como CSV",
        data=csv,
        file_name="dados_ativo.csv",
        mime="text/csv",
    )

def obter_noticias(ativo):
    # Substitua 'SUA_CHAVE_API' pela sua chave real da API de notícias
    url = f"https://newsapi.org/v2/everything?q={ativo}&apiKey=SUA_CHAVE_API"
    response = requests.get(url)
    if response.status_code == 200:
        news = response.json()['articles'][:5]  # Pegando as 5 primeiras notícias
        return news
    else:
        return None

st.title("Análise Técnica e Fundamental de Ativos - B3")
st.sidebar.header("Configurações")

codigo_ativo = st.sidebar.text_input("Digite o código do ativo (ex: PETR4.SA)")
periodo = st.sidebar.selectbox("Período", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])

if codigo_ativo:
    st.sidebar.write(f"Carregando dados para {codigo_ativo}...")
    dados = carregar_dados(codigo_ativo, periodo)

    indicadores = st.sidebar.multiselect("Selecione os indicadores técnicos", ["Média Móvel", "RSI", "MACD", "Bandas de Bollinger"])

    st.subheader(f"Gráfico de Candle com Indicadores para {codigo_ativo}")
    plotar_candle_com_indicadores(dados, indicadores)

    # Análise Fundamentalista
    st.subheader("Dados Fundamentalistas")
    dados_fundamentalistas = obter_dados_fundamentalistas(codigo_ativo)
    st.write(dados_fundamentalistas)

    # Previsões
    st.subheader("Previsão de Preço")
    preco_previsto, score = realizar_previsao(dados)
    st.write(f"Preço previsto para o próximo dia: R$ {preco_previsto:.2f}")
    st.write(f"Precisão do modelo: {score:.2%}")

    # Exportação de dados
    st.subheader("Exportar Dados")
    exportar_dados(dados)

    # Notícias
    st.subheader("Notícias Relacionadas")
    noticias = obter_noticias(codigo_ativo)
    if noticias:
        for noticia in noticias:
            st.write(f"**{noticia['title']}**")
            st.write(noticia['description'])
            st.write(f"[Leia mais]({noticia['url']})")
            st.write("---")
    else:
        st.write("Não foi possível carregar as notícias no momento.")

else:
    st.sidebar.write("Digite o código de um ativo para começar.")

if st.sidebar.button("Limpar Cache"):
    st.cache_data.clear()
    st.sidebar.write("Cache limpo com sucesso.")
