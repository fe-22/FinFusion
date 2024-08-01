import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import yfinance as yf

# Função para atualizar o esquema do banco de dados
def update_database_schema():
    with sqlite3.connect('finfusion.db') as conn:
        c = conn.cursor()

        # Verificar se a coluna 'payment_method' já existe
        c.execute("PRAGMA table_info(financial_data)")
        columns = [info[1] for info in c.fetchall()]

        if 'payment_method' not in columns:
            c.execute("ALTER TABLE financial_data ADD COLUMN payment_method TEXT")

        if 'installments' not in columns:
            c.execute("ALTER TABLE financial_data ADD COLUMN installments INTEGER")

        conn.commit()

# Atualizar o esquema do banco de dados
update_database_schema()

# Função para recuperar dados financeiros de um usuário
def get_financial_data(username):
    with sqlite3.connect('finfusion.db') as conn:
        c = conn.cursor()
        c.execute("SELECT date, description, amount, type, payment_method, installments FROM financial_data WHERE username=?", (username,))
        data = c.fetchall()
    return data

# Função para adicionar despesa ou receita
def add_financial_data(username, date, description, amount, type, payment_method, installments):
    with sqlite3.connect('finfusion.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO financial_data (username, date, description, amount, type, payment_method, installments) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (username, date, description, amount, type, payment_method, installments))
        conn.commit()

# Função para formatar números em moeda
def format_currency(value):
    return f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Função para a página inicial
def home():
    st.title('FinFusion - Controle Financeiro')

    if 'username' in st.session_state:
        username = st.session_state['username']
        st.success(f'Bem-vindo, {username}!')

        # Formulário para adicionar dados financeiros
        with st.form(key='finance_form'):
            date = st.date_input('Data')
            description = st.text_input('Descrição')
            amount = st.number_input('Quantia', format="%0.2f")
            type = st.selectbox('Tipo', ['Receita', 'Despesa'])
            payment_method = st.selectbox('Método de Pagamento', ['À Vista', 'Parcelado'])
            installments = st.number_input('Número de Parcelas', min_value=1, value=1)
            submit_button = st.form_submit_button(label='Adicionar')

            if submit_button:
                add_financial_data(username, date, description, amount, type, payment_method, installments)
                st.success('Dados financeiros adicionados com sucesso!')

        # Exibir os dados financeiros do usuário
        st.subheader('Seus Dados Financeiros')
        financial_data = get_financial_data(username)
        if financial_data:
            df = pd.DataFrame(financial_data, columns=['date', 'description', 'amount', 'type', 'payment_method', 'installments'])
            st.dataframe(df)
        else:
            st.info('Nenhum dado financeiro encontrado.')

        # Botão para ir para a página de análise financeira
        if st.button('Ir para Análise Financeira'):
            st.session_state['page'] = 'financial_analysis'
            st.experimental_rerun()
    else:
        # Formulário de login
        with st.form(key='login_form'):
            username = st.text_input('Username')
            password = st.text_input('Password', type='password')
            login_button = st.form_submit_button(label='Login')
            if login_button:
                # Simulação de autenticação (deve ser substituída por autenticação real)
                st.session_state['username'] = username
                st.success('Logged in successfully!')

        # Formulário de registro
        with st.form(key='register_form'):
            new_username = st.text_input('New Username')
            new_password = st.text_input('New Password', type='password')
            confirm_password = st.text_input('Confirm Password', type='password')
            email = st.text_input('Email')
            register_button = st.form_submit_button(label='Register')
            if register_button:
                # Simulação de registro (deve ser substituída por registro real)
                st.success('User created successfully!')

# Função para a página de análise financeira
def financial_analysis():
    st.title('FinFusion - Financial Charts')

    if 'username' in st.session_state:
        username = st.session_state['username']

        # Recuperar dados financeiros
        financial_data = get_financial_data(username)
        if financial_data:
            df = pd.DataFrame(financial_data, columns=['date', 'description', 'amount', 'type', 'payment_method', 'installments'])
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
            st.title("Consulta de Ações - Itaú, Bitcoin e Etherium")

            # Carrega os dados das ações do Itaú
            itau = yf.Ticker("ITUB4.SA")
            itau_hist = itau.history(period="1y")

            # Carrega os dados do Bitcoin
            bitcoin = yf.Ticker("BTC-USD")
            bitcoin_hist = bitcoin.history(period="1y")

            # Carrega os dados do Etherium
            etherium = yf.Ticker("ETH-USD")
            etherium_hist = etherium.history(period="1y")

            # Carrega os dados do Ibovespa
            ibovespa = yf.Ticker("^BVSP")
            ibovespa_hist = ibovespa.history(period="1y")

            # Gráficos de ações
            st.subheader("Evolução dos Preços das Ações do Itaú")
            st.line_chart(itau_hist["Close"])

            st.subheader("Evolução dos Preços do Bitcoin")
            st.line_chart(bitcoin_hist["Close"])

            st.subheader("Evolução dos Preços do Etherium")
            st.line_chart(etherium_hist["Close"])

            st.subheader("Evolução do IBOVESPA")
            st.line_chart(ibovespa_hist["Close"])

# Barra lateral para navegação
st.sidebar.title("Navegação")
page = st.sidebar.radio("Ir para", ("Página Inicial", "Análise Financeira"))

# Selecionar a página
if page == "Página Inicial":
    home()
elif page == "Análise Financeira":
    financial_analysis()

# Rodapé
st.markdown("""
<footer style='text-align: center;'>
    <p>&copy; 2024 FinFusion. Todos os direitos reservados. Desenvolvido por fthec</p>
    <p><a href="https://github.com/fe-22/FinFusion" style="color: blue; text-decoration: none;">
    <pre>Ajude o Dev a continuar melhorando sua vida. Pix 11982170425</pre></a></p>
</footer>
""", unsafe_allow_html=True)
