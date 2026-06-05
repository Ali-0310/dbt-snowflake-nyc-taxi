# 03 — Modèles dbt et tests qualité

## Architecture dbt

```
nyc_taxi_dbt/
├── models/
│   ├── staging/
│   │   ├── _sources.yml          # Déclaration source RAW
│   │   ├── _stg_clean_trips.yml  # Tests génériques
│   │   └── stg_clean_trips.sql   # Vue STAGING (nettoyage + enrichissement)
│   └── final/
│       ├── daily_summary.sql     # Table : métriques par jour
│       ├── zone_analysis.sql     # Table : métriques par zone
│       └── hourly_patterns.sql   # Table : patterns par heure
├── macros/
│   └── generate_schema_name.sql  # Override : schemas Snowflake exacts
└── tests/
    └── assert_no_aberrant_speed.sql  # Test singulier : vitesse > 150 km/h
```

---

## Modèle STAGING — `stg_clean_trips`

**Matérialisation :** `view` (pas de stockage supplémentaire)

### Pipeline de transformation

| CTE | Rôle |
|---|---|
| `source` | Lecture de `RAW.yellow_taxi_trips` |
| `converted` | Conversion timestamps BIGINT → TIMESTAMP_NTZ, renommage colonnes |
| `filtered` | Filtres qualité |
| `enriched` | Colonnes calculées |
| `speed_filtered` | Exclusion des vitesses aberrantes |

### Règles de filtrage

| Règle | Seuil | Lignes exclues |
|---|---|---|
| `fare_amount > 0` | Pas de tarif nul/négatif | — |
| `trip_distance` | 0.1 – 200 miles | — |
| `passenger_count` | 1 – 6 | — |
| Durée du trajet | 1 – 180 minutes | — |
| `avg_speed_kmh <= 150` | Détecté par test singulier | 1 148 lignes |
| **Total filtré** | | **3 637 684 lignes (15.1%)** |
| **Total retenu** | | **20 445 700 lignes** |

### Conversions appliquées

- `trip_distance` : miles × 1.60934 → `trip_distance_km`
- `avg_speed` : mph × 1.60934 → `avg_speed_kmh`
- `distance_category` : seuils recalculés en km (1.6 / 8 / 24 km)

### Colonnes enrichies

| Colonne | Description |
|---|---|
| `trip_date` | Date du trajet |
| `pickup_hour` | Heure de prise en charge |
| `pickup_dow` | Jour de la semaine |
| `time_of_day` | morning / afternoon / evening / night |
| `trip_duration_min` | Durée en minutes |
| `avg_speed_kmh` | Vitesse moyenne en km/h |
| `distance_category` | short / medium / long / very_long |
| `tip_rate_pct` | Taux de pourboire en % |

---

## Modèles FINAL

**Matérialisation :** `table` (calculés et stockés pour la performance)

| Modèle | Clé de groupe | Métriques principales |
|---|---|---|
| `daily_summary` | `trip_date` | trips, distance_km, revenue, speed_kmh, tip_rate |
| `zone_analysis` | `pickup_location_id` | trips, distance_km, fare, tip_rate, destinations |
| `hourly_patterns` | `pickup_hour`, `time_of_day`, `pickup_dow` | trips, speed_kmh, fare, tip_rate |

---

## Tests qualité

**20 tests — 20 succès**

### Tests génériques (`_stg_clean_trips.yml`)

| Colonne | Tests |
|---|---|
| `vendor_id` | `not_null`, `accepted_values` [1, 2, 6, 7] |
| `pickup_datetime`, `dropoff_datetime` | `not_null` |
| `payment_type` | `not_null`, `accepted_values` [0–6] |
| `time_of_day` | `not_null`, `accepted_values` |
| `distance_category` | `not_null`, `accepted_values` |
| Autres colonnes clés | `not_null` |

### Test singulier (`assert_no_aberrant_speed.sql`)

Vérifie qu'aucun trajet n'a une vitesse > 150 km/h.
Ce test a révélé **1 148 outliers** non capturés par les filtres initiaux → ajout du filtre `avg_speed_kmh <= 150` dans le modèle.

---

## Lancer dbt

```bash
# Charger les variables d'environnement
set -a && source .env && set +a

# Exécuter tous les modèles
dbt run --project-dir nyc_taxi_dbt

# Lancer les tests
dbt test --project-dir nyc_taxi_dbt

# Run + test en une commande
dbt build --project-dir nyc_taxi_dbt
```

---

## Macro `generate_schema_name`

Par défaut dbt préfixe les schémas custom avec le schéma cible (`STAGING_STAGING`).
Ce macro override force l'utilisation du nom exact défini dans `dbt_project.yml` :

```sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim | upper }}
    {%- endif -%}
{%- endmacro %}
```
