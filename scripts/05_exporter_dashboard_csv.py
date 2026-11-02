"""Exporte les tables dbt utilisées par le dashboard vers app/data/*.csv (BigQuery -> CSV), avec la date de l'instantané.

Usage : export GCP_PROJECT=$(gcloud config get-value project) ; python scripts/05_exporter_dashboard_csv.py
Les fichiers app/data/*.csv sont versionnés : ils alimentent le dashboard publié (Streamlit Community Cloud).
"""
import os
from datetime import date
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

DATASET = "naissances_dbt"
TABLES = {
    "indicateurs": "mart_naissances_tardives_indicateurs",
    "tranches": "mart_naissances_tranches_natives",
    "couverture": "mart_education_couverture",
    "edu_fenetre": "mart_education_par_fenetre",
}

projet = os.environ["GCP_PROJECT"]
client = bigquery.Client(project=projet)
sortie = Path("app/data")
sortie.mkdir(parents=True, exist_ok=True)

for cle, table in TABLES.items():
    sql = f"SELECT * FROM `{projet}.{DATASET}.{table}`"
    df = pd.DataFrame([dict(ligne) for ligne in client.query(sql).result()])
    df.to_csv(sortie / f"{cle}.csv", index=False)
    print(f"{cle}.csv : {len(df)} lignes")

(sortie / "instantane.txt").write_text(date.today().isoformat() + "\n", encoding="utf-8")
print("instantane.txt :", date.today().isoformat())
