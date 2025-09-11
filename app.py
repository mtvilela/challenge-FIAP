import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Monitoramento Solar", layout="wide")

# ---------------------------
# Título com imagem ao lado
# ---------------------------
col1, col2 = st.columns([0.07, 0.93])  # primeira coluna menor
with col1:
    st.image("ibagem.png", width=107)   # imagem pequena
with col2:
    st.title("⚡ Monitoramento Solar com Baterias e Consumo da Casa")

# ---------------------------
# Leitura fixa do Excel
# ---------------------------
df = pd.read_excel("powerplan.xlsx", header=1)

# ---------------------------
# Limpeza e colunas
# ---------------------------
df.columns = df.columns.str.strip()
df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
df['Date'] = df['Time'].dt.date

# ---------------------------
# Resumos por dia
# ---------------------------
daily_data = df.groupby('Date').agg({
    'PV(W)': 'sum',
    'Battery(W)': 'sum',
    'Grid(W)': 'sum',
    'Load(W)': 'sum',
    'SOC(%)': 'mean'
}).reset_index()

daily_data['PV(kWh)'] = daily_data['PV(W)'] / 1000
daily_data['Battery(kWh)'] = daily_data['Battery(W)'] / 1000
daily_data['Grid(kWh)'] = daily_data['Grid(W)'] / 1000
daily_data['Load(kWh)'] = daily_data['Load(W)'] / 1000

# Variação de energia
daily_data['Variação Energia (kWh)'] = daily_data['PV(kWh)'] - daily_data['Load(kWh)']

# Pico de potência
peak_load = df.groupby('Date')['Load(W)'].max().reset_index(name="Pico Potência (W)")

# SOC inicial e final
soc_first = df.groupby('Date')['SOC(%)'].first().reset_index(name="SOC Inicial (%)")
soc_last = df.groupby('Date')['SOC(%)'].last().reset_index(name="SOC Final (%)")

# Merge final
daily_data = daily_data.merge(peak_load, on="Date")
daily_data = daily_data.merge(soc_first, on="Date")
daily_data = daily_data.merge(soc_last, on="Date")

# ---------------------------
# Função para card estilizado
# ---------------------------
def metric_card(label, value, unit="", color="#262730", big=False):
    font_size = "36px" if big else "28px"
    return f"""
    <div style="
        background-color:{color};
        padding:30px;
        border-radius:15px;
        text-align:center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        color:white;
        font-size:20px;
        font-weight:bold;
        ">
        {label}<br>
        <span style="font-size:{font_size};">{value} {unit}</span>
    </div>
    """

# ---------------------------
# Mostrar indicadores
# ---------------------------
st.subheader("📊 Indicadores de Hoje")

# Último dia disponível
row = daily_data.iloc[-1]

col1, col2, col3 = st.columns(3)

# cor condicional para variação
var_color = "#2ecc71" if row['Variação Energia (kWh)'] >= 0 else "#e74c3c"

with col1:
    st.markdown(metric_card("🔋 Variação de Energia", f"{row['Variação Energia (kWh)']:.2f}", "kWh", var_color), unsafe_allow_html=True)

with col2:
    st.markdown(metric_card("⚡ Pico de Potência", f"{row['Pico Potência (W)']:.0f}", "W", "#3498db"), unsafe_allow_html=True)

with col3:
    st.markdown(metric_card("🔄 SOC Bateria", f"{int(row['SOC Inicial (%)'])}% → {int(row['SOC Final (%)'])}%", "", "#9b59b6"), unsafe_allow_html=True)

# ---------------------------
# Novo card - Consumo Atual
# ---------------------------
st.markdown("### ⚡ Consumo Instantâneo da Casa")

# valor aleatório entre 100 e 700 W
consumo_atual = random.randint(100, 700)

st.markdown(metric_card("🏠 Consumo Atual", f"{consumo_atual}", "W", "#e67e22", big=True), unsafe_allow_html=True)

# ---------------------------
# Ajudante inteligente
# ---------------------------
st.markdown("### 🤖 Ajudante de Consumo")

limite_alerta = 500  # limite em Watts para alerta

if consumo_atual > limite_alerta:
    st.error(f"🚨 Consumo atual está alto: {consumo_atual}W (acima de {limite_alerta}W).")
    st.markdown("""
    **Sugestões para reduzir o consumo:**
    - Desligue aparelhos que não estão em uso.
    - Prefira usar eletrodomésticos no horário de maior produção solar.
    - Evite ligar chuveiro elétrico, ferro de passar ou micro-ondas simultaneamente.
    - Se possível, troque lâmpadas por versões LED mais econômicas.
    """)
else:
    st.success(f"✅ Consumo atual ({consumo_atual}W) está dentro do limite de {limite_alerta}W.")
    st.markdown("Continue aproveitando bem a energia disponível! 🌞🔋")
