import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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

# Function to retrieve financial data for a user
def get_financial_data(username):
    c.execute("SELECT date, description, amount, type FROM financial_data WHERE username=?", (username,))
    return c.fetchall()

# Function to format numbers in currency
def format_currency(value):
    return f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Function to calculate future value of an investment
def calculate_investment(amount, rate, period):
    future_value = amount * math.pow((1 + rate), period)
    return future_value

# Function to calculate monthly installments
def calculate_installments(amount, interest_rate, periods):
    if interest_rate > 0:
        return amount * (interest_rate * (1 + interest_rate) ** periods) / ((1 + interest_rate) ** periods - 1)
    else:
        return amount / periods

# Login form
st.title('FinFusion - Financial Data Input')
with st.form(key='login_form'):
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    login_button = st.form_submit_button(label='Login')

# Register form
with st.form(key='register_form'):
    new_username = st.text_input('New Username')
    new_password = st.text_input('New Password', type='password')
    confirm_password = st.text_input('Confirm Password', type='password')
    register_button = st.form_submit_button(label='Register')

if login_button:
    if authenticate_user(username, password):
        st.success('Logged in successfully!')
        st.session_state['username'] = username  # Save username in session state
    else:
        st.error('Invalid username or password')

if register_button:
    if new_password == confirm_password:
        if not user_exists(new_username):
            add_user(new_username, new_password)
            st.success('User created successfully!')
        else:
            st.error('Username already exists')
    else:
        st.error('Passwords do not match')

# If user is logged in, display financial data input form
if 'username' in st.session_state:
    username = st.session_state['username']

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
            try:
                # Add financial data to database
                if card_payment == 'parcelado':
                    for i in range(installments):
                        installment_amount = calculate_installments(amount, interest_rate, installments)
                        due_date = date + timedelta(days=30*i)
                        add_financial_data(username, due_date.strftime('%Y-%m-%d'), f"{description} (parcela {i + 1}/{installments})", -installment_amount, type)
                else:
                    add_financial_data(username, date.strftime('%Y-%m-%d'), description, -amount if type in ['despesa', 'cartão de crédito'] else amount, type)
                st.success('Dados adicionados com sucesso!')
            except Exception as e:
                st.error(f"Erro ao adicionar dados financeiros: {e}")

    # Retrieve and display financial data
    financial_data = get_financial_data(username)
    if financial_data:
        df = pd.DataFrame(financial_data, columns=['date', 'description', 'amount', 'type'])
        df['date'] = pd.to_datetime(df['date'])

        # Display financial summary
        total_income = df[df['type'] == 'renda']['amount'].sum()
        total_expenses = df[df['type'] == 'despesa']['amount'].sum()
        total_card_expenses = df[df['type'] == 'cartão de crédito']['amount'].sum()
        net_balance = total_income + total_expenses + total_card_expenses

        st.subheader('Resumo financeiro:')
        st.write(f"Renda Total: {format_currency(total_income)}")
        st.write(f"Despesas totais: {format_currency(total_expenses)}")
        st.write(f"Gastos no cartão de crédito: {format_currency(total_card_expenses)}")
        st.write(f"Saldo líquido: {format_currency(net_balance)}")

        # Alert for negative balance
        if net_balance < 0:
            interest = abs(net_balance) * 0.08
            st.warning(f"Cuidado! Você entrou no cheque especial. Juros de 8%: {format_currency(interest)}")
        else:
            # Investment calculator
            with st.expander("Calculadora de Aplicações"):
                investment_amount = st.number_input('Quantia para investir', step=0.01)
                interest_rate = st.number_input('Taxa de juros anual (%)', step=0.01) / 100
                investment_period = st.number_input('Período de investimento (anos)', step=1)

                if st.button('Calcular'):
                    future_value = calculate_investment(investment_amount, interest_rate, investment_period)
                    st.write(f"Valor futuro: {format_currency(future_value)}")

        # Monthly comparison calculation
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        current_month = datetime.today().month
        current_year = datetime.today().year

        current_month_data = df[(df['month'] == current_month) & (df['year'] == current_year)]
        last_month = current_month - 1 if current_month > 1 else 12
        last_year = current_year if current_month > 1 else current_year - 1
        last_month_data = df[(df['month'] == last_month) & (df['year'] == last_year)]

        current_month_balance = current_month_data['amount'].sum()
        last_month_balance = last_month_data['amount'].sum()

        balance_difference = current_month_balance - last_month_balance

        st.subheader('Comparativo com o mês anterior:')
        st.write(f"Saldo do mês anterior: {format_currency(last_month_balance)}")
        st.write(f"Saldo do mês atual: {format_currency(current_month_balance)}")
        st.write(f"Diferença: {format_currency(balance_difference)}")

        # Monthly detailed data display
        months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        with st.expander("Dados mensais detalhados"):
            for i, month in enumerate(months):
                month_data = df[(df['month'] == i + 1)]
                if not month_data.empty:
                    st.subheader(f"{month}")
                    st.dataframe(month_data)

        # Budget commitment percentage calculation
        debt_commitment_percentage = (total_expenses + total_card_expenses) / total_income * 100 if total_income != 0 else 0
        st.subheader('Comprometimento do orçamento:')
        st.write(f"Porcentagem comprometida com dívidas: {debt_commitment_percentage:.2f}%")

        if debt_commitment_percentage > 30:
            st.warning("Atenção! Sua dívida está comprometendo mais de 30% do seu orçamento. Considere reorganizar suas finanças.")

        # Add button to save financial data to CSV
        if st.button('Salvar dados financeiros'):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Baixar dados financeiros como CSV",
                data=csv,
                file_name=f'financial_data_{username}.csv',
                mime='text/csv',
            )

# Footer
st.markdown("""
<footer style='text-align: center;'>
    <p>&copy; 2024 FinFusion. Todos os direitos reservados. Desenvolvido por fthec</p>
    <p><a href="https://github.com/fe-22/FinFusion" style="color: blue; text-decoration: none;">
    <pre>Ajude o Dev a continuar melhorando sua vida. Pix 11982170425</pre></a></p>
</footer>
""", unsafe_allow_html=True)
