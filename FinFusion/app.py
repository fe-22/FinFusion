# Importações
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import hashlib
from datetime import datetime, timedelta
import yfinance as yf
import matplotlib.pyplot as plt

# Funções de utilidade
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def format_currency(value):
    return f"R${value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Funções de banco de dados
def create_database():
    conn = sqlite3.connect('finfusion.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS financial_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date DATE NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            payment_method TEXT,
            installments INTEGER,
            necessity TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def download_data(symbol, start_date, end_date):
    try:
        data = yf.download(symbol, start=start_date, end=end_date)
        return data
    except BrokenPipeError:
        time.sleep(5)  # Espera de 5 segundos
        data = yf.download(symbol, start=start_date, end=end_date)
        return data

def register_user(username, password):
    with sqlite3.connect('finfusion.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()

def verify_password(username, password):
    with sqlite3.connect('finfusion.db') as conn:
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        stored_password = c.fetchone()
        return stored_password and stored_password[0] == hash_password(password)

def get_financial_data(username):
    try:
        with sqlite3.connect('finfusion.db') as conn:
            c = conn.cursor()
            c.execute("SELECT id, date, description, amount, type, payment_method, installments, necessity FROM financial_data WHERE username=?", (username,))
            data = c.fetchall()
        return data if data else []
    except sqlite3.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return []

def add_financial_data(username, date, description, amount, type, payment_method, installments, necessity):
    with sqlite3.connect('finfusion.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO financial_data (username, date, description, amount, type, payment_method, installments, necessity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (username, date, description, amount, type, payment_method, installments, necessity))
        conn.commit()

def remove_financial_data(ids):
    with sqlite3.connect('finfusion.db') as conn:
        c = conn.cursor()
        c.executemany("DELETE FROM financial_data WHERE id=?", [(id,) for id in ids])
        conn.commit()

# Funções adicionais
def calculate_total_balance(username):
    """Calcula o saldo total com base nas receitas e despesas do usuário."""
    data = get_financial_data(username)
    total_income = sum(item[3] for item in data if item[4] == "Receita")
    total_expense = sum(item[3] for item in data if item[4] == "Despesa")
    return total_income - total_expense

def display_major_expenses(username):
    """Exibe uma tabela com os maiores gastos e os gastos não essenciais."""
    data = get_financial_data(username)
    if not data:
        st.warning('Nenhum dado financeiro disponível.')
        return

    df = pd.DataFrame(data, columns=['id', 'Data', 'Descrição', 'Quantia', 'Tipo', 'Método de Pagamento', 'Parcelas', 'Necessidade'])

    major_expenses = df[df['Tipo'] == 'Despesa'].sort_values(by='Quantia', ascending=False).head(5)
    st.subheader('Maiores Gastos')
    st.table(major_expenses[['Data', 'Descrição', 'Quantia', 'Método de Pagamento', 'Necessidade']])

    non_essential_expenses = df[(df['Tipo'] == 'Despesa') & (df['Necessidade'] == 'Não essencial')].sort_values(by='Quantia', ascending=False)
    st.subheader('Gastos Supérfluos')
    st.table(non_essential_expenses[['Data', 'Descrição', 'Quantia', 'Método de Pagamento']])

def alert_overdraft_and_credit(username):
    """Exibe alertas para cheque especial e gastos excessivos no cartão de crédito."""
    balance = calculate_total_balance(username)
    if balance < 0:
        st.error(f"Alerta: Você está no cheque especial! Juros de 8% ao mês serão aplicados. Saldo: {format_currency(balance)}")

    data = get_financial_data(username)
    if not data:
        return

    df = pd.DataFrame(data, columns=['id', 'Data', 'Descrição', 'Quantia', 'Tipo', 'Método de Pagamento', 'Parcelas', 'Necessidade'])

    credit_card_expenses = df[(df['Tipo'] == 'Despesa') & (df['Método de Pagamento'] == 'Cartão de Crédito')]['Quantia'].sum()
    credit_limit = 1000  # Defina o limite conforme necessário
    if credit_card_expenses > credit_limit:
        st.warning(f"Atenção: Seus gastos no cartão de crédito estão altos ({format_currency(credit_card_expenses)}). Limite sugerido: {format_currency(credit_limit)}.")

# Função para adicionar o footer
def add_footer():
    st.markdown(
        """
        <style>
         .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: #0000FF;
            color: white;
            text-align: center;
            padding: 8px;
            font-size: 10px;
        }
        </style>
        <div class="footer">
            <p>App construído por @fthec | Contato: fernandoalexthec@gmail.com</p>
            <p>Chave pix:11982170425</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Funções das páginas
def home():
    create_database()  # Garantir que o banco de dados existe
    st.title('FinFusion - Controle Financeiro')

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        username = st.session_state['username']
        balance = calculate_total_balance(username)
        st.subheader(f'Saldo Líquido: {format_currency(balance)}')
        sidebar_navigation()
    else:
        # Formulário de login
        st.subheader('Login')
        username = st.text_input('Usuário')
        password = st.text_input('Senha', type='password')
        if st.button('Entrar'):
            if verify_password(username, password):
                st.session_state['username'] = username
                st.session_state['logged_in'] = True
                # Evite o `st.experimental_rerun()`, pois a mudança de estado automaticamente atualiza a interface.
            else:
                st.error('Nome de usuário ou senha incorretos.')
        
        # Formulário de registro
        st.subheader('Registrar')
        new_username = st.text_input('Novo Usuário')
        new_password = st.text_input('Nova Senha', type='password')
        if st.button('Registrar'):
            register_user(new_username, new_password)
            st.success('Usuário registrado com sucesso!')
            
    add_footer()


def insert_data_page():
    st.title("Inserir Dados Financeiros")

    username = st.session_state['username']

    with st.form("data_entry_form"):
        date = st.date_input("Data")
        description = st.text_input("Descrição")
        amount = st.number_input("Quantia", min_value=0.0, format="%.2f")
        type = st.selectbox("Tipo", ["Receita", "Despesa"])
        payment_method = st.selectbox("Método de Pagamento", ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Transferência"])
        installments = st.number_input("Parcelas", min_value=1, max_value=12, value=1)
        necessity = st.selectbox("Necessidade", ["Essencial", "Não essencial"])
        submitted = st.form_submit_button("Salvar")

        if submitted:
            add_financial_data(username, date, description, amount, type, payment_method, installments, necessity)
            st.success("Dados financeiros adicionados com sucesso!")
            st.experimental_set_query_params(rerun='true')
            st.experimental_rerun()

    add_footer()

def financial_data_page():
    st.title('Dados Financeiros')

    username = st.session_state['username']

    financial_data = get_financial_data(username)
    if not financial_data:
        st.warning("Nenhum dado financeiro encontrado.")
    else:
        df = pd.DataFrame(financial_data, columns=['ID', 'Data', 'Descrição', 'Quantia', 'Tipo', 'Método de Pagamento', 'Parcelas', 'Necessidade'])
        st.write("### Dados Financeiros")
        st.dataframe(df)

        # Adicionar opção de deletar dados
        ids_to_remove = st.multiselect("Selecione os IDs para remover", df['ID'])
        if st.button("Remover Selecionados"):
            remove_financial_data(ids_to_remove)
            st.success("Dados removidos com sucesso!")
            st.experimental_set_query_params(rerun='true')
            st.experimental_rerun()

    add_footer()

def financial_analysis_page():
    st.title('Análise Financeira')

    username = st.session_state['username']

    # Saldo total
    balance = calculate_total_balance(username)
    st.subheader(f'Saldo Total: {format_currency(balance)}')

    # Principais gastos
    display_major_expenses(username)

    # Alerta de cheque especial e gastos no cartão de crédito
    alert_overdraft_and_credit(username)

    add_footer()

def stock_price_page():
    st.title('Análise de Preço de Ações')

    symbol = st.text_input('Código da Ação (ex: AAPL)', 'AAPL')
    start_date = st.date_input('Data Inicial', datetime.today() - timedelta(days=365))
    end_date = st.date_input('Data Final', datetime.today())

    if st.button('Analisar'):
        data = download_data(symbol, start_date, end_date)
        if not data.empty:
            st.subheader(f'Preço de Fechamento - {symbol}')
            st.line_chart(data['Close'])
        else:
            st.warning("Nenhum dado encontrado para o código fornecido.")

    add_footer()

def sidebar_navigation():
    st.sidebar.title("Navegação")
    menu = ["Home", "Inserir Dados", "Dados Financeiros", "Análise Financeira", "Análise de Preço de Ações"]
    choice = st.sidebar.selectbox("Selecione a Página", menu)

    if choice == "Home":
        home()
    elif choice == "Inserir Dados":
        insert_data_page()
    elif choice == "Dados Financeiros":
        financial_data_page()
    elif choice == "Análise Financeira":
        financial_analysis_page()
    elif choice == "Análise de Preço de Ações":
        stock_price_page()

# Main
if __name__ == '__main__':
    home()
