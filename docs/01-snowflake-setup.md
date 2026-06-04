# 01 — Setup Snowflake

## Objectif

Créer l'infrastructure Snowflake du projet : warehouse, base de données, schémas, et configurer une authentification sécurisée par clé RSA.

---

## 1. Objets Snowflake créés

### Warehouse

```sql
CREATE WAREHOUSE IF NOT EXISTS NYC_TAXI_WH
  WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;
```

> `AUTO_SUSPEND = 60s` : le warehouse s'arrête automatiquement après 1 minute d'inactivité pour limiter la consommation de crédits.

### Base de données et schémas

```sql
CREATE DATABASE IF NOT EXISTS NYC_TAXI_DB;

USE DATABASE NYC_TAXI_DB;

CREATE SCHEMA IF NOT EXISTS RAW;
CREATE SCHEMA IF NOT EXISTS STAGING;
CREATE SCHEMA IF NOT EXISTS FINAL;
```

| Schéma    | Rôle                                      |
|-----------|-------------------------------------------|
| RAW       | Données brutes ingérées (Parquet → table) |
| STAGING   | Données nettoyées et enrichies (dbt)      |
| FINAL     | Tables analytiques et reporting (dbt)     |

---

## 2. Authentification Key Pair RSA

### Pourquoi Key Pair ?

- Standard industrie pour les connexions programmatiques (dbt, Python, CI/CD)
- Pas de mot de passe stocké en clair
- Compatible nativement avec `dbt-fusion` et `snowflake-connector-python`

### Génération des clés

```bash
# Clé privée (format PKCS8, non chiffrée)
openssl genrsa 2048 | openssl pkcs8 -topk8 -nocrypt -out .secrets/snowflake_key.p8

# Clé publique
openssl rsa -in .secrets/snowflake_key.p8 -pubout -out .secrets/snowflake_key.pub
```

Les clés sont stockées dans `.secrets/` — ce dossier est ignoré par git.

### Attachement de la clé publique au user Snowflake

```sql
-- Remplacer <USERNAME> par le résultat de SELECT CURRENT_USER();
ALTER USER <USERNAME> SET RSA_PUBLIC_KEY='<contenu_clé_publique_sans_headers>';
```

---

## 3. Variables d'environnement

Fichier `.env` à la racine (ignoré par git) :

```bash
SNOWFLAKE_ACCOUNT=<orgname>-<accountname>
SNOWFLAKE_USER=<username>
SNOWFLAKE_PRIVATE_KEY_PATH=.secrets/snowflake_key.p8
SNOWFLAKE_WAREHOUSE=NYC_TAXI_WH
SNOWFLAKE_DATABASE=NYC_TAXI_DB
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

> L'`ACCOUNT` se trouve dans l'URL Snowsight : `https://app.snowflake.com/<orgname>/<accountname>/`

---

## 4. Dépendances Python

```bash
uv add snowflake-connector-python python-dotenv cryptography
```

---

## Résultat attendu

Une connexion Python réussie retourne :

```
User      : <USERNAME>
Warehouse : NYC_TAXI_WH
Database  : NYC_TAXI_DB
Role      : ACCOUNTADMIN
Schemas   : ['FINAL', 'INFORMATION_SCHEMA', 'PUBLIC', 'RAW', 'STAGING']

Connexion Snowflake OK
```
