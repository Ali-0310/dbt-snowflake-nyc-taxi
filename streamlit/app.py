import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.snowflake import query

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

with st.spinner("Chargement des métriques..."):
    stats = query("""
        SELECT
            (SELECT COUNT(*) FROM NYC_TAXI_DB.RAW.YELLOW_TAXI_TRIPS)        AS raw_count,
            (SELECT COUNT(*) FROM NYC_TAXI_DB.STAGING.STG_CLEAN_TRIPS)      AS staging_count,
            (SELECT MIN(trip_date) FROM NYC_TAXI_DB.FINAL.DAILY_SUMMARY)    AS date_min,
            (SELECT MAX(trip_date) FROM NYC_TAXI_DB.FINAL.DAILY_SUMMARY)    AS date_max
    """).iloc[0]

raw_count     = int(stats["raw_count"])
staging_count = int(stats["staging_count"])
rejected      = raw_count - staging_count
reject_pct    = rejected / raw_count * 100
periode       = f"{stats['date_min'].strftime('%b %Y')} – {stats['date_max'].strftime('%b %Y')}"

st.markdown(f"""
<div class="home-card">
    <div class="home-title">🚕 NYC Taxi Data Warehouse</div>
    <div class="home-sub">Pipeline complet · Snowflake · dbt-fusion · GitHub Actions · {periode}</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Lignes ingérées (RAW)",      f"{raw_count:,}")
col2.metric("Lignes nettoyées (STAGING)", f"{staging_count:,}")
col3.metric("Taux de rejet",              f"{reject_pct:.1f} %")
col4.metric("Période",                    periode)

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
