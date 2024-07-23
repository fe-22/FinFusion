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

# Função para calcular parcelas mensais
def calculate_installments(amount, interest_rate, periods):
    if interest_rate > 0:
        return amount * (interest_rate * (1 + interest_rate) ** periods) / ((1 + interest_rate) ** periods - 1)
    else:
        return amount / periods

# Inicializa os dados financeiros
if 'data' not in st.session_state:
    st.session_state['data'] = []

# Formulário de entrada de dados financeiros
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
        if card_payment == 'parcelado':
            for i in range(installments):
                installment_amount = calculate_installments(amount, interest_rate, installments)
                due_date = date + pd.DateOffset(months=i)
                st.session_state['data'].append({
                    'date': due_date,
                    'description': f"{description} (parcela {i + 1}/{installments})",
                    'amount': -installment_amount,
                    'type': type
                })
        else:
            st.session_state['data'].append({
                'date': date,
                'description': description,
                'amount': -amount if type in ['despesa', 'cartão de crédito'] else amount,
                'type': type
            })

# Exibição dos dados financeiros
if st.session_state['data']:
    df = pd.DataFrame(st.session_state['data'])
    df['date'] = pd.to_datetime(df['date'])
    
    df.to_csv('financial_data.csv', index=False)

    # Cálculo do resumo financeiro
    total_income = df[df['type'] == 'renda']['amount'].sum()
    total_expenses = df[df['type'] == 'despesa']['amount'].sum()
    total_card_expenses = df[df['type'] == 'cartão de crédito']['amount'].sum()
    net_balance = total_income + total_expenses + total_card_expenses

    st.subheader('Resumo financeiro:')
    st.write(f"Renda Total: {format_currency(total_income)}")
    st.write(f"Despesas totais: {format_currency(total_expenses)}")
    st.write(f"Gastos no cartão de crédito: {format_currency(total_card_expenses)}")
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

    current_month_balance = current_month_data[current_month_data['type'] == 'renda']['amount'].sum() + current_month_data[current_month_data['type'] == 'despesa']['amount'].sum() + current_month_data[current_month_data['type'] == 'cartão de crédito']['amount'].sum()
    last_month_balance = last_month_data[last_month_data['type'] == 'renda']['amount'].sum() + last_month_data[last_month_data['type'] == 'despesa']['amount'].sum() + last_month_data[last_month_data['type'] == 'cartão de crédito']['amount'].sum()

    balance_difference = current_month_balance - last_month_balance

    st.subheader('Comparativo com o mês anterior:')
    st.write(f"Saldo do mês anterior: {format_currency(last_month_balance)}")
    st.write(f"Saldo do mês atual: {format_currency(current_month_balance)}")
    st.write(f"Diferença: {format_currency(balance_difference)}")

    # Exibição de abas para cada mês do ano
    months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    with st.expander("Dados mensais detalhados"):
        for i, month in enumerate(months):
            month_data = df[(df['month'] == i + 1)]
            if not month_data.empty:
                st.subheader(f"{month}")
                st.dataframe(month_data)

    # Cálculo da porcentagem de comprometimento do orçamento
    debt_commitment_percentage = (total_expenses + total_card_expenses) / total_income * 100
    st.subheader('Comprometimento do orçamento:')
    st.write(f"Porcentagem comprometida com dívidas: {debt_commitment_percentage:.2f}%")

    if debt_commitment_percentage > 30:
        st.warning("Atenção! Sua dívida está comprometendo mais de 30% do seu orçamento. Considere reorganizar suas finanças.")

# Rodapé
st.markdown("""
<footer style='text-align: center;'>
    <p>&copy; 2024 FinFusion. Todos os direitos reservados.Desenvolvido por fthec</p>
    <p><a href="https://github.com/fe-22/FinFusion" style="color: blue; text-decoration: none;">
    <pre>Ajude o Dev a continuar melhorando sua vida.Pix11982170425</pre></a></p>
</footer>
""", unsafe_allow_html=True)


