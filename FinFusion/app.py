import streamlit as st
import pandas as pd
import sqlite3
import hashlib

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
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()

# Função para a página inicial
def home():
    st.title('FinFusion - Controle Financeiro')

    if 'username' in st.session_state:
        username = st.session_state['username']
        st.success(f'Bem-vindo, {username}!')
        financial_data_page(username)  # Após o login, vá para a página de gráficos
    else:
        # Exibir a interface de login
        st.subheader('Login')
        username = st.text_input('Usuário')
        password = st.text_input('Senha', type='password')
        if st.button('Entrar'):
            if verify_password(username, password):
                st.session_state['username'] = username
                st.session_state['show_graphs'] = True  # Ativa a navegação para gráficos
                st.experimental_rerun()  # Reinicia a aplicação para refletir o estado da sessão
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
    if financial_data is None or len(financial_data) == 0:
        st.error('Erro ao recuperar os dados financeiros ou nenhum dado disponível.')
        return

    # Exibir tabela de dados financeiros
    st.subheader('Dados Financeiros')
    df = pd.DataFrame(financial_data, columns=['id', 'Data', 'Descrição', 'Quantia', 'Tipo', 'Método de Pagamento', 'Parcelas', 'Necessidade'])
    st.table(df.drop(columns=['id']))  # Exibir tabela sem a coluna 'id'

# Função para recuperar dados financeiros do banco de dados
def get_financial_data(username):
    try:
        with sqlite3.connect('finfusion.db') as conn:
            c = conn.cursor()
            c.execute("SELECT id, date, description, amount, type, payment_method, installments, necessity FROM financial_data WHERE username=?", (username,))
            data = c.fetchall()
        return data
    except sqlite3.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

if __name__ == '__main__':
    if 'show_graphs' not in st.session_state:
        st.session_state['show_graphs'] = False

    if st.session_state['show_graphs']:
        financial_data_page(st.session_state['username'])
    else:
        home()
