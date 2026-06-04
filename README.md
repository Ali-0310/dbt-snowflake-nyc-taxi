# NYC Taxi Data Warehouse

Pipeline de données complet sur les NYC Taxi Trip Data (~40M trajets, 2024-2025).

## Architecture

```
RAW → STAGING → FINAL
```

| Couche  | Outil          | Rôle                            |
|---------|----------------|---------------------------------|
| RAW     | Python + SQL   | Ingestion fichiers Parquet      |
| STAGING | dbt            | Nettoyage et enrichissement     |
| FINAL   | dbt            | Tables analytiques et reporting |

## Stack

- **Snowflake** — Data Warehouse
- **dbt-fusion** — Transformations SQL
- **Python / uv** — Ingestion et scripts
- **GitHub Actions** — Orchestration
- **Streamlit** — Rapport et présentation

## Structure

```
├── ingestion/         # Scripts Python (download + load Parquet)
├── nyc_taxi_dbt/      # Projet dbt
├── streamlit/         # Applications Streamlit
├── docs/              # Documentation par étape
└── .github/workflows/ # CI/CD GitHub Actions
```

## Documentation

Voir [docs/](docs/) pour la documentation détaillée de chaque étape.
