##########################################################################
###### Calculadora Análise de Probabilidade para Ações              ######
###### Versão = 2.0                                                 ######
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

@st.cache_data(ttl=3600)
def carregar_feriados():
    try:
        sheet_id = "1CL4jPYJ-kvLAf30HUTSXLAH_4SFnUhLAga0O-kRMnKc"  # ID da sua planilha
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        df = pd.read_csv(url)
        
        # Tenta diferentes formatos de data
        for fmt in ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d', '%m/%d/%Y']:
            try:
                df['Data'] = pd.to_datetime(df['Data'], format=fmt).dt.date
                break
            except:
                continue
        else:
            # Se nenhum formato funcionar, usa inferência
            df['Data'] = pd.to_datetime(df['Data'], infer_datetime_format=True).dt.date
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar feriados: {str(e)}")
        return pd.DataFrame()
    
# Configuração da página
st.set_page_config(
    page_title="Quantum Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Moderno
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .stApp {
        background: #0f172a;
    }
    
    .calculator-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    .header-title {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        color: #94a3b8;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .section-title {
        color: #e2e8f0;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        border-left: 4px solid #00b4db;
        padding-left: 1rem;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(0, 180, 219, 0.3);
    }
    
    .stNumberInput>div>div>input, .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: white;
        padding: 0.75rem;
    }
    
    .stSelectbox>div>div>select {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: white;
    }
    
    .stDateInput>div>div>input {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: white;
    }
    
    .calculator-tabs {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
        gap: 1rem;
    }
    
    .tab-button {
        padding: 1rem 2rem;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #94a3b8;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .tab-button.active {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
        color: white;
        box-shadow: 0 10px 25px rgba(0, 180, 219, 0.3);
    }
    
    .result-badge {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .risk-high { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
    .risk-medium { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
    .risk-low { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
</style>
""", unsafe_allow_html=True)

# Funções existentes (mantidas iguais)
def delta_preco():
    delta = (pr / preco_atual -1) *100
    return delta

def preco_por_desvio():
    desvios = [-3, -2, -1, 1, 2, 3]
    cols = st.columns(6)
    for i, d in enumerate(desvios):
        global pr
        pr = preco_atual * np.exp((tx_juro - vol**2/2) * prazo/dias_ano + (d) * vol * np.sqrt(prazo / dias_ano))
        delta = delta_preco()
        
        with cols[i]:
            # Título dentro do card estilizado
            st.markdown(f"""
                <div class="metric-card">
                    <strong>{d} Desvio{"s" if abs(d) != 1 else ""}</strong>
                </div>
            """, unsafe_allow_html=True)
            
            # Preço e delta com st.metric (mantém formatação Streamlit)
            if d == 1 or d == -1:
                st.metric(label="", value=f'R$ {pr:.2f}', delta=f'{delta:.2f}%')
            else:
                st.metric(label="", value=f'R$ {pr:.2f}', delta=f'{delta:.2f}%')

def probabilidade():
    d1_abaixo = (np.log(preco_atual / menor_preco) + (tx_juro - 1/2 * vol**2) * prazo / dias_ano) / (vol * np.sqrt(2 * prazo / dias_ano))
    d1_acima = (np.log(maior_preco / preco_atual) - (tx_juro - 1/2 * vol**2) * prazo / dias_ano) / (vol * np.sqrt(2 * prazo / dias_ano))

    erfc_d1_abaixo = 2 - 2 * norm.cdf(d1_abaixo * np.sqrt(2))
    erfc_d1_acima = 2 - 2 * norm.cdf(d1_acima * np.sqrt(2))

    prob_abaixo = 1/2 * erfc_d1_abaixo * 100
    prob_acima = 1/2 * erfc_d1_acima * 100
    prob_entre = 100 - (prob_abaixo + prob_acima)

    cols = st.columns(3)
    with cols[0]:
        risk_class = "risk-high" if prob_abaixo > 50 else "risk-medium" if prob_abaixo > 25 else "risk-low"
        st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
        st.metric(f'**Abaixo de R$ {menor_preco}**', value=f'{prob_abaixo:.1f}%')
        st.markdown(f'<div class="result-badge {risk_class}">{"ALTO" if prob_abaixo > 50 else "MÉDIO" if prob_abaixo > 25 else "BAIXO"} RISCO</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
        st.metric(f'**Entre R$ {menor_preco} - R$ {maior_preco}**', value=f'{prob_entre:.1f}%')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with cols[2]:
        risk_class = "risk-high" if prob_acima > 50 else "risk-medium" if prob_acima > 25 else "risk-low"
        st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
        st.metric(f'**Acima de R$ {maior_preco}**', value=f'{prob_acima:.1f}%')
        st.markdown(f'<div class="result-badge {risk_class}">{"ALTO" if prob_acima > 50 else "MÉDIO" if prob_acima > 25 else "BAIXO"} POTENCIAL</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def volatilidade():
    prices = yf.download(tickers=ativo, period=periodo, auto_adjust=False)['Adj Close'].dropna()
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
    hist = ret.std().item() * (252**(1/2))

    cols = st.columns(2)
    with cols[0]:
        st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
        st.metric('**Volatilidade Histórica**', value=f'{hist * 100:.2f}%')
        st.markdown('<div style="color: #94a3b8; font-size: 0.9rem;">Baseada em dados históricos</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
        st.metric('**Volatilidade GARCH**', value=f'{garch * 100:.2f}%')
        st.markdown('<div style="color: #94a3b8; font-size: 0.9rem;">Modelo preditivo avançado</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def iterdates(data1, data2):
    global one_day
    one_day = datetime.timedelta(days = 1)
    current = data1
    while current < data2:
        yield current
        current += one_day

def dias_uteis():
    try:
        # Carregar feriados com cache
        df = carregar_feriados()
        
        if df.empty:
            st.error("Não foi possível carregar a lista de feriados")
            return
            
        lista_feriados = df['Data'].tolist()

        one_day = datetime.timedelta(days=1)
        dias_u = 0
        dias_c = 0
        feriad = 0
        
        for d in iterdates(data_inicial, data_final + one_day):
            if d.weekday() not in (5, 6) and d not in lista_feriados:
                dias_u += 1    
            if d in lista_feriados:
                feriad +=1
            dias_c += 1
        
        cols = st.columns(3)
        with cols[0]:
            st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
            st.metric('**Dias Úteis**', value=f'{dias_u}')
            st.markdown('<div style="color: #94a3b8; font-size: 0.9rem;">Dias de negociação</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
            st.metric('**Feriados**', value=f'{feriad}')
            st.markdown('<div style="color: #94a3b8; font-size: 0.9rem;">Dias não úteis</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with cols[2]:
            st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
            st.metric('**Dias Corridos**', value=f'{dias_c}')
            st.markdown('<div style="color: #94a3b8; font-size: 0.9rem;">Total do período</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Erro ao calcular dias úteis: {str(e)}")

# Header Principal
st.markdown('<div class="header-title">Quantum Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Análise Quantitativa Avançada para Mercado Financeiro</div>', unsafe_allow_html=True)

# Navegação por Tabs
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    prob_tab = st.button("📊 Probabilidade", use_container_width=True)
with col2:
    vol_tab = st.button("📈 Volatilidade", use_container_width=True)
with col3:
    days_tab = st.button("📅 Dias Úteis", use_container_width=True)

# Inicializar estado da tab
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'Probabilidade'

# Atualizar tab baseado nos botões
if prob_tab:
    st.session_state.current_tab = 'Probabilidade'
if vol_tab:
    st.session_state.current_tab = 'Volatilidade'
if days_tab:
    st.session_state.current_tab = 'Dias Úteis'

# Calculadora de Probabilidade
if st.session_state.current_tab == 'Probabilidade':
    st.markdown('<div class="calculator-card">', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">📊 Calculadora de Probabilidade</div>', unsafe_allow_html=True)
    
    cols = st.columns(2)
    with cols[0]:
        st.subheader("💰 Preços")
        preco_atual = st.number_input('Preço Atual (R$)', value=100.0, step=0.1, format="%.2f")
        menor_preco = st.number_input('Menor Preço-Alvo (R$)', value=90.0, step=0.1, format="%.2f")
        maior_preco = st.number_input('Maior Preço-Alvo (R$)', value=110.0, step=0.1, format="%.2f")
    
    with cols[1]:
        st.subheader("⚙️ Parâmetros")
        prazo = st.number_input('Prazo (dias)', value=30, step=1)
        vol = st.number_input('Volatilidade (% a.a.)', value=30.0, step=1.0) / 100
        dias_ano = st.number_input('Dias Úteis no Ano', value=252, step=1)
        tx_juro = st.number_input('Taxa de Juro (% a.a.)', value=10.0, step=0.1) / 100

    calcular_prob = st.button('🎯 Calcular Probabilidades', use_container_width=True)

    if calcular_prob:
        if preco_atual > 0 and menor_preco > 0 and maior_preco > 0:
            st.markdown('<div class="section-title">📈 Preços por Desvio Padrão</div>', unsafe_allow_html=True)
            preco_por_desvio()
            
            st.markdown('<div class="section-title">🎲 Probabilidades de Termino</div>', unsafe_allow_html=True)
            probabilidade()
        else:
            st.error("⚠️ Por favor, insira valores válidos para todos os campos")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Calculadora de Volatilidade
elif st.session_state.current_tab == 'Volatilidade':
    st.markdown('<div class="calculator-card">', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">📈 Calculadora de Volatilidade</div>', unsafe_allow_html=True)
    
    cols = st.columns([2, 1])
    with cols[0]:
        ativo = st.text_input('Ticker da Ação (ex: PETR4, VALE3)', 'PETR4').upper() + '.SA'
    with cols[1]:
        periodo = str(st.slider('Período (dias úteis)', 30, 1260, 252)) + 'd'

    calcular_vol = st.button('📊 Calcular Volatilidade', use_container_width=True)

    if calcular_vol:
        try:
            st.markdown('<div class="section-title">📊 Resultados da Volatilidade</div>', unsafe_allow_html=True)
            volatilidade()
        except Exception as e:
            st.error(f"⚠️ Erro ao calcular volatilidade: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Calculadora de Dias Úteis
else:
    st.markdown('<div class="calculator-card">', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">📅 Calculadora de Dias Úteis</div>', unsafe_allow_html=True)
    
    cols = st.columns(2)
    with cols[0]:
        data_inicial = st.date_input("Data Inicial", datetime.date.today())
    with cols[1]:
        data_final = st.date_input("Data Final", datetime.date.today() + datetime.timedelta(days=30))


    calcular_dias = st.button('📅 Calcular Dias Úteis', use_container_width=True)

    if calcular_dias:
        st.markdown('<div class="section-title">📋 Resultado do Período</div>', unsafe_allow_html=True)
        dias_uteis()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; color: #64748b; margin-top: 3rem; padding: 2rem;">
    <hr style="border-color: #334155; margin-bottom: 1rem;">
    <div>Quantum Analytics v2.0 • Desenvolvido por Gustavo Silva</div>
    <div style="font-size: 0.8rem; margin-top: 0.5rem;">
        Ferramenta profissional para análise quantitativa de ativos financeiros
    </div>
</div>
""", unsafe_allow_html=True)