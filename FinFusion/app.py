import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

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

    # Verificar se a coluna 'id' existe
    c.execute("PRAGMA table_info(financial_data)")
    columns = [info[1] for info in c.fetchall()]

    if 'id' not in columns:
        # Renomear a tabela antiga
        c.execute("ALTER TABLE financial_data RENAME TO old_financial_data")

        # Criar a nova tabela com a estrutura correta
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

        # Migrar dados da tabela antiga para a nova tabela
        c.execute('''
            INSERT INTO financial_data (username, date, description, amount, type, payment_method, installments, necessity)
            SELECT username, date, description, amount, type, payment_method, installments, necessity
            FROM old_financial_data
        ''')

        # Remover a tabela antiga
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

# Função para adicionar despesa ou receita
def add_financial_data(username, date, description, amount, type, payment_method, installments, necessity):
    with sqlite3.connect('finfusion.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO financial_data (username, date, description, amount, type, payment_method, installments, necessity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (username, date, description, amount, type, payment_method, installments, necessity))
        conn.commit()

# Função para remover dados financeiros
def remove_financial_data(ids):
    with sqlite3.connect('finfusion.db') as conn:
        c = conn.cursor()
        c.executemany("DELETE FROM financial_data WHERE id=?", [(id,) for id in ids])
        conn.commit()

# Função para formatar números em moeda
def format_currency(value):
    return f"R${value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Função para calcular o valor líquido
def calculate_net_value(financial_data):
    net_value = 0
    for row in financial_data:
        if row[4] == 'Receita':
            net_value += row[3]
        elif row[4] == 'Despesa':
            net_value -= row[3]
    return net_value

# Função para calcular as despesas
def calculate_expenses(financial_data):
    expenses = 0
    for row in financial_data:
        if row[4] == 'Despesa':
            expenses += row[3]
    return expenses

# Função para calcular o alerta de cheque especial
def calculate_special_check_alert(net_value, previous_month_net_value):
    if net_value < 0:
        return f"Alerta de cheque especial! Seu saldo é de {format_currency(net_value)} e você está usando {format_currency(-net_value)} do seu cheque especial."
    elif net_value < previous_month_net_value * 0.92:  # 8% interest rate
        return f"Alerta de cheque especial! Seu saldo é de {format_currency(net_value)} e você está próximo de usar seu cheque especial."
    else:
        return ""

# Função para calcular o saldo
def calculate_balance(financial_data):
    balance = 0
    for row in financial_data:
        if row[4] == 'Receita':
            balance += row[3]
        elif row[4] == 'Despesa':
            balance -= row[3]
    return balance

# Função para calcular despesas à vista
def calculate_cash_expenses(financial_data):
    expenses = 0
    for row in financial_data:
        if row[4] == 'Despesa' and row[5] == 'À Vista':
            expenses += row[3]
    return expenses

# Função para calcular despesas de cartão de crédito
def calculate_credit_card_expenses(financial_data):
    expenses = 0
    for row in financial_data:
        if row[4] == 'Despesa' and row[5] == 'Cartão de Crédito':
            expenses += row[3]
    return expenses

# Função para adicionar dados financeiros de uma planilha
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

# Função para exportar dados financeiros para uma planilha
def export_financial_data_to_excel(username):
    financial_data = get_financial_data(username)
    df = pd.DataFrame(financial_data, columns=['id', 'date', 'description', 'amount', 'type', 'payment_method', 'installments', 'necessity'])
    df.to_excel(f'{username}_financial_data.xlsx', index=False)

# Função para hash de senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Função para verificar senha
def verify_password(username, password):
    with sqlite3.connect('finfusion.db') as conn:
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        stored_password = c.fetchone()
        if stored_password and stored_password[0] == hash_password(password):
            return True
        else:
            return False

# Função para registrar usuário
def register_user(username, password):
    with sqlite3.connect('finfusion.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?, ?)", (username, hash_password(password)))
        conn.commit()

# Função para a página inicial
def home():
    st.title('FinFusion - Controle Financeiro')

    if 'username' in st.session_state:
        username = st.session_state['username']
        st.success(f'Bem-vindo, {username}!')

        # Upload de planilha
        uploaded_file = st.file_uploader("Faça upload de uma planilha CSV ou Excel", type=["csv", "xlsx"])
        if uploaded_file:
            file_type = 'csv' if uploaded_file.name.endswith('.csv') else 'excel'
            add_financial_data_from_file(username, uploaded_file, file_type)
            st.success('Planilha importada com sucesso!')

        # Recuperar dados financeiros do usuário
        financial_data = get_financial_data(username)
        if financial_data is None:
            st.error('Erro ao recuperar os dados financeiros.')
            return

        # Calcular o saldo, despesas à vista e despesas de cartão de crédito
        balance = calculate_balance(financial_data)
        cash_expenses = calculate_cash_expenses(financial_data)
        credit_card_expenses = calculate_credit_card_expenses(financial_data)

        # Exibir informações financeiras
        st.subheader('Resumo Financeiro')
        st.metric('Saldo', format_currency(balance))
        st.metric('Despesas à Vista', format_currency(cash_expenses))
        st.metric('Despesas no Cartão de Crédito', format_currency(credit_card_expenses))

        # Alerta de saldo negativo
        if balance < 0:
            st.error(f'Alerta: Seu saldo está negativo! {format_currency(balance)}')

        # Formulário para adicionar dados financeiros
        with st.form(key='finance_form'):
            date = st.date_input('Data')
            description = st.text_input('Descrição')
            amount = st.number_input('Quantia', format="%0.2f")
            type = st.selectbox('Tipo', ['Receita', 'Despesa'])
            payment_method = st.selectbox('Método de Pagamento', ['À Vista', 'Cartão de Crédito'])
            installments = st.number_input('Parcelas', min_value=1, value=1)
            necessity = st.selectbox('Necessidade', ['Essencial', 'Não Essencial'])
            submit_button = st.form_submit_button('Adicionar')

            if submit_button:
                add_financial_data(username, date, description, amount, type, payment_method, installments, necessity)
                st.success('Dados financeiros adicionados com sucesso!')

        # Exibir tabela de dados financeiros
        st.subheader('Dados Financeiros')
        if financial_data:
            df = pd.DataFrame(financial_data, columns=['id', 'Data', 'Descrição', 'Quantia', 'Tipo', 'Método de Pagamento', 'Parcelas', 'Necessidade'])
            st.table(df.drop(columns=['id']))  # Exibir tabela sem a coluna 'id'

        # Seleção de linhas para remoção
        st.subheader('Remover Dados Financeiros')
        remove_ids = st.multiselect('Selecione os IDs dos dados a serem removidos', options=[row[0] for row in financial_data])
        if st.button('Remover Selecionados'):
            remove_financial_data(remove_ids)
            st.success('Dados removidos com sucesso!')

        # Link para a página de dados financeiros e gráficos
        st.sidebar.title('Navegação')
        if st.sidebar.button('Ver Dados Financeiros e Gráficos'):
            st.session_state['show_graphs'] = True
            st.experimental_rerun()

    else:
        st.subheader('Login')
        username = st.text_input('Usuário')
        password = st.text_input('Senha', type='password')
        if st.button('Entrar'):
            if verify_password(username, password):
                st.session_state['username'] = username
                st.success('Login bem-sucedido!')
                st.experimental_rerun()
            else:
                st.error('Nome de usuário ou senha incorretos.')

        st.subheader('Registrar')
        new_username = st.text_input('Novo Usuário')
        new_password = st.text_input('Nova Senha', type='password')
        if st.button('Registrar'):
            register_user(new_username, new_password)
            st.success('Usuário registrado com sucesso!')

# Função para a página de dados financeiros e gráficos
def financial_data_page(username):
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
    st.pyplot(plt)

    # Gráfico de tipos de despesas
    st.subheader('Gráfico de Tipos de Despesas')
    expense_df = df[df['Tipo'] == 'Despesa']
    expense_df.groupby('Descrição')['Quantia'].sum().plot(kind='bar')
    plt.title('Despesas por Categoria')
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
        st.experimental_rerun()

if __name__ == '__main__':
    if 'show_graphs' in st.session_state and st.session_state['show_graphs']:
        financial_data_page(st.session_state['username'])
    else:
        home()
