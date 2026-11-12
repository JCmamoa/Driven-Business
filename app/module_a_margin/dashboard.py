import streamlit as st
from app.module_a_margin.etl import load_product_history, compute_margin, flag_high_risk
from app.module_a_margin.simulator import simulate_scenario

st.set_page_config(page_title="Margin Simulator", layout="wide")
st.title("Simulador de Margem — E-commerce")

df = compute_margin(load_product_history())

col1, col2 = st.columns(2)
with col1:
    return_red = st.slider("Redução da taxa de devolução (%)", 0, 60, 20)
with col2:
    order_scale = st.slider("Escala de pedidos (%)", -20, 100, 15)

result = simulate_scenario(df, return_red, order_scale)

st.metric("Lucro líquido médio (R$)", f"{result['mean_net_profit']:,.2f}")
st.metric("P10 (cenário pessimista)", f"{result['p10_net_profit']:,.2f}")
st.metric("P90 (cenário otimista)", f"{result['p90_net_profit']:,.2f}")
st.metric("Taxa de devolução simulada", f"{result['simulated_return_rate']:.2%}")

st.subheader("SKUs de alto risco de devolução")
st.dataframe(flag_high_risk(df), use_container_width=True)