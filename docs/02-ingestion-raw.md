# 02 — Ingestion Parquet → RAW

## Objectif

Télécharger les fichiers Parquet NYC Taxi depuis la source publique et les charger dans `RAW.yellow_taxi_trips` sur Snowflake.

---

## 1. Architecture du pipeline

```
URL CloudFront          Local (tmp)           Snowflake
yellow_tripdata_        ──────────────────    ─────────────────────────────
2025-01.parquet  ──→   /tmp/xxx/*.parquet  → @RAW.nyc_taxi_stage (PUT)
2025-02.parquet                            → RAW.yellow_taxi_trips (COPY INTO)
...
```

**Mécanisme Snowflake :**
- **Stage interne** (`@RAW.nyc_taxi_stage`) : espace de stockage temporaire géré par Snowflake, équivalent d'un bucket S3 privé
- **PUT** : upload du fichier local vers le stage via le connecteur Python
- **COPY INTO** : chargement du stage vers la table avec `MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE`
- Le fichier est supprimé du stage après chaque chargement (`REMOVE`)

---

## 2. Design OOP / SOLID

```
ingestion/
├── protocols.py    # Interfaces Protocol (DIP — dépendance vers abstractions)
├── config.py       # SnowflakeConfig — lecture .env (SRP)
├── downloader.py   # ParquetDownloader — téléchargement HTTP (SRP)
├── loader.py       # SnowflakeStageLoader — PUT + COPY INTO (SRP)
├── pipeline.py     # IngestionPipeline + MonthRange — orchestration (SRP)
└── main.py         # Point d'entrée
```

`IngestionPipeline` dépend de `FileDownloaderProtocol` et `DataLoaderProtocol` — on peut brancher n'importe quelle implémentation sans modifier le pipeline (OCP + DIP).

---

## 3. Schéma `RAW.yellow_taxi_trips`

| Colonne | Type Snowflake | Type Parquet | Note |
|---|---|---|---|
| VendorID | INTEGER | int32 | |
| tpep_pickup_datetime | **BIGINT** | timestamp[us] | Microsecondes brutes ⚠️ |
| tpep_dropoff_datetime | **BIGINT** | timestamp[us] | Microsecondes brutes ⚠️ |
| passenger_count | INTEGER | int64 | |
| trip_distance | FLOAT | double | |
| RatecodeID | INTEGER | int64 | |
| store_and_fwd_flag | VARCHAR(1) | large_string | |
| PULocationID | INTEGER | int32 | |
| DOLocationID | INTEGER | int32 | |
| payment_type | INTEGER | int64 | |
| fare_amount | FLOAT | double | |
| extra | FLOAT | double | |
| mta_tax | FLOAT | double | |
| tip_amount | FLOAT | double | |
| tolls_amount | FLOAT | double | |
| improvement_surcharge | FLOAT | double | |
| total_amount | FLOAT | double | |
| congestion_surcharge | FLOAT | double | |
| Airport_fee | FLOAT | double | Casse exacte du Parquet |
| cbd_congestion_fee | FLOAT | double | Nouveau depuis jan. 2025 |
| _loaded_at | TIMESTAMP_NTZ DEFAULT NOW() | — | Colonne technique |

### ⚠️ Timestamps stockés en BIGINT

**Problème rencontré :** Snowflake interprète les `timestamp[us]` Parquet (INT64 microsecondes depuis epoch Unix) comme des **secondes**, produisant des dates en l'an ~55 000 000.

**Décision RAW :** stocker la valeur brute en `BIGINT` (microsecondes). La conversion vers `TIMESTAMP_NTZ` est déléguée à la couche STAGING :

```sql
-- Conversion dans dbt STAGING
TO_TIMESTAMP_NTZ(tpep_pickup_datetime / 1000000) AS tpep_pickup_datetime
```

---

## 4. Résultats

| Mois | Lignes chargées | Taille fichier |
|---|---|---|
| 2025-01 | 3 475 226 | 59.2 MB |
| 2025-02 | 3 577 543 | 60.3 MB |
| 2025-03 | 4 145 257 | 70.0 MB |
| 2025-04 | 3 970 553 | 67.4 MB |
| 2025-05 | 4 591 845 | 77.8 MB |
| 2025-06 | 4 322 960 | 73.5 MB |
| **TOTAL** | **24 083 384** | **408 MB** |

Durée totale : ~4 minutes (warehouse X-SMALL).

---

## 5. Lancer l'ingestion

```bash
# Variables d'environnement dans .env (voir docs/01-snowflake-setup.md)
uv run python -m ingestion.main
```

Pour modifier la période, éditer `ingestion/main.py` :

```python
period = MonthRange(start_year=2025, start_month=1, end_year=2025, end_month=6)
```
