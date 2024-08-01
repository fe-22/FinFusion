import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import yfinance as yf

# Conectar ao banco de dados
conn = sqlite3.connect('finfusion.db')
c = conn.cursor()

# Função para recuperar dados financeiros de um usuário
def get_financial_data(username):
    c.execute("SELECT date, description, amount, type FROM financial_data WHERE username=?", (username,))
    return c.fetchall()

# Função para formatar números em moeda
def format_currency(value):
    return f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Interface do Streamlit
st.title('FinFusion - Financial Charts')

# Verificar se o usuário está logado
if 'username' in st.session_state:
    username = st.session_state['username']

    # Recuperar dados financeiros
    financial_data = get_financial_data(username)
    if financial_data:
        df = pd.DataFrame(financial_data, columns=['date', 'description', 'amount', 'type'])
        df['date'] = pd.to_datetime(df['date'])

        # Gráfico de barras de renda e despesas por mês
        df['month'] = df['date'].dt.to_period('M')
        monthly_summary = df.groupby(['month', 'type'])['amount'].sum().unstack().fillna(0)

        st.subheader('Gráfico de Renda e Despesas por Mês')
        fig, ax = plt.subplots()
        monthly_summary.plot(kind='bar', ax=ax)
        ax.set_xlabel('Mês')
        ax.set_ylabel('Quantia')
        ax.set_title('Renda e Despesas por Mês')
        st.pyplot(fig)

        # Gráfico de linha de saldo líquido ao longo do tempo
        df['net_balance'] = df['amount'].cumsum()
        st.subheader('Gráfico de Saldo Líquido ao Longo do Tempo')
        fig, ax = plt.subplots()
        df.plot(x='date', y='net_balance', kind='line', ax=ax)
        ax.set_xlabel('Data')
        ax.set_ylabel('Saldo Líquido')
        ax.set_title('Saldo Líquido ao Longo do Tempo')
        st.pyplot(fig)

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

        # Botão para retornar à página principal
        if st.button('Voltar para a página principal'):
            st.session_state['page'] = 'main'

else:
    st.warning('Por favor, faça o login para visualizar os gráficos.')

# Rodapé
st.markdown("""
<footer style='text-align: center;'>
    <p>&copy; 2024 FinFusion. Todos os direitos reservados. Desenvolvido por fthec</p>
    <p><a href="https://github.com/fe-22/FinFusion" style="color: blue; text-decoration: none;">
    <pre>Ajude o Dev a continuar melhorando sua vida. Pix 11982170425</pre></a></p>
</footer>
""", unsafe_allow_html=True)
