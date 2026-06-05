import streamlit as st

st.set_page_config(page_title="Présentation — NYC Taxi Pipeline", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.slide-header {
    background: #1e2130;
    border-radius: 12px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    border-left: 5px solid #f6c90e;
}
.slide-title    { font-size: 1.8rem; font-weight: 700; color: #f6c90e; margin-bottom: 0.4rem; }
.slide-subtitle { font-size: 1rem; color: #a0aec0; }
.arrow          { font-size: 1.4rem; color: #f6c90e; text-align: center; }
</style>
""", unsafe_allow_html=True)


# ── SLIDES ────────────────────────────────────────────────────────────────

def slide_titre():
    st.markdown("""
<div class="slide-header">
    <div class="slide-title">🚕 NYC Taxi Data Warehouse</div>
    <div class="slide-subtitle">Simplon — Projet Data Engineering · 2025 · Snowflake · dbt · GitHub Actions</div>
</div>
""", unsafe_allow_html=True)
    st.markdown("Pipeline de données complet sur les **NYC Yellow Taxi Trip Data** — ingestion, nettoyage, transformation, tests qualité et orchestration CI/CD.")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lignes chargées",  "24 083 384")
    col2.metric("Lignes nettoyées", "20 445 700")
    col3.metric("Mois de données",  "6 (Jan–Jun 2025)")
    col4.metric("Tests qualité",    "20 / 20 ✓")


def slide_contexte():
    st.markdown("""
<div class="slide-header">
    <div class="slide-title">🎯 Contexte & Dataset</div>
</div>
""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Dataset")
        st.markdown("""
- **Source :** NYC Taxi & Limousine Commission
- **Format :** fichiers Parquet mensuels
- **Volume :** ~4M trajets / mois
- **Période :** Jan – Jun 2025
- **Colonnes :** 20 (tarifs, distances, zones, timestamps...)
- **Nouveauté 2025 :** colonne `cbd_congestion_fee` (taxe MTA)
        """)
    with col2:
        st.markdown("#### Objectifs pédagogiques")
        st.markdown("""
- ✅ Ingestion automatisée depuis une source externe
- ✅ Architecture **RAW → STAGING → FINAL**
- ✅ Transformations et tests avec **dbt-fusion**
- ✅ Authentification sécurisée (**Key Pair RSA**)
- ✅ Pipeline CI/CD avec **GitHub Actions**
- ✅ Visualisation avec **Streamlit**
        """)


def slide_architecture():
    st.markdown("""
<div class="slide-header">
    <div class="slide-title">🏗️ Architecture du pipeline</div>
</div>
""", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns([2, 0.4, 2, 0.4, 2])
    with col1:
        st.markdown("""**📥 Ingestion (Python)**
```
NYC TLC CloudFront
yellow_tripdata_
2025-01.parquet
2025-02.parquet
        ↓
 ParquetDownloader
        ↓
 SnowflakeStageLoader
   PUT → stage
   COPY INTO
        ↓
RAW.yellow_taxi_trips
  (24M lignes)
```""")
    with col2:
        st.markdown("<div class='arrow'>→</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("""**⚙️ Transformation (dbt)**
```
RAW.yellow_taxi_trips
        ↓
  stg_clean_trips (view)
  - Filtres qualité
  - miles → km
  - BIGINT → TIMESTAMP
  - Colonnes enrichies
        ↓
STAGING (20.4M lignes)
```""")
    with col4:
        st.markdown("<div class='arrow'>→</div>", unsafe_allow_html=True)
    with col5:
        st.markdown("""**📊 Analytique (dbt)**
```
  stg_clean_trips
        ↓
  daily_summary
  zone_analysis
  hourly_patterns
        ↓
FINAL (tables)
  prêtes pour
  le reporting
```""")
    st.info("Le pipeline est orchestré automatiquement via **GitHub Actions** à chaque push sur `main`.")


def slide_stack():
    st.markdown("""
<div class="slide-header">
    <div class="slide-title">🛠️ Stack technique</div>
</div>
""", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("#### ❄️ Snowflake")
        st.markdown("- Warehouse `X-SMALL`\n- `AUTO_SUSPEND = 60s`\n- 3 schémas : RAW / STAGING / FINAL\n- Auth RSA Key Pair\n- Internal stage (PUT/COPY)")
    with col2:
        st.markdown("#### 🔧 dbt-fusion")
        st.markdown("- Version `2.0.0-preview`\n- 4 modèles\n- 20 tests qualité\n- Macro `generate_schema_name`\n- Vue STAGING + Tables FINAL")
    with col3:
        st.markdown("#### 🐍 Python / uv")
        st.markdown("- Python 3.10\n- `uv` gestionnaire packages\n- Design OOP/SOLID\n- `snowflake-connector-python`\n- `requests`, `cryptography`")
    with col4:
        st.markdown("#### ⚙️ GitHub Actions")
        st.markdown("- Trigger : push sur `main`\n- `dbt run` + `dbt test`\n- Auth via GitHub Secrets\n- Durée : ~50s\n- Node.js 24 (v6)")


def slide_ingestion():
    st.markdown("""
<div class="slide-header">
    <div class="slide-title">📥 Pipeline d'ingestion</div>
    <div class="slide-subtitle">Design OOP / SOLID — 3 classes, 1 orchestrateur</div>
</div>
""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Design des classes")
        st.code("""\
# Interfaces (DIP)
class FileDownloaderProtocol(Protocol):
    def download(self, year, month) -> Path: ...

class DataLoaderProtocol(Protocol):
    def setup_table(self) -> None: ...
    def load(self, file_path: Path) -> int: ...

# Implémentations
class ParquetDownloader:        # SRP : téléchargement HTTP
class SnowflakeStageLoader:     # SRP : PUT + COPY INTO
class IngestionPipeline:        # SRP : orchestration
    def __init__(
        self,
        downloader: FileDownloaderProtocol,  # DIP
        loader: DataLoaderProtocol,
    ): ...
""", language="python")
    with col2:
        st.markdown("#### Résultats")
        import pandas as pd
        data = {
            "Mois": ["2025-01","2025-02","2025-03","2025-04","2025-05","2025-06"],
            "Lignes": ["3 475 226","3 577 543","4 145 257","3 970 553","4 591 845","4 322 960"],
            "Taille": ["59 MB","60 MB","70 MB","67 MB","78 MB","74 MB"],
        }
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        st.metric("Total", "24 083 384 lignes en ~4 minutes")
        st.markdown("""
**Point technique :** les timestamps Parquet (`timestamp[us]`) sont stockés en `BIGINT` en RAW
(Snowflake interprète les µsecondes comme des secondes → année 55 000 000 sinon).
Conversion appliquée en STAGING : `TO_TIMESTAMP_NTZ(val / 1000000)`.
        """)


def slide_dbt():
    st.markdown("""
<div class="slide-header">
    <div class="slide-title">🔧 Transformations dbt</div>
    <div class="slide-subtitle">stg_clean_trips — 5 CTEs, vue STAGING</div>
</div>
""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Pipeline SQL (CTEs)")
        st.code("""\
with source as (
    select * from {{ source('raw', 'yellow_taxi_trips') }}
),
converted as (
    -- Timestamps BIGINT → TIMESTAMP_NTZ
    -- Renommage colonnes (snake_case)
),
filtered as (
    -- fare_amount > 0
    -- trip_distance entre 0.1 et 200 miles
    -- passenger_count entre 1 et 6
    -- durée entre 1 et 180 min
),
enriched as (
    -- miles → km  (× 1.60934)
    -- mph  → km/h (× 1.60934)
    -- Dimensions temporelles
    -- distance_category, time_of_day
    -- tip_rate_pct
),
speed_filtered as (
    -- avg_speed_kmh <= 150 (1 148 outliers)
)
select * from speed_filtered
""", language="sql")
    with col2:
        st.markdown("#### Tables FINAL")
        st.markdown("""
| Modèle | Clé | Nb colonnes |
|---|---|---|
| `daily_summary` | `trip_date` | 11 |
| `zone_analysis` | `pickup_location_id` | 10 |
| `hourly_patterns` | `hour + dow + period` | 12 |
""")
        st.markdown("#### Macro `generate_schema_name`")
        st.markdown("""
Par défaut dbt crée `STAGING_STAGING` au lieu de `STAGING`.
Override qui force le nom exact du schéma :
```sql
{%- if custom_schema_name is none -%}
    {{ target.schema }}
{%- else -%}
    {{ custom_schema_name | trim | upper }}
{%- endif -%}
```
""")


def slide_tests():
    st.markdown("""
<div class="slide-header">
    <div class="slide-title">✅ Tests qualité dbt</div>
    <div class="slide-subtitle">20 tests — 20 succès</div>
</div>
""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Tests génériques (`_stg_clean_trips.yml`)")
        st.markdown("""
| Colonne | Tests |
|---|---|
| `vendor_id` | `not_null`, `accepted_values` [1,2,6,7] |
| `pickup_datetime` | `not_null` |
| `dropoff_datetime` | `not_null` |
| `passenger_count` | `not_null` |
| `trip_distance_km` | `not_null` |
| `payment_type` | `not_null`, `accepted_values` [0–6] |
| `time_of_day` | `not_null`, `accepted_values` |
| `distance_category` | `not_null`, `accepted_values` |
| Autres colonnes clés | `not_null` |
""")
    with col2:
        st.markdown("#### Test singulier")
        st.code("""\
-- assert_no_aberrant_speed.sql
-- Retourne les lignes qui violent la règle
-- 0 ligne = succès

select pickup_datetime,
       trip_distance_km,
       avg_speed_kmh
from {{ ref('stg_clean_trips') }}
where avg_speed_kmh > 150
""", language="sql")
        st.success("**Résultat :** 1 148 outliers détectés → filtre ajouté en staging → 0 ligne au re-test")
        st.markdown("""
> Le test a révélé une anomalie non capturée par les filtres initiaux.
> C'est la valeur ajoutée des tests singuliers : détecter les cas limites métier.
""")


def slide_cicd():
    st.markdown("""
<div class="slide-header">
    <div class="slide-title">⚙️ CI/CD — GitHub Actions</div>
</div>
""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Workflow `.github/workflows/dbt_ci.yml`")
        st.code("""\
on:
  push:     { branches: [main] }
  pull_request: { branches: [main] }

jobs:
  dbt-run-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
      - run: pip install dbt-snowflake
      - name: Write RSA key
        run: echo "${{ secrets.SNOWFLAKE_PRIVATE_KEY }}"
             > .secrets/snowflake_key.p8
      - run: dbt run  --project-dir nyc_taxi_dbt
                      --profiles-dir nyc_taxi_dbt
      - run: dbt test --project-dir nyc_taxi_dbt
                      --profiles-dir nyc_taxi_dbt
""", language="yaml")
    with col2:
        st.markdown("#### Résultat")
        st.success("✓ dbt-run-test in 50s\n\n✓ 4 models success\n\n✓ 20 tests success")
        st.markdown("#### Secrets GitHub (6)")
        st.markdown("""
```
SNOWFLAKE_ACCOUNT
SNOWFLAKE_USER
SNOWFLAKE_ROLE
SNOWFLAKE_DATABASE
SNOWFLAKE_WAREHOUSE
SNOWFLAKE_PRIVATE_KEY
```
""")
        st.markdown("**Auth :** clé RSA écrite dans un fichier temporaire à chaque run — aucun mot de passe en clair.")


def slide_livrables():
    st.markdown("""
<div class="slide-header">
    <div class="slide-title">📦 Livrables</div>
</div>
""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""**Fichiers produits :**
- `ingestion/` — pipeline Python OOP/SOLID
- `nyc_taxi_dbt/` — projet dbt (4 modèles, 20 tests)
- `.github/workflows/dbt_ci.yml` — CI/CD automatisé
- `streamlit/` — rapport + présentation
- `docs/` — documentation markdown par étape
        """)
    with col2:
        st.markdown("""**Structure du projet :**
```
dbt-snowflake-nyc-taxi/
├── ingestion/
│   ├── config.py
│   ├── downloader.py
│   ├── loader.py
│   ├── pipeline.py
│   └── protocols.py
├── nyc_taxi_dbt/
│   ├── models/staging/
│   ├── models/final/
│   ├── macros/
│   └── tests/
├── streamlit/
├── docs/
└── .github/workflows/
```
        """)
    st.success("Pipeline opérationnelle ✅ | 24M lignes ingérées ✅ | 20 tests qualité ✅ | CI/CD ✅")


# ── REGISTRE ──────────────────────────────────────────────────────────────
SLIDES = [
    ("🚕 Titre",               slide_titre),
    ("🎯 Contexte & Dataset",  slide_contexte),
    ("🏗️ Architecture",        slide_architecture),
    ("🛠️ Stack technique",     slide_stack),
    ("📥 Ingestion",           slide_ingestion),
    ("🔧 Transformations dbt", slide_dbt),
    ("✅ Tests qualité",       slide_tests),
    ("⚙️ CI/CD",               slide_cicd),
    ("📦 Livrables",           slide_livrables),
]
N = len(SLIDES)

# ── SESSION STATE ─────────────────────────────────────────────────────────
if "slide_idx" not in st.session_state:
    st.session_state.slide_idx = 0

# ── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎓 Présentation")
    mode = st.radio("Mode d'affichage", ["🎞️ Diaporama", "📄 Vue complète"], index=0)
    st.divider()
    if mode == "🎞️ Diaporama":
        st.markdown("**Aller à la slide :**")
        for i, (title, _) in enumerate(SLIDES):
            btn_type = "primary" if i == st.session_state.slide_idx else "secondary"
            if st.button(title, key=f"nav_{i}", use_container_width=True, type=btn_type):
                st.session_state.slide_idx = i
                st.rerun()

# ── RENDU ─────────────────────────────────────────────────────────────────
if mode == "🎞️ Diaporama":
    idx = st.session_state.slide_idx

    col_prev, col_info, col_next = st.columns([1, 3, 1])
    with col_prev:
        if st.button("◀ Précédent", disabled=(idx == 0), use_container_width=True):
            st.session_state.slide_idx -= 1
            st.rerun()
    with col_info:
        st.markdown(
            f"<div style='text-align:center;padding:0.4rem;color:#a0aec0;font-weight:600;'>"
            f"Slide {idx + 1} / {N} — {SLIDES[idx][0]}</div>",
            unsafe_allow_html=True,
        )
        st.progress((idx + 1) / N)
    with col_next:
        if st.button("Suivant ▶", disabled=(idx == N - 1), use_container_width=True):
            st.session_state.slide_idx += 1
            st.rerun()

    st.divider()
    SLIDES[idx][1]()
    st.divider()

    col_prev2, _, col_next2 = st.columns([1, 3, 1])
    with col_prev2:
        if st.button("◀ Précédent ", disabled=(idx == 0), use_container_width=True):
            st.session_state.slide_idx -= 1
            st.rerun()
    with col_next2:
        if st.button(" Suivant ▶", disabled=(idx == N - 1), use_container_width=True):
            st.session_state.slide_idx += 1
            st.rerun()

else:
    for title, render_fn in SLIDES:
        render_fn()
        st.divider()
