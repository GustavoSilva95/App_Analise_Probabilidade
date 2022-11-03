##########################################################################
###### Calculadora Análise de Probabilidade para Ações              ######
###### Versão = 1.0                                                 ######
###### Autor = Gustavo Silva                                        ######
###### LinkedIn = http://www.linkedin.com/in/gustavo-vinicius-silva ######
##########################################################################

# Bibliotecas
import streamlit as st
from scipy.stats import norm
from arch import arch_model
import yfinance as yf
import pandas as pd
import numpy as np
import datetime


# Retorna a variação do preço em cada desvio em relação ao Preço Atual
def delta_preco():
    delta = (pr / preco_atual -1) *100
    return delta
    

# Retorna o preço em cada desvio padrão
def preco_por_desvio():
    desvios = [-3, -2, -1, 1, 2, 3]
    cols = st.columns((1, 1, 1, 1, 1, 1))
    for i, d in enumerate(desvios):
        global pr
        pr = preco_atual * np.exp((tx_juro - vol**2/2) * prazo/dias_ano + (d) * vol * np.sqrt(prazo / dias_ano))
        if d == 1 or d == -1:
            cols[i].metric(f'{d} Desvio', value=f'{pr:.2f}', delta=f'{delta_preco():.2f}%')
        else:
            cols[i].metric(f'{d} Desvios', value=f'{pr:.2f}', delta=f'{delta_preco():.2f}%')


# Retorna a probabilidade do Preço Atual do Ativo terminar abaixo, acima e entre Menor e maior Preço Alvo
def probabilidade():
    d1_abaixo = (np.log(preco_atual / menor_preco) + (tx_juro - 1/2 * vol**2) * prazo / dias_ano) / (vol * np.sqrt(2 * prazo / dias_ano))

    d1_acima = (np.log(maior_preco / preco_atual) - (tx_juro - 1/2 * vol**2) * prazo / dias_ano) / (vol * np.sqrt(2 * prazo / dias_ano))

    erfc_d1_abaixo = 2 - 2 * norm.cdf(d1_abaixo * np.sqrt(2))
    erfc_d1_acima = 2 - 2 * norm.cdf(d1_acima * np.sqrt(2))

    prob_abaixo = 1/2 * erfc_d1_abaixo * 100
    prob_acima = 1/2 * erfc_d1_acima * 100

    cols = st.columns((1 ,1 , 1))
    cols[0].metric(f'Terminar Abaixo de $ {menor_preco}', value=f'{prob_abaixo:.2f}%')
    cols[1].metric(f'Terminar entre $ {menor_preco} e $ {maior_preco}', value=f'{100 - (prob_abaixo + prob_acima):.2f}%')
    cols[2].metric(f'Terminar Acima de $ {maior_preco}', value=f'{prob_acima:.2f}%')


# Retorna a Volatilidade Histórica e a Volatilidade Garch
def volatilidade():
    prices = yf.download(tickers=ativo, period=periodo)['Adj Close'].dropna()

    log_returns = np.log(prices/prices.shift(1))

    ret = log_returns.dropna()
    model = arch_model(ret, vol='Garch', p=1, o=0, q=1, dist='Normal')
    results = model.fit()

    par = results.params.tolist()
    omega = par[1]
    alfa = par[2]
    beta = par[3]
    gama = 1 - alfa - beta
    var = omega / gama
    garch = (var * 252)**(1/2)
    hist = ret.std() * (252**(1/2))

    cols = st.columns((1, 1))
    cols[0].markdown('# 📈📉')
    cols[1].markdown('# 📈📉')
    
    cols[0].metric('Volatilidade Histórica', value=f'{hist * 100:.2f}%')
    cols[1].metric('Volatilidade Garch', value=f'{garch * 100:.2f}%')
    

# Retorna o intervalo entre as datas de inicio e fim
def iterdates(data1, data2):
    global one_day
    one_day = datetime.timedelta(days = 1)
    current = data1
    while current < data2:
        yield current
        current += one_day


# Retorna os dias úteis, dias corridos e feriados existentes no intervalo selecionado
def dias_uteis():
    lista_feriados = []
    for f in df['Data']:
        lista_feriados.append(f)

    one_day = datetime.timedelta(days = 1)
    dias_u = 0
    dias_c = 0
    feriad = 0
    for d in iterdates(data_inicial, data_final + one_day):
        if d.weekday() not in (5, 6) and d not in lista_feriados:
            dias_u += 1    
        
        if d in lista_feriados:
            feriad +=1
        
        dias_c += 1
    cols = st.columns((1, 1, 1))
    cols[0].metric('Dias Úteis', value=f'{dias_u} 📆')
    cols[1].metric('Feriados', value=f'{feriad} 📆')
    cols[2].metric('Dias Corridos', value=f'{dias_c} 📆')


# Bloco inicial do app
st.set_page_config(page_title="Análise de Probabilidade", page_icon="📈", layout="centered")
st.sidebar.subheader('by [Gustavo Silva](http://www.linkedin.com/in/gustavo-vinicius-silva)')
st.sidebar.title('Calculadoras')
calculadora = st.sidebar.selectbox('Selecione uma calculadora:', ['Probabilidade', 'Volatilidade', 'Dias Úteis'])


################################
# Calculadora de Probabilidade #
################################
if calculadora == 'Probabilidade':
    st.title("📈 Calculadora de Probabilidade para Ações")
    st.markdown('### Parâmetros de Entrada')

    cols = st.columns((1, 1))
    preco_atual = cols[0].number_input('Preço Atual (S):', step=0.01, min_value=0.00)
    menor_preco = cols[1].number_input('Menor Preço-Alvo:', step=0.01, min_value=0.00)

    prazo = cols[0].number_input('Prazo em dias (T):',format='%d', step=1, min_value=0)
    maior_preco = cols[1].number_input('Maior Preço-Alvo:', step=0.01, min_value=0.00)

    vol = cols[0].number_input('Volatilidade (% a.a.):') / 100
    dias_ano = cols[1].number_input('Dias do Ano:',format='%d', step=1, min_value=0, value=252 )

    tx_juro = cols[0].number_input('Tx.Juro (% a.a.):') / 100


    calcular = st.button('Calcular')

    if calcular:
        try:
            st.markdown('### Preço em cada Desvio Padrão')
            preco_por_desvio()
            st.markdown('### Probabilidade do Preço Atual do Ativo')
            probabilidade()
        except ZeroDivisionError:
            st.warning('Preencha todos os campos!', icon="⚠️")


###############################
# Calculadora de Volatilidade #
###############################
elif calculadora == 'Volatilidade':
    st.title('📈Calculadora de Volatilidade📉')

    cols = st.columns((1, 2))
    ativo = cols[0].text_input('Ticker da Ação:').upper() + '.SA'
    periodo = str(cols[1].slider('Período (Dias Úteis):', min_value=1, max_value=1260, value=252)) + 'd'
    calcular_vol = st.button('Calcular Volatilidade')

    if calcular_vol:
        try:
            volatilidade()
        except ValueError:
            st.warning('Tiker não encontrado!', icon="⚠️")
        except ZeroDivisionError:
            st.warning('Problema ao calcular o Garch. Por favor, preencha o Tiker novamente. Aumente o período caso persista o erro.', icon="⚠️")


##########################
# Calculadora Dias Úteis #
##########################
else:
    st.title("📆 Calculadora Dias Úteis 📆")

    data_inicial = st.date_input(
        "Data de Início",
        datetime.date.today())

    data_final = st.date_input(
        "Data Final",
        datetime.date.today())

    df = pd.read_excel('https://github.com/GustavoSilva95/App_Analise_Probabilidade/raw/main/feriados/feriados.xlsx')
    df['Data'] = pd.to_datetime(df['Data'], format="%Y-%m-%d").dt.date

    calcular_dias_uteis = st.button('Calcular Dias Úteis')
    if calcular_dias_uteis:
        dias_uteis()   
    