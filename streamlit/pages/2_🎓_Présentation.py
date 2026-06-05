import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.snowflake import query

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

# ── Stats chargées une fois ───────────────────────────────────────────────
with st.spinner("Chargement des statistiques..."):
    _s = query("""
        SELECT
            (SELECT COUNT(*) FROM NYC_TAXI_DB.RAW.YELLOW_TAXI_TRIPS)        AS raw_count,
            (SELECT COUNT(*) FROM NYC_TAXI_DB.STAGING.STG_CLEAN_TRIPS)      AS staging_count,
            (SELECT MIN(trip_date) FROM NYC_TAXI_DB.FINAL.DAILY_SUMMARY)    AS date_min,
            (SELECT MAX(trip_date) FROM NYC_TAXI_DB.FINAL.DAILY_SUMMARY)    AS date_max
    """).iloc[0]

    _monthly = query("""
        SELECT
            DATE_TRUNC('month', trip_date)  AS mois,
            SUM(total_trips)                AS nb_lignes
        FROM NYC_TAXI_DB.FINAL.DAILY_SUMMARY
        GROUP BY 1
        ORDER BY 1
    """)

RAW_COUNT     = int(_s["raw_count"])
STAGING_COUNT = int(_s["staging_count"])
REJECTED      = RAW_COUNT - STAGING_COUNT
REJECT_PCT    = REJECTED / RAW_COUNT * 100
DATE_MIN      = _s["date_min"]
DATE_MAX      = _s["date_max"]
PERIODE       = f"{DATE_MIN.strftime('%b %Y')} – {DATE_MAX.strftime('%b %Y')}"
NB_MOIS       = len(_monthly)
_monthly["mois_label"] = pd.to_datetime(_monthly["mois"]).dt.strftime("%Y-%m")


# ── SLIDES ────────────────────────────────────────────────────────────────

def slide_titre():
    st.markdown(f"""
<div class="slide-header">
    <div class="slide-title">🚕 NYC Taxi Data Warehouse</div>
    <div class="slide-subtitle">Simplon — Projet Data Engineering · {PERIODE} · Snowflake · dbt · GitHub Actions</div>
</div>
""", unsafe_allow_html=True)
    st.markdown("Pipeline de données complet sur les **NYC Yellow Taxi Trip Data** — ingestion, nettoyage, transformation, tests qualité et orchestration CI/CD.")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lignes chargées (RAW)",  f"{RAW_COUNT:,}")
    col2.metric("Lignes nettoyées",       f"{STAGING_COUNT:,}")
    col3.metric("Période couverte",       PERIODE)
    col4.metric("Tests qualité",          "20 / 20 ✓")


def slide_contexte():
    st.markdown("""
<div class="slide-header">
    <div class="slide-title">🎯 Contexte & Dataset</div>
</div>
""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Dataset")
        st.markdown(f"""
- **Source :** NYC Taxi & Limousine Commission
- **Format :** fichiers Parquet mensuels
- **Volume :** ~{RAW_COUNT // NB_MOIS / 1e6:.1f}M trajets / mois
- **Période :** {PERIODE} ({NB_MOIS} mois)
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
        st.markdown(f"""**📥 Ingestion (Python)**
```
NYC TLC CloudFront
yellow_tripdata_
{DATE_MIN.strftime('%Y-%m')}.parquet
...
{DATE_MAX.strftime('%Y-%m')}.parquet
        ↓
 ParquetDownloader
        ↓
 SnowflakeStageLoader
   PUT → stage
   COPY INTO
        ↓
RAW.yellow_taxi_trips
  ({RAW_COUNT / 1e6:.0f}M lignes)
```""")
    with col2:
        st.markdown("<div class='arrow'>→</div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""**⚙️ Transformation (dbt)**
```
RAW.yellow_taxi_trips
        ↓
  stg_clean_trips (view)
  - Filtres qualité
  - miles → km
  - BIGINT → TIMESTAMP
  - Colonnes enrichies
        ↓
STAGING ({STAGING_COUNT / 1e6:.1f}M lignes)
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
        st.markdown("- CI : push `main` → dbt run+test\n- Cron : 1er du mois → pipeline complet\n- Auth via GitHub Secrets\n- Node.js 24 (v6)")


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
        st.markdown("#### Résultats par mois")
        df_display = _monthly[["mois_label", "nb_lignes"]].copy()
        df_display.columns = ["Mois", "Lignes"]
        df_display["Lignes"] = df_display["Lignes"].apply(lambda x: f"{int(x):,}")
        st.dataframe(df_display, use_container_width=True, hide_index=True, height=300)
        st.metric("Total RAW", f"{RAW_COUNT:,} lignes")
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
    -- pickup_datetime >= 2024-01-01
),
enriched as (
    -- miles → km  (× 1.60934)
    -- mph  → km/h (× 1.60934)
    -- Dimensions temporelles
    -- distance_category, time_of_day
    -- tip_rate_pct
),
speed_filtered as (
    -- avg_speed_kmh <= 150
)
select * from speed_filtered
""", language="sql")
    with col2:
        st.markdown("#### Résultat du filtrage")
        col_a, col_b = st.columns(2)
        col_a.metric("Avant filtrage", f"{RAW_COUNT:,}")
        col_b.metric("Après filtrage", f"{STAGING_COUNT:,}")
        st.metric("Lignes exclues", f"{REJECTED:,}", delta=f"-{REJECT_PCT:.1f} %", delta_color="inverse")
        st.markdown("#### Tables FINAL")
        st.markdown("""
| Modèle | Clé | Métriques |
|---|---|---|
| `daily_summary` | `trip_date` | trips, km, revenue, speed |
| `zone_analysis` | `pickup_location_id` | trips, fare, tip_rate |
| `hourly_patterns` | `hour + dow + period` | trips, speed, fare |
""")


def slide_dbt_source_ref():
    st.markdown("""
<div class="slide-header">
    <div class="slide-title">🔗 source() et ref() — les deux macros fondamentales</div>
    <div class="slide-subtitle">Comment dbt sait où lire les données et construit le graphe de dépendances</div>
</div>
""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### `{{ source() }}` — lire une source externe")
        st.code("""\
-- models/staging/_sources.yml
sources:
  - name: raw
    database: NYC_TAXI_DB
    schema: RAW
    tables:
      - name: yellow_taxi_trips

-- models/staging/stg_clean_trips.sql
select * from {{ source('raw', 'yellow_taxi_trips') }}
-- ↑ dbt résout → NYC_TAXI_DB.RAW.YELLOW_TAXI_TRIPS
""", language="yaml")
        st.markdown("""
**Pourquoi déclarer les sources ?**
- dbt peut tester leur fraîcheur (`dbt source freshness`)
- Les sources apparaissent dans le graphe de lineage
- Changement de schéma = 1 seul fichier à modifier
        """)
    with col2:
        st.markdown("#### `{{ ref() }}` — référencer un modèle dbt")
        st.code("""\
-- models/final/daily_summary.sql
select * from {{ ref('stg_clean_trips') }}
-- ↑ dbt résout → NYC_TAXI_DB.STAGING.STG_CLEAN_TRIPS

-- models/final/zone_analysis.sql
select * from {{ ref('stg_clean_trips') }}

-- models/final/hourly_patterns.sql
select * from {{ ref('stg_clean_trips') }}
""", language="sql")
        st.markdown("""
**Pourquoi `ref()` plutôt qu'un nom en dur ?**
- dbt construit automatiquement le **DAG de dépendances**
- Si `stg_clean_trips` change → les 3 tables FINAL sont reconstruites dans le bon ordre
- Fonctionne dans tous les environnements (dev, prod) sans changer le code
        """)
    st.info("**Règle dbt :** `source()` pour lire des données externes (RAW), `ref()` pour lire un autre modèle dbt. Ne jamais écrire un nom de table en dur.")


def slide_dbt_materialisations():
    st.markdown("""
<div class="slide-header">
    <div class="slide-title">🧱 Matérialisations dbt</div>
    <div class="slide-subtitle">Que stocke-t-on dans Snowflake — et pourquoi ?</div>
</div>
""", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("#### 👁️ view")
        st.markdown("""
**Ce que c'est :**
SQL stocké, données calculées à chaque requête.

**Notre usage :**
`stg_clean_trips`

**Avantages :**
- 0 stockage supplémentaire
- Toujours à jour
- Pas de coût d'écriture

**Inconvénient :**
- Recalculé à chaque fois → lent sur 90M lignes si requêté directement
        """)
    with col2:
        st.markdown("#### 📦 table")
        st.markdown("""
**Ce que c'est :**
Données calculées et stockées physiquement.

**Notre usage :**
`daily_summary`, `zone_analysis`, `hourly_patterns`

**Avantages :**
- Requêtes rapides (données pré-calculées)
- Idéal pour les dashboards

**Inconvénient :**
- Stockage supplémentaire
- Doit être recalculé (`dbt run`)
        """)
    with col3:
        st.markdown("#### ⚡ incremental")
        st.markdown("""
**Ce que c'est :**
Table qui s'enrichit à chaque run — n'insère que les nouvelles lignes.

**Usage type :**
Tables de faits volumineuses (logs, events)

**Avantages :**
- Beaucoup plus rapide que de tout recalculer
- Économique en compute Snowflake

**Inconvénient :**
- Logique de déduplication à gérer
        """)
    with col4:
        st.markdown("#### 🔮 ephemeral")
        st.markdown("""
**Ce que c'est :**
Jamais stocké — injecté comme CTE dans les modèles qui en dépendent.

**Usage type :**
Transformations intermédiaires légères

**Avantages :**
- Aucun objet créé dans Snowflake
- Simplifie les dépendances

**Inconvénient :**
- Pas interrogeable directement
- N'apparaît pas dans Snowflake
        """)

    st.divider()
    st.markdown("#### Notre choix dans `dbt_project.yml`")
    st.code("""\
models:
  nyc_taxi_dbt:
    staging:
      +materialized: view    # Pas de copie des données — RAW suffit
      +schema: STAGING
    final:
      +materialized: table   # Agrégations pré-calculées pour le dashboard
      +schema: FINAL
""", language="yaml")
    st.success("**Règle simple :** `view` tant que les données source existent déjà. `table` quand on agrège / quand la performance compte.")


def slide_dbt_lineage():
    st.markdown("""
<div class="slide-header">
    <div class="slide-title">🗺️ Lineage — le graphe de dépendances dbt</div>
    <div class="slide-subtitle">Comment dbt détermine l'ordre d'exécution automatiquement</div>
</div>
""", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("#### Notre DAG")
        st.code("""\
[SOURCE]
NYC_TAXI_DB.RAW.yellow_taxi_trips
            │
            │  {{ source('raw', 'yellow_taxi_trips') }}
            ▼
[STAGING — VIEW]
stg_clean_trips
     ├──────────────────────────────────┐
     │  {{ ref('stg_clean_trips') }}    │  {{ ref('stg_clean_trips') }}
     ▼                                  ▼
[FINAL — TABLE]              [FINAL — TABLE]
daily_summary                zone_analysis
                                  │
                     {{ ref('stg_clean_trips') }}
                                  ▼
                         [FINAL — TABLE]
                         hourly_patterns
""")
        st.markdown("""
dbt lit les `{{ ref() }}` dans chaque fichier SQL et construit ce graphe automatiquement.
Il exécute les modèles **dans l'ordre topologique** : source → staging → final.
        """)
    with col2:
        st.markdown("#### Commandes utiles")
        st.code("""\
# Tout reconstruire
dbt run

# Reconstruire un modèle + ses dépendances amont
dbt run --select +daily_summary
# ↑ reconstruit stg_clean_trips ET daily_summary

# Reconstruire un modèle + tout l'aval
dbt run --select stg_clean_trips+
# ↑ reconstruit les 3 tables FINAL

# Tester uniquement un modèle
dbt test --select stg_clean_trips
""", language="bash")
        st.markdown("#### Pourquoi c'est puissant")
        st.markdown("""
Si on modifie le filtre dans `stg_clean_trips` :
1. dbt sait que `daily_summary`, `zone_analysis` et `hourly_patterns` en dépendent
2. Il les reconstruit **automatiquement dans le bon ordre**
3. Aucun script d'orchestration manuel à écrire
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
select pickup_datetime,
       trip_distance_km,
       avg_speed_kmh
from {{ ref('stg_clean_trips') }}
where avg_speed_kmh > 150
-- 0 ligne = succès ✓
""", language="sql")
        st.success("**Résultat :** outliers détectés → filtre ajouté → 0 ligne au re-test")
        st.markdown(f"""
> Taux de filtrage total : **{REJECT_PCT:.1f} %** ({REJECTED:,} lignes)
> dont outliers vitesse : **≤ 0.01 %** du total RAW.
""")


def slide_cicd():
    st.markdown("""
<div class="slide-header">
    <div class="slide-title">⚙️ CI/CD — GitHub Actions</div>
</div>
""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Deux workflows")
        st.markdown("""
**`dbt_ci.yml` — déclenché sur push**
- Vérifie que les modèles tournent toujours
- `dbt run` + `dbt test` (20 tests)

**`pipeline_monthly.yml` — cron + manuel**
- Le 1er de chaque mois à 6h UTC
- Ingestion du mois précédent (Python)
- `dbt run` + `dbt test` en cascade
- `workflow_dispatch` pour lancer manuellement
""")
        st.code("""\
schedule:
  - cron: "0 6 1 * *"
workflow_dispatch:
  inputs:
    start_year, start_month
    end_year,   end_month
""", language="yaml")
    with col2:
        st.success("✓ dbt-run-test in ~50s\n\n✓ 4 models success\n\n✓ 20 tests success")
        st.markdown("#### Secrets GitHub (6)")
        st.markdown("""
```
SNOWFLAKE_ACCOUNT · SNOWFLAKE_USER
SNOWFLAKE_ROLE    · SNOWFLAKE_DATABASE
SNOWFLAKE_WAREHOUSE · SNOWFLAKE_PRIVATE_KEY
```
**Auth :** clé RSA écrite dans un fichier temporaire — aucun mot de passe en clair.
""")


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
- `.github/workflows/` — CI/CD (2 workflows)
- `streamlit/` — rapport + présentation
- `docs/` — documentation markdown par étape
        """)
    with col2:
        st.markdown("""**Structure du projet :**
```
dbt-snowflake-nyc-taxi/
├── ingestion/
│   ├── config.py · downloader.py
│   ├── loader.py · pipeline.py
│   └── protocols.py
├── nyc_taxi_dbt/
│   ├── models/staging/ · models/final/
│   ├── macros/ · tests/
│   └── profiles.yml
├── streamlit/
├── docs/
└── .github/workflows/
```
        """)
    st.success(f"Pipeline opérationnelle ✅ | {RAW_COUNT:,} lignes ingérées ✅ | 20 tests qualité ✅ | CI/CD ✅")


# ── REGISTRE ──────────────────────────────────────────────────────────────
SLIDES = [
    ("🚕 Titre",               slide_titre),
    ("🎯 Contexte & Dataset",  slide_contexte),
    ("🏗️ Architecture",        slide_architecture),
    ("🛠️ Stack technique",     slide_stack),
    ("📥 Ingestion",           slide_ingestion),
    ("🔧 Transformations dbt",        slide_dbt),
    ("🔗 source() et ref()",          slide_dbt_source_ref),
    ("🧱 Matérialisations",           slide_dbt_materialisations),
    ("🗺️ Lineage & DAG",              slide_dbt_lineage),
    ("✅ Tests qualité",              slide_tests),
    ("⚙️ CI/CD",               slide_cicd),
    ("📦 Livrables",           slide_livrables),
]
N = len(SLIDES)

if "slide_idx" not in st.session_state:
    st.session_state.slide_idx = 0

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
