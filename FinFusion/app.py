import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

# Demais funções existentes...

# Função para a página de dados financeiros e gráficos
def financial_data_page(username):
    # Inserir CSS para fundo preto
    st.markdown(
        """
        <style>
        body {
            background-color: #121212;
            color: white;
        }
        .css-1v3fvcr {
            background-color: #121212;
        }
        .stButton>button {
            color: white;
            background-color: #333333;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.title('Dados Financeiros e Gráficos')

    # Recuperar dados financeiros do usuário
    financial_data = get_financial_data(username)
    if financial_data is None:
        st.error('Erro ao recuperar os dados financeiros.')
        return

    # Exibir tabela de dados financeiros
    st.subheader('Dados Financeiros')
    if financial_data:
        df = pd.DataFrame(financial_data, columns=['id', 'Data', 'Descrição', 'Quantia', 'Tipo', 'Método de Pagamento', 'Parcelas', 'Necessidade'])
        st.table(df.drop(columns=['id']))  # Exibir tabela sem a coluna 'id'

    # Gráfico de receitas e despesas
    st.subheader('Gráfico de Receitas e Despesas')
    df['Data'] = pd.to_datetime(df['Data'])
    df.set_index('Data', inplace=True)
    df.groupby('Tipo')['Quantia'].plot(legend=True)
    plt.title('Receitas e Despesas ao Longo do Tempo')
    plt.grid(color='gray', linestyle='--', linewidth=0.5)
    st.pyplot(plt)

    # Alertar para os maiores gastos
    st.subheader('Alertas de Maiores Gastos')
    highest_expense = df[df['Tipo'] == 'Despesa'].sort_values(by='Quantia', ascending=False).head(1)
    if not highest_expense.empty:
        st.warning(f"O maior gasto foi com {highest_expense['Descrição'].values[0]} no valor de {format_currency(highest_expense['Quantia'].values[0])}")

    # Gráfico de tipos de despesas
    st.subheader('Gráfico de Tipos de Despesas')
    expense_df = df[df['Tipo'] == 'Despesa']
    expense_df.groupby('Descrição')['Quantia'].sum().plot(kind='bar')
    plt.title('Despesas por Categoria')
    plt.grid(color='gray', linestyle='--', linewidth=0.5)
    st.pyplot(plt)

    # Gráficos de Bitcoin, Ethereum, IBOVESPA e NASDAQ
    st.subheader('Evolução do Bitcoin, Ethereum, IBOVESPA e NASDAQ')
    
    # Define as datas para os últimos 6 meses
    end_date = datetime.today()
    start_date = end_date - timedelta(days=180)
    
    # Recupera dados do Yahoo Finance
    symbols = {'Bitcoin': 'BTC-USD', 'Ethereum': 'ETH-USD', 'IBOVESPA': '^BVSP', 'NASDAQ': '^IXIC'}
    data = {}
    
    for name, symbol in symbols.items():
        data[name] = yf.download(symbol, start=start_date, end=end_date)
    
    # Plota os dados individualmente
    for name, df in data.items():
        plt.figure()
        df['Close'].plot(title=f'Evolução do {name}')
        plt.xlabel('Data')
        plt.ylabel('Preço de Fechamento')
        plt.grid(color='gray', linestyle='--', linewidth=0.5)
        st.pyplot(plt)

    # Sugestões de Compra
    st.subheader('Sugestões de Compra')
    for name, df in data.items():
        current_price = df['Close'][-1]
        st.write(f'Preço atual do {name}: {format_currency(current_price)}')
        if current_price < df['Close'].mean():
            st.write(f'Sugestão: Pode ser uma boa hora para comprar {name}.')
        else:
            st.write(f'Sugestão: Espere uma possível queda no preço de {name} antes de comprar.')
    
    # Voltar à página inicial
    st.sidebar.title('Navegação')
    if st.sidebar.button('Voltar'):
        st.session_state['show_graphs'] = False

if __name__ == '__main__':
    if 'show_graphs' not in st.session_state:
        st.session_state['show_graphs'] = False

    if st.session_state['show_graphs']:
        financial_data_page(st.session_state['username'])
    else:
        home()
