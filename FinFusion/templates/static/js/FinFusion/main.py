import streamlit as st
import pandas as pd
import yfinance as yf

# Define o título do aplicativo
st.title("App de Ações - Itaú, Bitcoin e Etherium")

# Carrega os dados das ações do Itaú
itaú = yf.Ticker("ITUB4.SA")

# Obtém os dados históricos dos preços
itaú_hist = itaú.history(period="1y")

# Carrega os dados do Bitcoin
bitcoin = yf.Ticker("BTC-USD")

# Obtém os dados históricos dos preços
bitcoin_hist = bitcoin.history(period="1y")

# Carrega os dados do Etherium
etherium = yf.Ticker("ETH-USD")

# Obtém os dados históricos dos preços
etherium_hist = etherium.history(period="1y")

ibovespa = yf.Ticker("^BVSP")
ibovespa_hist = ibovespa.history(period="1y")

# Cria um gráfico de linha com os preços do Itaú
st.subheader("Evolução dos Preços das Ações do Itaú")
st.line_chart(itaú_hist["Close"])
st.write("O gráfico acima representa a evolução dos preços das ações do Itaú nos últimos 12 meses.")

# Cria um gráfico de linha com os preços do Bitcoin
st.subheader("Evolução dos Preços do Bitcoin")
st.line_chart(bitcoin_hist["Close"])
st.write("O gráfico acima representa a evolução dos preços do Bitcoin nos últimos 12 meses.")

# Cria um gráfico de linha com os preços do Etherium
st.subheader("Evolução dos Preços do Etherium")
st.line_chart(etherium_hist["Close"])
st.write("O gráfico acima representa a evolução dos preços do Etherium nos últimos 12 meses.")

st.subheader("Evolução do IBOVESPA")
st.line_chart(ibovespa_hist["Close"])
st.write("O gráfico acima representa a evolução do IBOVESPA nos últimos 12 meses.")