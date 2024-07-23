import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import math
import hashlib
import sqlite3

# Create a SQLite database connection
conn = sqlite3.connect('finfusion.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, password TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS financial_data
             (username TEXT, date DATE, description TEXT, amount REAL, type TEXT)''')
conn.commit()

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to check if user exists
def user_exists(username):
    c.execute("SELECT 1 FROM users WHERE username=?", (username,))
    return c.fetchone() is not None

# Function to authenticate user
def authenticate_user(username, password):
    c.execute("SELECT 1 FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    return c.fetchone() is not None

# Function to add new user
def add_user(username, password):
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
    conn.commit()

# Function to add financial data
def add_financial_data(username, date, description, amount, type):
    c.execute("INSERT INTO financial_data (username, date, description, amount, type) VALUES (?, ?, ?, ?, ?)", (username, date, description, amount, type))
    conn.commit()

# Login form
with st.form(key='login_form'):
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    login_button = st.form_submit_button(label='Login')

if login_button:
    if authenticate_user(username, password):
        st.success('Logged in successfully!')
        # Load user's financial data
        c.execute("SELECT * FROM financial_data WHERE username=?", (username,))
        financial_data = c.fetchall()
        # Process financial data
        # ...
    else:
        st.error('Invalid username or password')

# Register form
with st.form(key='register_form'):
    new_username = st.text_input('New Username')
    new_password = st.text_input('New Password', type='password')
    confirm_password = st.text_input('Confirm Password', type='password')
    register_button = st.form_submit_button(label='Register')

if register_button:
    if new_password == confirm_password:
        if not user_exists(new_username):
            add_user(new_username, new_password)
            st.success('User created successfully!')
        else:
            st.error('Username already exists')
    else:
        st.error('Passwords do not match')

# Financial data input form
with st.form(key='financial_form'):
    date = st.date_input('Data', datetime.today())
    description = st.text_input('Descrição')
    amount = st.number_input('Quantia', step=0.01)
    type = st.selectbox('Tipo', ['renda', 'despesa', 'cartão de crédito'])
    card_payment = st.selectbox('Pagamento no cartão', ['não', 'à vista', 'parcelado'])
    installments = 1
    interest_rate = 0

    if card_payment == 'parcelado':
        installments = st.number_input('Número de parcelas', min_value=1, step=1)
        interest_rate = st.number_input('Taxa de juros mensal (%)', step=0.01) / 100

    submit_button = st.form_submit_button(label='Adicionar')

    if submit_button:
        # Add financial data to database
        add_financial_data(username, date, description, amount, type)
        # Process financial data
        # ...

# Display financial data
c.execute("SELECT * FROM financial_data WHERE username=?", (username,))
financial_data = c.fetchall()
# Process financial data
# ...

