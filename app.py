import streamlit as st
import pandas as pd

st.set_page_config(page_title="Monitoramento Solar", layout="wide")
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

# SOC inicial e final (agora como inteiro)
soc_first = df.groupby('Date')['SOC(%)'].first().reset_index(name="SOC Inicial (%)")
soc_last = df.groupby('Date')['SOC(%)'].last().reset_index(name="SOC Final (%)")

# Merge final
daily_data = daily_data.merge(peak_load, on="Date")
daily_data = daily_data.merge(soc_first, on="Date")
daily_data = daily_data.merge(soc_last, on="Date")

# ---------------------------
# Função para card estilizado
# ---------------------------
def metric_card(label, value, unit="", color="#262730"):
    return f"""
    <div style="
        background-color:{color};
        padding:20px;
        border-radius:15px;
        text-align:center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        color:white;
        font-size:20px;
        font-weight:bold;
        ">
        {label}<br>
        <span style="font-size:28px;">{value} {unit}</span>
    </div>
    """

# ---------------------------
# Mostrar indicadores
# ---------------------------
st.subheader("📊 Indicadores de Hoje")

# Mostrar apenas o último dia disponível
row = daily_data.iloc[-1]  # pega o último dia

col1, col2, col3 = st.columns(3)

# cor condicional para variação
var_color = "#2ecc71" if row['Variação Energia (kWh)'] >= 0 else "#e74c3c"

with col1:
    st.markdown(metric_card("🔋 Variação de Energia", f"{row['Variação Energia (kWh)']:.2f}", "kWh", var_color), unsafe_allow_html=True)

with col2:
    st.markdown(metric_card("⚡ Pico de Potência", f"{row['Pico Potência (W)']:.0f}", "W", "#3498db"), unsafe_allow_html=True)

with col3:
    st.markdown(metric_card("🔄 SOC Bateria", f"{int(row['SOC Inicial (%)'])}% → {int(row['SOC Final (%)'])}%", "", "#9b59b6"), unsafe_allow_html=True)

st.markdown("---")

# ---------------------------
# Tabela resumida
# ---------------------------
st.subheader("📑 Resumo Completo")
st.dataframe(
    daily_data[['Date','PV(kWh)','Load(kWh)','Battery(kWh)','Grid(kWh)',
                'Variação Energia (kWh)','Pico Potência (W)','SOC Inicial (%)','SOC Final (%)']]
)
