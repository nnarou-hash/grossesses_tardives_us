"""Dashboard : naissances tardives aux États-Unis (CDC WONDER, 1995-2024).

Lecture des tables dbt dans BigQuery (naissances_dbt).
Mode BigQuery si la variable GCP_PROJECT est définie, sinon mode CSV : instantané des tables dbt dans app/data/
(voir scripts/05_exporter_dashboard_csv.py). DATA_SOURCE=csv ou DATA_SOURCE=bigquery force le choix.
"""
import os
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Naissances tardives, États-Unis", layout="wide")

DATASET = "naissances_dbt"
CSV_DIR = Path(__file__).resolve().parent / "data"
TABLES = {
    "indicateurs": "mart_naissances_tardives_indicateurs",
    "tranches": "mart_naissances_tranches_natives",
    "couverture": "mart_education_couverture",
    "edu_fenetre": "mart_education_par_fenetre",
}
FENETRE_EDUCATION = "2016-2024"


def fr(valeur, decimales=1):
    """Format français : virgule décimale, espace pour les milliers."""
    texte = f"{valeur:,.{decimales}f}"
    return texte.replace(",", " ").replace(".", ",")


def mode_donnees():
    choix = os.environ.get("DATA_SOURCE", "").lower()
    if choix in ("csv", "bigquery"):
        return choix
    return "bigquery" if os.environ.get("GCP_PROJECT") else "csv"


@st.cache_data(show_spinner="Chargement des données…")
def charger(mode):
    if mode == "csv":
        manquants = [f"{cle}.csv" for cle in TABLES if not (CSV_DIR / f"{cle}.csv").exists()]
        if manquants:
            raise FileNotFoundError(
                f"Fichiers absents dans {CSV_DIR} : {', '.join(manquants)}. "
                "Lance : python scripts/05_exporter_dashboard_csv.py"
            )
        return {cle: pd.read_csv(CSV_DIR / f"{cle}.csv") for cle in TABLES}

    from google.cloud import bigquery

    projet = os.environ["GCP_PROJECT"]
    client = bigquery.Client(project=projet)
    donnees = {}
    for cle, table in TABLES.items():
        sql = f"SELECT * FROM `{projet}.{DATASET}.{table}`"
        donnees[cle] = pd.DataFrame([dict(ligne) for ligne in client.query(sql).result()])
    return donnees


mode = mode_donnees()
try:
    data = charger(mode)
except KeyError:
    st.error("La variable GCP_PROJECT n'est pas définie. Lance : export GCP_PROJECT=$(gcloud config get-value project)")
    st.stop()
except Exception as erreur:  # noqa: BLE001
    st.error(f"Impossible de charger les données : {erreur}")
    st.stop()

ind = data["indicateurs"].sort_values("annee").reset_index(drop=True)
tr = data["tranches"]
cov = data["couverture"].sort_values("annee")
edu_fenetre = data["edu_fenetre"]

premiere, derniere = ind.iloc[0], ind.iloc[-1]
annees_incompletes = sorted(ind.loc[ind["donnee_incomplete"], "annee"].astype(int).tolist())

st.title("Naissances tardives aux États-Unis")
st.caption(
    f"Part des naissances dont la mère a 35 ans ou plus, {int(premiere.annee)} à {int(derniere.annee)}. "
    "Source : CDC WONDER (National Vital Statistics System), naissances vivantes, niveau national."
)

if mode == "csv":
    fichier_date = CSV_DIR / "instantane.txt"
    date_instantane = fichier_date.read_text(encoding="utf-8").strip() if fichier_date.exists() else "date inconnue"
    st.caption(f"Données : instantané des tables dbt exportées depuis BigQuery le {date_instantane}.")

col1, col2, col3 = st.columns(3)
col1.metric(
    f"Mères de 35 ans et plus, {int(derniere.annee)}",
    f"{fr(derniere.part_35_plus_pct)} %",
    f"{fr(derniere.part_35_plus_pct - premiere.part_35_plus_pct)} pts depuis {int(premiere.annee)}",
)
col2.metric(
    f"Mères de 40 ans et plus, {int(derniere.annee)}",
    f"{fr(derniere.part_40_plus_pct)} %",
    f"{fr(derniere.part_40_plus_pct - premiere.part_40_plus_pct)} pts depuis {int(premiere.annee)}",
)
col3.metric(f"Naissances vivantes, {int(derniere.annee)}", fr(derniere.nb_naissances_total, 0))

# ---------------------------------------------------------------- Évolution 35+ / 40+
st.subheader("Évolution de la part des naissances tardives")
long = ind.melt(
    id_vars=["annee"],
    value_vars=["part_35_plus_pct", "part_40_plus_pct"],
    var_name="indicateur",
    value_name="part",
)
long["indicateur"] = long["indicateur"].map(
    {"part_35_plus_pct": "35 ans et plus", "part_40_plus_pct": "40 ans et plus"}
)
lignes = (
    alt.Chart(long)
    .mark_line(point=True)
    .encode(
        x=alt.X("annee:Q", title="Année", axis=alt.Axis(format="d"),
                scale=alt.Scale(domain=[int(premiere.annee), int(derniere.annee)])),
        y=alt.Y("part:Q", title="Part des naissances (%)"),
        color=alt.Color("indicateur:N", title=None),
        tooltip=[alt.Tooltip("annee:Q", title="Année", format="d"),
                 alt.Tooltip("indicateur:N", title="Indicateur"),
                 alt.Tooltip("part:Q", title="Part (%)", format=".2f")],
    )
)
repere = (
    alt.Chart(pd.DataFrame({"annee": [2007]}))
    .mark_rule(strokeDash=[4, 4], color="gray")
    .encode(x="annee:Q")
)
st.altair_chart(lignes + repere, width="stretch")
st.caption(
    "Trait pointillé : 2007, changement de base WONDER et des règles d'imputation de l'âge "
    "(limites L5 et L8). Prudence sur la comparaison de part et d'autre."
)

# ---------------------------------------------------------------- Tranches d'âge natives
st.subheader("Répartition par tranche d'âge de la mère (tranches de 5 ans)")
ordre_libelles = (
    tr[["ordre_tranche", "tranche_age_libelle"]].drop_duplicates().sort_values("ordre_tranche")["tranche_age_libelle"].tolist()
)
onglet_temps, onglet_annee = st.tabs(["Dans le temps", "Une année"])

with onglet_temps:
    aire = (
        alt.Chart(tr)
        .mark_area()
        .encode(
            x=alt.X("annee:Q", title="Année", axis=alt.Axis(format="d"),
                    scale=alt.Scale(domain=[int(premiere.annee), int(derniere.annee)])),
            y=alt.Y("part_pct:Q", title="Part des naissances (%)", stack="zero"),
            color=alt.Color("tranche_age_libelle:N", title="Tranche d'âge", sort=ordre_libelles,
                            scale=alt.Scale(domain=ordre_libelles)),
            order=alt.Order("ordre_tranche:Q"),
            tooltip=[alt.Tooltip("annee:Q", title="Année", format="d"),
                     alt.Tooltip("tranche_age_libelle:N", title="Tranche"),
                     alt.Tooltip("part_pct:Q", title="Part (%)", format=".2f")],
        )
    )
    st.altair_chart(aire, width="stretch")

with onglet_annee:
    annee_choisie = st.slider(
        "Année", int(premiere.annee), int(derniere.annee), int(derniere.annee), step=1
    )
    tranche_annee = tr[tr["annee"] == annee_choisie]
    histogramme = (
        alt.Chart(tranche_annee)
        .mark_bar()
        .encode(
            x=alt.X("tranche_age_libelle:N", sort=ordre_libelles, title="Tranche d'âge de la mère",
                    axis=alt.Axis(labelAngle=-30)),
            y=alt.Y("part_pct:Q", title="Part des naissances (%)"),
            tooltip=[alt.Tooltip("tranche_age_libelle:N", title="Tranche"),
                     alt.Tooltip("nb_naissances:Q", title="Naissances", format=","),
                     alt.Tooltip("part_pct:Q", title="Part (%)", format=".2f")],
        )
    )
    st.altair_chart(histogramme, width="stretch")
    if annee_choisie in annees_incompletes:
        st.info(
            f"{annee_choisie} : la tranche des 50 ans et plus est absente des données du CDC "
            "(âges de 50 ans et plus imputés jusqu'en 1996, limite L7). "
            "La part des 40 ans et plus est très légèrement sous-estimée."
        )

# ---------------------------------------------------------------- Éducation
st.subheader("Niveau d'éducation de la mère")
cov_fenetre = cov[cov["fenetre_analyse"] == FENETRE_EDUCATION]
st.caption(
    "Le CDC ne fournit pas de catégorie socioprofessionnelle : l'éducation sert de substitut du niveau socio-économique. "
    f"Période {FENETRE_EDUCATION} : tous les États utilisent le certificat de naissance de 2003, "
    f"et le niveau d'éducation est connu pour {fr(cov_fenetre.couverture_pct.min())} à {fr(cov_fenetre.couverture_pct.max())} % des naissances. "
    "Avant 2016, les certificats de 1989 et de 2003 coexistent et ne sont pas comparables."
)

ef = edu_fenetre[edu_fenetre["fenetre_analyse"] == FENETRE_EDUCATION].sort_values("ordre_groupe")
ordre_groupes = ef["groupe_education"].tolist()
st.markdown(f"**Niveau d'éducation : toutes les mères et mères de 35+ ({FENETRE_EDUCATION})**")
compare = ef.melt(
    id_vars=["groupe_education", "ordre_groupe"],
    value_vars=["part_dans_toutes_meres_pct", "part_dans_meres_35_plus_pct"],
    var_name="population", value_name="part",
)
compare["population"] = compare["population"].map(
    {"part_dans_toutes_meres_pct": "Toutes les mères", "part_dans_meres_35_plus_pct": "Mères de 35 ans et plus"}
)
barres_cmp = (
    alt.Chart(compare)
    .mark_bar()
    .encode(
        y=alt.Y("groupe_education:N", sort=ordre_groupes, title=None),
        x=alt.X("part:Q", title="Répartition (%)"),
        yOffset="population:N",
        color=alt.Color("population:N", title=None),
        tooltip=[alt.Tooltip("groupe_education:N", title="Éducation"),
                 alt.Tooltip("population:N", title="Population"),
                 alt.Tooltip("part:Q", title="Part (%)", format=".1f")],
    )
)
st.altair_chart(barres_cmp, width="stretch")

# ---------------------------------------------------------------- Qualité
with st.expander("Qualité des données et limites"):
    concept = ind["concept_age"].iloc[0]
    st.markdown(
        f"""
- **Concept d'âge** : `{concept}` (âge au dernier anniversaire, d'après la définition CDC/NCHS).
- **Contrôles** : données validées avant chargement (Great Expectations) puis après transformation (tests dbt).
- **Années avec données incomplètes** : {", ".join(str(a) for a in annees_incompletes) or "aucune"} (tranche 50 ans et plus absente, L7).
- **Rupture 2006-2007** : changement de base WONDER et des règles d'imputation de l'âge (L5, L8), non quantifié.
- **Cellules supprimées** : écart de 0,01 à 0,03 % sur les totaux (L4).
- **Niveau national uniquement** : pas de détail par État (L6).
- **Éducation** : analyse limitée à 2016-2024, période où tous les États utilisent le certificat de 2003. Avant, les certificats de 1989 et de 2003 ne sont pas comparables et la couverture est partielle (L9).
- **Pas de catégorie socioprofessionnelle** dans CDC WONDER (L10). Les niveaux d'éducation sont regroupés en 4 groupes (docs/06_education_harmonisation.md).
        """
    )

with st.expander("Données"):
    st.dataframe(ind, width="stretch", hide_index=True)
