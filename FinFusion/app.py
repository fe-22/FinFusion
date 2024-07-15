import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import math

st.title('FinFusion - Financial Data Input')

# Função para formatar números em moeda
def format_currency(value):
    return f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Função para calcular valor futuro de uma aplicação
def calculate_investment(amount, rate, period):
    future_value = amount * math.pow((1 + rate), period)
    return future_value

# Inicializa os dados financeiros
if 'data' not in st.session_state:
    st.session_state['data'] = []

# Formulário de entrada de dados financeiros
with st.form(key='financial_form'):
    date = st.date_input('Data', datetime.today())
    description = st.text_input('Descrição')
    amount = st.number_input('Quantia', step=0.01)
    type = st.selectbox('Tipo', ['renda', 'despesa'])
    submit_button = st.form_submit_button(label='Adicionar')

    if submit_button:
        st.session_state['data'].append({
            'date': date,
            'description': description,
            'amount': amount,
            'type': type
        })

# Exibição dos dados financeiros
if st.session_state['data']:
    df = pd.DataFrame(st.session_state['data'])

    st.subheader('Dados:')
    st.write(df)

    # Cálculo do resumo financeiro
    total_income = df[df['type'] == 'renda']['amount'].sum()
    total_expenses = df[df['type'] == 'despesa']['amount'].sum()
    net_balance = total_income - total_expenses

    st.subheader('Resumo financeiro:')
    st.write(f"Renda Total: {format_currency(total_income)}")
    st.write(f"Despesas totais: {format_currency(total_expenses)}")
    st.write(f"Saldo líquido: {format_currency(net_balance)}")

    # Alerta e cálculo de juros se o saldo for negativo
    if net_balance < 0:
        interest = abs(net_balance) * 0.08
        st.warning(f"Cuidado! Você entrou no cheque especial. Juros de 8%: {format_currency(interest)}")
    else:
        # Exibe formulário de investimentos se o saldo for positivo
        with st.expander("Calculadora de Aplicações"):
            investment_amount = st.number_input('Quantia para investir', step=0.01)
            interest_rate = st.number_input('Taxa de juros anual (%)', step=0.01) / 100
            investment_period = st.number_input('Período de investimento (anos)', step=1)

            if st.button('Calcular'):
                future_value = calculate_investment(investment_amount, interest_rate, investment_period)
                st.write(f"Valor futuro: {format_currency(future_value)}")

    # Cálculo e exibição do comparativo mensal
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    current_month = datetime.today().month
    current_year = datetime.today().year

    current_month_data = df[(df['month'] == current_month) & (df['year'] == current_year)]
    last_month = current_month - 1 if current_month > 1 else 12
    last_year = current_year if current_month > 1 else current_year - 1
    last_month_data = df[(df['month'] == last_month) & (df['year'] == last_year)]

    current_month_balance = current_month_data[current_month_data['type'] == 'renda']['amount'].sum() - current_month_data[current_month_data['type'] == 'despesa']['amount'].sum()
    last_month_balance = last_month_data[last_month_data['type'] == 'renda']['amount'].sum() - last_month_data[last_month_data['type'] == 'despesa']['amount'].sum()

    balance_difference = current_month_balance - last_month_balance

    st.subheader('Comparativo com o mês anterior:')
    st.write(f"Saldo do mês anterior: {format_currency(last_month_balance)}")
    st.write(f"Saldo do mês atual: {format_currency(current_month_balance)}")
    st.write(f"Diferença: {format_currency(balance_difference)}")

# Rodapé
st.markdown("""
<footer style='text-align: center;'>
    <p>&copy; 2024 FinFusion. Todos os direitos reservados.</p>
    <p><a href="https://chatgptonline.tech/pt/" style="color: white; text-decoration: none;">Visite o nosso site</a></p>
</footer>
""", unsafe_allow_html=True)
