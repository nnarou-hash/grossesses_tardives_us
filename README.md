# Naissances tardives aux États-Unis (1995-2024)

Projet portfolio **Data Governance** : un pipeline de données complet (validation, transformation, tests, documentation, dashboard)
construit sur les statistiques de naissances du CDC (CDC WONDER), avec la gouvernance des données comme fil conducteur.

## Dashboard en ligne

Dashboard HTML en ligne : https://nnarou-hash.github.io/maternite-tardive/\n\nVersion Streamlit : `streamlit run app/dashboard.py` (application interactive exécutable en local ; le dépôt ne contient pas encore d'URL Streamlit Community Cloud publiée).

Le dashboard publié lit un instantané des tables dbt (`app/data/*.csv`), exporté depuis BigQuery avec
`python scripts/05_exporter_dashboard_csv.py`. En local avec BigQuery : `export GCP_PROJECT=...` puis `streamlit run app/dashboard.py`.

## Question

Comment évolue la part des naissances dont la mère a 35 ans ou plus (et 40 ans ou plus) aux États-Unis, selon l'âge de la mère
et son niveau d'éducation, et que valent les données qui permettent de le mesurer ?

## Résultats

- La part des naissances à **35 ans et plus** passe de **11,6 % en 1995 à 21,3 % en 2024** ; celle des **40 ans et plus** de **1,8 % à 4,2 %**.
- Sur 2016-2024, **53 %** des mères de 35 ans et plus ont une licence ou plus, contre **34 %** de l'ensemble des mères.
- Le CDC ne fournit pas de catégorie socioprofessionnelle : l'éducation sert de substitut du niveau socio-économique.

## Architecture

```
CDC WONDER (exports TSV)
   -> scripts/01, 03 : consolidation (Python, pandas)
   -> scripts/02, 04 : validation des données brutes (Great Expectations)
   -> BigQuery naissances_raw
   -> dbt : staging -> intermediate -> marts (+ seed de correspondance, tests)
   -> BigQuery naissances_dbt
   -> app/dashboard.py (Streamlit)
```

Technologies : Python, Great Expectations, BigQuery, dbt, Streamlit.

## Gouvernance des données

| Document | Contenu |
|---|---|
| [docs/01_glossaire.md](docs/01_glossaire.md) | Définitions et périmètre (naissance tardive, naissance vivante, âge de la mère, période) |
| [docs/02_matrice_sources.md](docs/02_matrice_sources.md) | Correspondance des définitions entre sources et règle d'harmonisation |
| [docs/03_dictionnaire_donnees.md](docs/03_dictionnaire_donnees.md) | Dictionnaire des tables finales |
| [docs/04_regles_qualite.md](docs/04_regles_qualite.md) | Règles de qualité, outil de contrôle et gravité |
| [docs/05_limites_methodologiques.md](docs/05_limites_methodologiques.md) | Registre des limites et mesures prises |
| [docs/06_education_harmonisation.md](docs/06_education_harmonisation.md) | Décisions sur l'éducation de la mère (non-comparabilité des certificats de naissance) |

Contrôles : Great Expectations avant le chargement (complétude, validité, unicité), puis tests dbt après transformation
(complétude, unicité, cohérence entre tables, justification de la période d'analyse de l'éducation).

## Principales limites

- Les États-Unis uniquement, au niveau national (l'API de CDC WONDER ne fournit pas de détail par État).
- Âge de la mère : âge révolu (définition CDC/NCHS) ; la tranche « 50 ans et plus » est absente en 1995 et 1996 (âges imputés par le CDC).
- Rupture possible entre 2006 et 2007 (changement de base WONDER et des règles d'imputation de l'âge).
- Éducation : les certificats de naissance de 1989 et de 2003 ne sont pas comparables ; l'analyse est limitée à 2016-2024,
  période où tous les États utilisent le certificat de 2003.

Détail et mesures prises : [docs/05_limites_methodologiques.md](docs/05_limites_methodologiques.md).

## Reproduire

Les données ne sont pas versionnées (conditions d'usage de CDC WONDER) : il faut refaire les exports.

1. **Environnement**
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Exports CDC WONDER** (https://wonder.cdc.gov/natality.html) : pour chacune des bases *1995-2002*, *2003-2006* et *2007-2024*,
   regrouper les résultats par `Year`, `Age of Mother` (tranches de 5 ans) et `Mother's Education`, sélectionner toutes les années,
   exporter en TSV et enregistrer sous `data/cdc/wonder_1995_2002.tsv`, `wonder_2003_2006.tsv`, `wonder_2007_2024.tsv`.
3. **Consolidation et validation**
   ```bash
   python scripts/01_consolider_cdc.py && python scripts/02_valider_cdc_ge.py
   python scripts/03_consolider_education_cdc.py && python scripts/04_valider_education_ge.py
   ```
4. **Chargement dans BigQuery**
   ```bash
   PROJECT=$(gcloud config get-value project)
   bq --location=EU mk --dataset ${PROJECT}:naissances_raw
   bq --location=EU mk --dataset ${PROJECT}:naissances_dbt
   bq load --location=EU --source_format=CSV --skip_leading_rows=1 --replace naissances_raw.cdc_naissances_age_annee \
     data/cdc/cdc_naissances_age_annee.csv \
     zone_code:STRING,zone_type:STRING,annee:INT64,tranche_age_native:STRING,source_base:STRING,nb_naissances:INT64
   bq load --location=EU --source_format=CSV --skip_leading_rows=1 --replace naissances_raw.cdc_naissances_age_education_annee \
     data/cdc/cdc_naissances_age_education_annee.csv \
     zone_code:STRING,zone_type:STRING,annee:INT64,tranche_age_native:STRING,education_native:STRING,source_base:STRING,nb_naissances:INT64
   ```
5. **dbt**
   ```bash
   export GCP_PROJECT=$(gcloud config get-value project)
   cd dbt_naissances
   dbt seed --profiles-dir . && dbt run --profiles-dir . && dbt test --profiles-dir .
   ```
6. **Dashboard**
   ```bash
   cd .. && streamlit run app/dashboard.py
   ```

## Sources

- CDC WONDER, Natality (National Center for Health Statistics, National Vital Statistics System) : https://wonder.cdc.gov/natality.html
- Documentation de l'éducation de la mère : https://wonder.cdc.gov/wonder/help/natality.html
- Définition de l'âge (CDC/NCHS, Health, United States) : https://www.cdc.gov/nchs/hus/sources-definitions/age.htm

## Suite prévue

Extension à la France (INSEE) et à l'Europe (Eurostat) pour une comparaison multi-sources : le cadrage des définitions est déjà documenté
dans [docs/02_matrice_sources.md](docs/02_matrice_sources.md).
