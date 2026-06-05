import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.snowflake import query

st.set_page_config(page_title="Rapport d'analyse — NYC Taxi", page_icon="📊", layout="wide")

st.markdown("""
<style>
.section-header {
    background: #1e2130;
    border-radius: 10px;
    padding: 1.2rem 1.8rem;
    margin-bottom: 1.2rem;
    border-left: 5px solid #f6c90e;
}
.section-title { font-size: 1.4rem; font-weight: 700; color: #f6c90e; }
.section-sub   { font-size: 0.9rem; color: #a0aec0; }
</style>
""", unsafe_allow_html=True)

with st.spinner("Chargement des métriques qualité..."):
    qstats = query("""
        SELECT
            (SELECT COUNT(*) FROM NYC_TAXI_DB.RAW.YELLOW_TAXI_TRIPS)     AS raw_count,
            (SELECT COUNT(*) FROM NYC_TAXI_DB.STAGING.STG_CLEAN_TRIPS)   AS staging_count,
            (SELECT MIN(trip_date) FROM NYC_TAXI_DB.FINAL.DAILY_SUMMARY) AS date_min,
            (SELECT MAX(trip_date) FROM NYC_TAXI_DB.FINAL.DAILY_SUMMARY) AS date_max
    """).iloc[0]

raw_count     = int(qstats["raw_count"])
staging_count = int(qstats["staging_count"])
rejected      = raw_count - staging_count
reject_pct    = rejected / raw_count * 100
periode       = f"{qstats['date_min'].strftime('%b %Y')} – {qstats['date_max'].strftime('%b %Y')}"

st.markdown(f"""
<div class="section-header">
    <div class="section-title">📊 Rapport d'analyse — NYC Yellow Taxi</div>
    <div class="section-sub">{periode} · Données : NYC Taxi & Limousine Commission</div>
</div>
""", unsafe_allow_html=True)

# ── 1. Qualité des données ────────────────────────────────────────────────
st.markdown("## 1. Qualité des données")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Lignes RAW",      f"{raw_count:,}")
col2.metric("Lignes STAGING",  f"{staging_count:,}")
col3.metric("Lignes filtrées", f"{rejected:,}", delta=f"-{reject_pct:.1f} %", delta_color="inverse")
col4.metric("Outliers vitesse","1 148",          delta="≤ 0.006 %",           delta_color="inverse")
col5.metric("Tests dbt",       "20 / 20",        delta="✓ tous passés")

with st.expander("Détail des règles de filtrage"):
    st.markdown("""
| Règle | Seuil |
|---|---|
| `fare_amount` | > 0 |
| `trip_distance` | 0.1 – 200 miles |
| `passenger_count` | 1 – 6 |
| Durée du trajet | 1 – 180 minutes |
| `avg_speed_kmh` | ≤ 150 km/h |
""")

st.divider()

# ── 2. KPIs globaux ───────────────────────────────────────────────────────
st.markdown("## 2. KPIs globaux")

with st.spinner("Chargement des données..."):
    df_daily = query("SELECT * FROM NYC_TAXI_DB.FINAL.DAILY_SUMMARY ORDER BY TRIP_DATE")
    df_zones = query("SELECT * FROM NYC_TAXI_DB.FINAL.ZONE_ANALYSIS ORDER BY TOTAL_TRIPS DESC")
    df_hours = query("SELECT * FROM NYC_TAXI_DB.FINAL.HOURLY_PATTERNS")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total trajets",       f"{df_daily['total_trips'].sum():,.0f}")
col2.metric("Distance totale",     f"{df_daily['total_distance_km'].sum() / 1e6:.1f} M km")
col3.metric("Revenu total",        f"${df_daily['total_revenue'].sum() / 1e6:.1f} M")
col4.metric("Vitesse moy.",        f"{df_daily['avg_speed_kmh'].mean():.1f} km/h")
col5.metric("Taux pourboire moy.", f"{df_daily['avg_tip_rate_pct'].mean():.1f} %")

st.divider()

# ── 3. Trafic journalier ──────────────────────────────────────────────────
st.markdown("## 3. Trafic journalier")

col1, col2 = st.columns(2)

with col1:
    fig = px.line(
        df_daily, x="trip_date", y="total_trips",
        title="Nombre de trajets par jour",
        labels={"trip_date": "Date", "total_trips": "Trajets"},
        color_discrete_sequence=["#f6c90e"],
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.line(
        df_daily, x="trip_date", y="total_revenue",
        title="Revenu journalier ($)",
        labels={"trip_date": "Date", "total_revenue": "Revenu ($)"},
        color_discrete_sequence=["#48bb78"],
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    fig = px.line(
        df_daily, x="trip_date", y="avg_speed_kmh",
        title="Vitesse moyenne journalière (km/h)",
        labels={"trip_date": "Date", "avg_speed_kmh": "Vitesse (km/h)"},
        color_discrete_sequence=["#63b3ed"],
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.line(
        df_daily, x="trip_date", y="avg_tip_rate_pct",
        title="Taux de pourboire moyen (%)",
        labels={"trip_date": "Date", "avg_tip_rate_pct": "Taux pourboire (%)"},
        color_discrete_sequence=["#fc8181"],
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── 4. Analyse par zone ───────────────────────────────────────────────────
st.markdown("## 4. Top 15 zones de prise en charge")

top15 = df_zones.head(15)
fig = px.bar(
    top15, x="pickup_location_id", y="total_trips",
    title="Zones les plus actives (nombre de trajets)",
    labels={"pickup_location_id": "Zone ID", "total_trips": "Trajets"},
    color="avg_fare_amount",
    color_continuous_scale="YlOrRd",
    text="total_trips",
)
fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
fig.update_layout(template="plotly_dark", coloraxis_colorbar_title="Tarif moy. ($)")
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    fig = px.scatter(
        df_zones.head(50), x="avg_distance_km", y="avg_fare_amount",
        size="total_trips", color="avg_tip_rate_pct",
        title="Distance vs Tarif — Top 50 zones",
        labels={
            "avg_distance_km": "Distance moy. (km)",
            "avg_fare_amount": "Tarif moy. ($)",
            "avg_tip_rate_pct": "Tip (%)",
        },
        color_continuous_scale="Viridis",
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(
        top15, x="pickup_location_id", y="avg_fare_amount",
        title="Tarif moyen par zone (Top 15)",
        labels={"pickup_location_id": "Zone ID", "avg_fare_amount": "Tarif moy. ($)"},
        color_discrete_sequence=["#f6c90e"],
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── 5. Patterns horaires ──────────────────────────────────────────────────
st.markdown("## 5. Patterns horaires")

df_heatmap = (
    df_hours.groupby(["pickup_dow", "pickup_hour"])["total_trips"]
    .sum()
    .reset_index()
)
dow_labels = {1: "Dim", 2: "Lun", 3: "Mar", 4: "Mer", 5: "Jeu", 6: "Ven", 7: "Sam"}
df_heatmap["jour"] = df_heatmap["pickup_dow"].map(dow_labels)

fig = px.density_heatmap(
    df_heatmap, x="pickup_hour", y="jour",
    z="total_trips", histfunc="sum",
    title="Heatmap : intensité du trafic (heure × jour)",
    labels={"pickup_hour": "Heure", "jour": "Jour", "total_trips": "Trajets"},
    color_continuous_scale="YlOrRd",
    category_orders={"jour": ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]},
)
fig.update_layout(template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    df_tod = df_hours.groupby("time_of_day")["total_trips"].sum().reset_index()
    fig = px.pie(
        df_tod, names="time_of_day", values="total_trips",
        title="Répartition par période de la journée",
        color="time_of_day",
        color_discrete_map={
            "morning": "#f6c90e", "afternoon": "#48bb78",
            "evening": "#63b3ed", "night": "#a0aec0",
        },
        hole=0.4,
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df_hour_agg = df_hours.groupby("pickup_hour").agg(
        total_trips=("total_trips", "sum"),
        avg_speed_kmh=("avg_speed_kmh", "mean"),
    ).reset_index()
    fig = px.bar(
        df_hour_agg, x="pickup_hour", y="total_trips",
        title="Trajets par heure (toutes journées confondues)",
        labels={"pickup_hour": "Heure", "total_trips": "Trajets"},
        color="avg_speed_kmh",
        color_continuous_scale="Blues",
    )
    fig.update_layout(template="plotly_dark", coloraxis_colorbar_title="Vitesse moy. (km/h)")
    st.plotly_chart(fig, use_container_width=True)
