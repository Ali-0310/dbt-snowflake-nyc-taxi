import streamlit as st

st.set_page_config(
    page_title="NYC Taxi — Pipeline",
    page_icon="🚕",
    layout="wide",
)

st.markdown("""
<style>
.home-card {
    background: #1e2130;
    border-radius: 12px;
    padding: 2rem;
    border-left: 5px solid #f6c90e;
    margin-bottom: 1rem;
}
.home-title { font-size: 2.2rem; font-weight: 800; color: #f6c90e; }
.home-sub   { font-size: 1rem; color: #a0aec0; margin-top: 0.4rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="home-card">
    <div class="home-title">🚕 NYC Taxi Data Warehouse</div>
    <div class="home-sub">Pipeline complet · Snowflake · dbt-fusion · GitHub Actions · 2025</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Lignes ingérées (RAW)", "24 083 384")
col2.metric("Lignes nettoyées (STAGING)", "20 445 700")
col3.metric("Taux de rejet", "15.1 %")
col4.metric("Période", "Jan – Jun 2025")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 📊 Rapport d'analyse")
    st.markdown("Qualité des données, KPIs calculés et visualisations interactives depuis les tables FINAL Snowflake.")
    st.page_link("pages/1_📊_Rapport.py", label="Ouvrir le rapport →", icon="📊")

with col2:
    st.markdown("### 🎓 Présentation")
    st.markdown("Support de présentation du projet en mode diaporama — architecture, pipeline et résultats.")
    st.page_link("pages/2_🎓_Présentation.py", label="Ouvrir la présentation →", icon="🎓")
