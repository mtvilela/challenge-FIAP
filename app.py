import streamlit as st
import pandas as pd
import random
from gerador_texto_ia import RIA

st.set_page_config(page_title="Monitoramento Solar", layout="wide")

# ---------------------------
# Título com imagem ao lado
# ---------------------------
col1, col2 = st.columns([0.07, 0.93])
with col1:
    st.image("ibagem.png", width=107)
with col2:
    st.markdown("<h1 style='margin-bottom:0;'>SunGuard</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='margin-top:0;'>⚡ Monitoramento Solar com Baterias e Consumo da Casa</h2>", unsafe_allow_html=True)

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

daily_data['Variação Energia (kWh)'] = daily_data['PV(kWh)'] - daily_data['Load(kWh)']

peak_load = df.groupby('Date')['Load(W)'].max().reset_index(name="Pico Potência (W)")
soc_first = df.groupby('Date')['SOC(%)'].first().reset_index(name="SOC Inicial (%)")
soc_last = df.groupby('Date')['SOC(%)'].last().reset_index(name="SOC Final (%)")

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
# Indicadores de hoje
# ---------------------------
st.subheader("📊 Indicadores de Hoje")
row = daily_data.iloc[-1]

col1, col2, col3 = st.columns(3)
var_color = "#2ecc71" if row['Variação Energia (kWh)'] >= 0 else "#e74c3c"

with col1:
    st.markdown(metric_card("🔋 Variação de Energia", f"{row['Variação Energia (kWh)']:.2f}", "kWh", var_color), unsafe_allow_html=True)
with col2:
    st.markdown(metric_card("⚡ Pico de Potência", f"{row['Pico Potência (W)']:.0f}", "W", "#3498db"), unsafe_allow_html=True)
with col3:
    st.markdown(metric_card("🔄 SOC Bateria", f"{int(row['SOC Inicial (%)'])}% → {int(row['SOC Final (%)'])}%", "", "#9b59b6"), unsafe_allow_html=True)

# ---------------------------
# Consumo atual (fixo)
# ---------------------------
st.markdown("### ⚡ Consumo Instantâneo da Casa")

if "consumo_atual" not in st.session_state:
    st.session_state["consumo_atual"] = random.randint(100, 700)

consumo_atual = st.session_state["consumo_atual"]
st.markdown(metric_card("🏠 Consumo Atual", f"{consumo_atual}", "W", "#e67e22", big=True), unsafe_allow_html=True)

# ---------------------------
# Ajudante inteligente
# ---------------------------
st.markdown("### 🤖 Ajudante de Consumo")
limite_alerta = 500

if consumo_atual > limite_alerta:
    st.error(f"🚨 Consumo atual está alto: {consumo_atual}W")
    st.markdown("""
    **Sugestões para reduzir o consumo:**
    - Utilize o assistente virtual para desligar luzes que não estão em uso
    - Desligue aparelhos que não estão em uso.
    - Prefira usar eletrodomésticos no horário de maior produção solar.
    - Evite ligar chuveiro elétrico, ferro de passar ou micro-ondas simultaneamente.
    """)
else:
    st.success(f"✅ Consumo atual ({consumo_atual}W)")
    st.markdown("Continue aproveitando bem a energia disponível! 🌞🔋")

# ---------------------------
# Botões ilustrativos de cômodos
# ---------------------------
st.markdown("### 💡 Controle de Luzes por Cômodo (Ilustrativo)")

# Inicializa estado
for room in ["Quarto", "Sala", "Cozinha"]:
    if f"{room}_ligada" not in st.session_state:
        st.session_state[f"{room}_ligada"] = False

def toggle_light(room):
    st.session_state[f"{room}_ligada"] = not st.session_state[f"{room}_ligada"]

cols = st.columns(3)
for i, room in enumerate(["Quarto", "Sala", "Cozinha"]):
    with cols[i]:
        if st.button(room, key=room):
            toggle_light(room)
        estado = "🟢" if st.session_state[f"{room}_ligada"] else "⚪"
        st.markdown(f"Estado: {estado}")
