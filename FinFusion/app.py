import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import matplotlib.pyplot as plt
from datetime import datetime

# Funções de criação e migração do banco de dados
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

def migrate_old_data():
    conn = sqlite3.connect('finfusion.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(financial_data)")
    columns = [info[1] for info in c.fetchall()]
    if 'id' not in columns:
        c.execute("ALTER TABLE financial_data RENAME TO old_financial_data")
        c.execute('''
            CREATE TABLE financial_data (
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
            INSERT INTO financial_data (username, date, description, amount, type, payment_method, installments, necessity)
            SELECT username, date, description, amount, type, payment_method, installments, necessity
            FROM old_financial_data
        ''')
        c.execute("DROP TABLE old_financial_data")
        conn.commit()
    conn.close()

create_database()
migrate_old_data()

def get_financial_data(username):
    try:
        with sqlite3.connect('finfusion.db') as conn:
            c = conn.cursor()
            c.execute("SELECT id, date, description, amount, type, payment_method, installments, necessity FROM financial_data WHERE username=?", (username,))
            data = c.fetchall()
        return data
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

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

def format_currency(value):
    return f"R${value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def calculate_net_value(financial_data):
    net_value = 0
    for row in financial_data:
        if row[4] == 'Receita':
            net_value += row[3]
        elif row[4] == 'Despesa':
            net_value -= row[3]
    return net_value

def calculate_expenses(financial_data):
    expenses = 0
    for row in financial_data:
        if row[4] == 'Despesa':
            expenses += row[3]
    return expenses

def calculate_special_check_alert(net_value, previous_month_net_value):
    if net_value < 0:
        return f"Alerta de cheque especial! Seu saldo é de {format_currency(net_value)} e você está usando {format_currency(-net_value)} do seu cheque especial."
    elif net_value < previous_month_net_value * 0.92:  # 8% interest rate
        return f"Alerta de cheque especial! Seu saldo é de {format_currency(net_value)} e você está próximo de usar seu cheque especial."
    else:
        return ""

def calculate_balance(financial_data):
    balance = 0
    for row in financial_data:
        if row[4] == 'Receita':
            balance += row[3]
        elif row[4] == 'Despesa':
            balance -= row[3]
    return balance

def calculate_cash_expenses(financial_data):
    expenses = 0
    for row in financial_data:
        if row[4] == 'Despesa' and row[5] == 'À Vista':
            expenses += row[3]
    return expenses

def calculate_credit_card_expenses(financial_data):
    expenses = 0
    for row in financial_data:
        if row[4] == 'Despesa' and row[5] == 'Cartão de Crédito':
            expenses += row[3]
    return expenses

def add_financial_data_from_file(username, file, file_type):
    if file_type == 'csv':
        df = pd.read_csv(file)
    elif file_type == 'excel':
        df = pd.read_excel(file)
    
    for _, row in df.iterrows():
        date = row.get('date')
        description = row.get('description')
        amount = row.get('amount')
        type = row.get('type')
        payment_method = row.get('payment_method')
        installments = row.get('installments')
        necessity = row.get('necessity')
        add_financial_data(username, date, description, amount, type, payment_method, installments, necessity)

def export_financial_data_to_excel(username):
    financial_data = get_financial_data(username)
    df = pd.DataFrame(financial_data, columns=['id', 'date', 'description', 'amount', 'type', 'payment_method', 'installments', 'necessity'])
    df.to_excel(f'{username}_financial_data.xlsx', index=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(username, password):
    with sqlite3.connect('finfusion.db') as conn:
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        stored_password = c.fetchone()
        if stored_password and stored_password[0] == hash_password(password):
            return True
        else:
            return False

def register_user(username, password):
    with sqlite3.connect('finfusion.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()

def plot_balance_evolution(username):
    financial_data = get_financial_data(username)
    df = pd.DataFrame(financial_data, columns=['id', 'date', 'description', 'amount', 'type', 'payment_method', 'installments', 'necessity'])
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values(by='date', inplace=True)
    df['balance'] = df.apply(lambda row: row['amount'] if row['type'] == 'Receita' else -row['amount'], axis=1).cumsum()
    plt.figure(figsize=(10, 5))
    plt.plot(df['date'], df['balance'], marker='o')
    plt.xlabel('Data')
    plt.ylabel('Saldo')
    plt.title('Evolução do Saldo Financeiro')
    st.pyplot(plt)

def home():
    st.title('FinFusion - Controle Financeiro')

    if 'username' not in st.session_state:
        st.session_state['username'] = None

    if st.session_state['username'] is None:
        login_form()
    else:
        username = st.session_state['username']
        st.success(f'Bem-vindo, {username}!')
        
        if 'show_graphs' not in st.session_state:
            st.session_state['show_graphs'] = False

        if st.button('Adicionar Dados Financeiros'):
            st.session_state['show_graphs'] = False
            add_financial_data_form(username)

        if st.button('Ver Dados Financeiros e Gráficos'):
            st.session_state['show_graphs'] = True

        if st.session_state['show_graphs']:
            st.header('Dados Financeiros')
            financial_data = get_financial_data(username)
            if financial_data:
                df = pd.DataFrame(financial_data, columns=['id', 'date', 'description', 'amount', 'type', 'payment_method', 'installments', 'necessity'])
                st.dataframe(df)
                plot_balance_evolution(username)

def login_form():
    st.header('Login')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    
    if st.button('Login'):
        if verify_password(username, password):
            st.session_state['username'] = username
            st.success('Login bem-sucedido!')
        else:
            st.error('Nome de usuário ou senha incorretos.')

    if st.button('Registrar'):
        register_form()

def register_form():
    st.header('Registrar')
    username = st.text_input('Novo Username')
    password = st.text_input('Novo Password', type='password')

    if st.button('Registrar'):
        register_user(username, password)
        st.success('Usuário registrado com sucesso. Por favor, faça login.')
        login_form()

def add_financial_data_form(username):
    st.header('Adicionar Dados Financeiros')
    date = st.date_input('Data')
    description = st.text_input('Descrição')
    amount = st.number_input('Valor', min_value=0.0, format='%.2f')
    type = st.selectbox('Tipo', ['Receita', 'Despesa'])
    payment_method = st.selectbox('Método de Pagamento', ['À Vista', 'Cartão de Crédito'])
    installments = st.number_input('Parcelas', min_value=1, step=1)
    necessity = st.selectbox('Necessidade', ['Essencial', 'Não Essencial'])

    if st.button('Adicionar'):
        add_financial_data(username, date, description, amount, type, payment_method, installments, necessity)
        st.success('Dados adicionados com sucesso!')
        st.session_state['show_graphs'] = False

if __name__ == '__main__':
    home()
