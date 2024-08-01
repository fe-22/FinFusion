import streamlit as st
import json

# Crie um objeto para armazenar as informações digitadas
data = {}

# Crie uma função para armazenar as informações digitadas
def store_data(key, value):
    data[key] = value
    # Armazene as informações no armazenamento local
    localStorage.setItem('finfusion_data', json.dumps(data))

# Crie uma função para recuperar as informações armazenadas
def retrieve_data(key):
    # Recupere as informações do armazenamento local
    stored_data = localStorage.getItem('finfusion_data')
    if stored_data:
        data = json.loads(stored_data)
        return data.get(key)
    return None

# Exemplo de como utilizar as funções
st.text_input('Nome:', key='nome')
st.text_input('Email:', key='email')

# Armazene as informações digitadas
store_data('nome', st.session_state.nome)
store_data('email', st.session_state.email)

# Recupere as informações armazenadas
nome = retrieve_data('nome')
email = retrieve_data('email')

# Exiba as informações armazenadas
st.write(f'Nome: {nome}')
st.write(f'Email: {email}')