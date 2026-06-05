# 04 — GitHub Actions CI

## Objectif

Automatiser `dbt run` + `dbt test` à chaque push ou pull request sur `main`.

---

## Workflow : `.github/workflows/dbt_ci.yml`

**Déclencheurs :**
- Push sur `main`
- Pull request vers `main`

**Étapes :**

| Étape | Description |
|---|---|
| Checkout | Récupère le code |
| Set up Python 3.10 | Environnement Python pour dbt |
| Install dbt-snowflake | `pip install dbt-snowflake` (dbt-core) |
| Write private key | Écrit la clé RSA depuis le secret GitHub vers `.secrets/snowflake_key.p8` |
| dbt run | Exécute les 4 modèles (stg_clean_trips + 3 tables FINAL) |
| dbt test | Lance les 20 tests qualité |

---

## GitHub Secrets requis

| Secret | Description |
|---|---|
| `SNOWFLAKE_ACCOUNT` | Identifiant compte Snowflake (`orgname-accountname`) |
| `SNOWFLAKE_USER` | Nom d'utilisateur Snowflake |
| `SNOWFLAKE_ROLE` | Rôle Snowflake (`ACCOUNTADMIN`) |
| `SNOWFLAKE_DATABASE` | Base de données (`NYC_TAXI_DB`) |
| `SNOWFLAKE_WAREHOUSE` | Warehouse (`NYC_TAXI_WH`) |
| `SNOWFLAKE_PRIVATE_KEY` | Contenu complet du fichier `.p8` (headers inclus) |

> Configuration : **Settings → Secrets and variables → Actions → New repository secret**

---

## Authentification Snowflake en CI

La clé privée RSA est stockée comme secret GitHub et écrite dans un fichier temporaire lors du job :

```yaml
- name: Write Snowflake private key
  run: |
    mkdir -p .secrets
    echo "${{ secrets.SNOWFLAKE_PRIVATE_KEY }}" > .secrets/snowflake_key.p8
```

Le `profiles.yml` commité dans `nyc_taxi_dbt/` utilise `env_var()` — les valeurs sont injectées via `env:` dans chaque step dbt.

---

## Résultat attendu

```
✓ dbt-run-test in ~50s
  ✓ Install dbt-snowflake
  ✓ dbt run    → 4 models success
  ✓ dbt test   → 20 tests success
```

---

## Note : dbt-core vs dbt-fusion

| Environnement | Outil | Version |
|---|---|---|
| Local | dbt-fusion | 2.0.0-preview |
| CI/CD | dbt-snowflake (dbt-core) | dernière stable |

Le YAML de tests utilise la syntaxe dbt-fusion (`arguments:`). dbt-core l'accepte également depuis les versions récentes.
