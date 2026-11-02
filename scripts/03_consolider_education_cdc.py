"""Consolide l'éducation de la mère (CDC WONDER) : année x tranche d'âge native x niveau d'éducation natif.

Entrées : data/cdc/wonder_1995_2002.tsv, wonder_2003_2006.tsv, wonder_2007_2024.tsv
Sortie  : data/cdc/cdc_naissances_age_education_annee.csv
La race et la pluralité présentes dans les exports sont sommées (non utilisées ici).
"""
import io
from pathlib import Path

import pandas as pd

DATA = Path("data/cdc")
FICHIERS = ["wonder_1995_2002.tsv", "wonder_2003_2006.tsv", "wonder_2007_2024.tsv"]


def lire(nom):
    lignes = (DATA / nom).read_text(encoding="utf-8", errors="replace").split("\n")
    fin = next(i for i, l in enumerate(lignes) if l.strip() == '"---"')
    df = pd.read_csv(io.StringIO("\n".join(lignes[:fin])), sep="\t", dtype=str)
    col_age = next(c for c in df.columns if c.startswith("Age of Mother") and "Code" not in c)
    if "Mother's Education" not in df.columns:
        raise SystemExit(f"{nom} : colonne « Mother's Education » absente. Refaire l'export avec l'éducation.")
    df = df.rename(columns={
        col_age: "tranche_age_native",
        "Mother's Education": "education_native",
        "Year": "annee",
        "Births": "nb_naissances",
    })
    df = df[["annee", "tranche_age_native", "education_native", "nb_naissances"]].copy()
    df["nb_naissances"] = pd.to_numeric(df["nb_naissances"], errors="raise")
    df["annee"] = df["annee"].astype(int)
    df["source_base"] = nom
    return df


brut = pd.concat([lire(f) for f in FICHIERS], ignore_index=True)
agg = (
    brut.groupby(["annee", "tranche_age_native", "education_native", "source_base"], as_index=False)["nb_naissances"]
    .sum()
    .sort_values(["annee", "tranche_age_native", "education_native"])
)
agg.insert(0, "zone_code", "US")
agg.insert(1, "zone_type", "pays")
agg = agg[["zone_code", "zone_type", "annee", "tranche_age_native", "education_native", "source_base", "nb_naissances"]]
agg.to_csv(DATA / "cdc_naissances_age_education_annee.csv", index=False)
print(agg.shape, agg["annee"].min(), agg["annee"].max())
print("Niveaux d'éducation distincts :", agg["education_native"].nunique())
print(agg.groupby("annee")["nb_naissances"].sum().tail(3))
