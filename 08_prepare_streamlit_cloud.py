"""Prépare le déploiement du dashboard sur Streamlit Community Cloud.

À lancer depuis le dossier naissances_tardives :
    python 08_prepare_streamlit_cloud.py                       # prépare les fichiers
    python 08_prepare_streamlit_cloud.py --url https://xxx.streamlit.app   # après le déploiement : ajoute le lien au README

Ce script : remplace app/dashboard.py et scripts/05_exporter_dashboard_csv.py, crée app/requirements.txt,
autorise le versionnement de app/data/ dans .gitignore et ajoute la section « Dashboard en ligne » au README.
"""
import re
import sys
from pathlib import Path

if not Path("app").is_dir() or not Path("dbt_naissances").is_dir():
    sys.exit("Lance ce script depuis le dossier naissances_tardives (app et dbt_naissances introuvables).")

URL = None
if "--url" in sys.argv:
    i = sys.argv.index("--url")
    if i + 1 >= len(sys.argv):
        sys.exit("Usage : python 08_prepare_streamlit_cloud.py --url https://xxx.streamlit.app")
    URL = sys.argv[i + 1].strip()

FICHIERS = {'app/dashboard.py': '"""Dashboard : naissances tardives aux États-Unis (CDC WONDER, 1995-2024).\n\nLecture des tables dbt dans BigQuery (naissances_dbt).\nMode BigQuery si la variable GCP_PROJECT est définie, sinon mode CSV : instantané des tables dbt dans app/data/\n(voir scripts/05_exporter_dashboard_csv.py). DATA_SOURCE=csv ou DATA_SOURCE=bigquery force le choix.\n"""\nimport os\nfrom pathlib import Path\n\nimport altair as alt\nimport pandas as pd\nimport streamlit as st\n\nst.set_page_config(page_title="Naissances tardives, États-Unis", layout="wide")\n\nDATASET = "naissances_dbt"\nCSV_DIR = Path(__file__).resolve().parent / "data"\nTABLES = {\n    "indicateurs": "mart_naissances_tardives_indicateurs",\n    "tranches": "mart_naissances_tranches_natives",\n    "couverture": "mart_education_couverture",\n    "edu_fenetre": "mart_education_par_fenetre",\n}\nFENETRE_EDUCATION = "2016-2024"\n\n\ndef fr(valeur, decimales=1):\n    """Format français : virgule décimale, espace pour les milliers."""\n    texte = f"{valeur:,.{decimales}f}"\n    return texte.replace(",", " ").replace(".", ",")\n\n\ndef mode_donnees():\n    choix = os.environ.get("DATA_SOURCE", "").lower()\n    if choix in ("csv", "bigquery"):\n        return choix\n    return "bigquery" if os.environ.get("GCP_PROJECT") else "csv"\n\n\n@st.cache_data(show_spinner="Chargement des données…")\ndef charger(mode):\n    if mode == "csv":\n        manquants = [f"{cle}.csv" for cle in TABLES if not (CSV_DIR / f"{cle}.csv").exists()]\n        if manquants:\n            raise FileNotFoundError(\n                f"Fichiers absents dans {CSV_DIR} : {\', \'.join(manquants)}. "\n                "Lance : python scripts/05_exporter_dashboard_csv.py"\n            )\n        return {cle: pd.read_csv(CSV_DIR / f"{cle}.csv") for cle in TABLES}\n\n    from google.cloud import bigquery\n\n    projet = os.environ["GCP_PROJECT"]\n    client = bigquery.Client(project=projet)\n    donnees = {}\n    for cle, table in TABLES.items():\n        sql = f"SELECT * FROM `{projet}.{DATASET}.{table}`"\n        donnees[cle] = pd.DataFrame([dict(ligne) for ligne in client.query(sql).result()])\n    return donnees\n\n\nmode = mode_donnees()\ntry:\n    data = charger(mode)\nexcept KeyError:\n    st.error("La variable GCP_PROJECT n\'est pas définie. Lance : export GCP_PROJECT=$(gcloud config get-value project)")\n    st.stop()\nexcept Exception as erreur:  # noqa: BLE001\n    st.error(f"Impossible de charger les données : {erreur}")\n    st.stop()\n\nind = data["indicateurs"].sort_values("annee").reset_index(drop=True)\ntr = data["tranches"]\ncov = data["couverture"].sort_values("annee")\nedu_fenetre = data["edu_fenetre"]\n\npremiere, derniere = ind.iloc[0], ind.iloc[-1]\nannees_incompletes = sorted(ind.loc[ind["donnee_incomplete"], "annee"].astype(int).tolist())\n\nst.title("Naissances tardives aux États-Unis")\nst.caption(\n    f"Part des naissances dont la mère a 35 ans ou plus, {int(premiere.annee)} à {int(derniere.annee)}. "\n    "Source : CDC WONDER (National Vital Statistics System), naissances vivantes, niveau national."\n)\n\nif mode == "csv":\n    fichier_date = CSV_DIR / "instantane.txt"\n    date_instantane = fichier_date.read_text(encoding="utf-8").strip() if fichier_date.exists() else "date inconnue"\n    st.caption(f"Données : instantané des tables dbt exportées depuis BigQuery le {date_instantane}.")\n\ncol1, col2, col3 = st.columns(3)\ncol1.metric(\n    f"Mères de 35 ans et plus, {int(derniere.annee)}",\n    f"{fr(derniere.part_35_plus_pct)} %",\n    f"{fr(derniere.part_35_plus_pct - premiere.part_35_plus_pct)} pts depuis {int(premiere.annee)}",\n)\ncol2.metric(\n    f"Mères de 40 ans et plus, {int(derniere.annee)}",\n    f"{fr(derniere.part_40_plus_pct)} %",\n    f"{fr(derniere.part_40_plus_pct - premiere.part_40_plus_pct)} pts depuis {int(premiere.annee)}",\n)\ncol3.metric(f"Naissances vivantes, {int(derniere.annee)}", fr(derniere.nb_naissances_total, 0))\n\n# ---------------------------------------------------------------- Évolution 35+ / 40+\nst.subheader("Évolution de la part des naissances tardives")\nlong = ind.melt(\n    id_vars=["annee"],\n    value_vars=["part_35_plus_pct", "part_40_plus_pct"],\n    var_name="indicateur",\n    value_name="part",\n)\nlong["indicateur"] = long["indicateur"].map(\n    {"part_35_plus_pct": "35 ans et plus", "part_40_plus_pct": "40 ans et plus"}\n)\nlignes = (\n    alt.Chart(long)\n    .mark_line(point=True)\n    .encode(\n        x=alt.X("annee:Q", title="Année", axis=alt.Axis(format="d"),\n                scale=alt.Scale(domain=[int(premiere.annee), int(derniere.annee)])),\n        y=alt.Y("part:Q", title="Part des naissances (%)"),\n        color=alt.Color("indicateur:N", title=None),\n        tooltip=[alt.Tooltip("annee:Q", title="Année", format="d"),\n                 alt.Tooltip("indicateur:N", title="Indicateur"),\n                 alt.Tooltip("part:Q", title="Part (%)", format=".2f")],\n    )\n)\nrepere = (\n    alt.Chart(pd.DataFrame({"annee": [2007]}))\n    .mark_rule(strokeDash=[4, 4], color="gray")\n    .encode(x="annee:Q")\n)\nst.altair_chart(lignes + repere, width="stretch")\nst.caption(\n    "Trait pointillé : 2007, changement de base WONDER et des règles d\'imputation de l\'âge "\n    "(limites L5 et L8). Prudence sur la comparaison de part et d\'autre."\n)\n\n# ---------------------------------------------------------------- Tranches d\'âge natives\nst.subheader("Répartition par tranche d\'âge de la mère (tranches de 5 ans)")\nordre_libelles = (\n    tr[["ordre_tranche", "tranche_age_libelle"]].drop_duplicates().sort_values("ordre_tranche")["tranche_age_libelle"].tolist()\n)\nonglet_temps, onglet_annee = st.tabs(["Dans le temps", "Une année"])\n\nwith onglet_temps:\n    aire = (\n        alt.Chart(tr)\n        .mark_area()\n        .encode(\n            x=alt.X("annee:Q", title="Année", axis=alt.Axis(format="d"),\n                    scale=alt.Scale(domain=[int(premiere.annee), int(derniere.annee)])),\n            y=alt.Y("part_pct:Q", title="Part des naissances (%)", stack="zero"),\n            color=alt.Color("tranche_age_libelle:N", title="Tranche d\'âge", sort=ordre_libelles,\n                            scale=alt.Scale(domain=ordre_libelles)),\n            order=alt.Order("ordre_tranche:Q"),\n            tooltip=[alt.Tooltip("annee:Q", title="Année", format="d"),\n                     alt.Tooltip("tranche_age_libelle:N", title="Tranche"),\n                     alt.Tooltip("part_pct:Q", title="Part (%)", format=".2f")],\n        )\n    )\n    st.altair_chart(aire, width="stretch")\n\nwith onglet_annee:\n    annee_choisie = st.slider(\n        "Année", int(premiere.annee), int(derniere.annee), int(derniere.annee), step=1\n    )\n    tranche_annee = tr[tr["annee"] == annee_choisie]\n    histogramme = (\n        alt.Chart(tranche_annee)\n        .mark_bar()\n        .encode(\n            x=alt.X("tranche_age_libelle:N", sort=ordre_libelles, title="Tranche d\'âge de la mère",\n                    axis=alt.Axis(labelAngle=-30)),\n            y=alt.Y("part_pct:Q", title="Part des naissances (%)"),\n            tooltip=[alt.Tooltip("tranche_age_libelle:N", title="Tranche"),\n                     alt.Tooltip("nb_naissances:Q", title="Naissances", format=","),\n                     alt.Tooltip("part_pct:Q", title="Part (%)", format=".2f")],\n        )\n    )\n    st.altair_chart(histogramme, width="stretch")\n    if annee_choisie in annees_incompletes:\n        st.info(\n            f"{annee_choisie} : la tranche des 50 ans et plus est absente des données du CDC "\n            "(âges de 50 ans et plus imputés jusqu\'en 1996, limite L7). "\n            "La part des 40 ans et plus est très légèrement sous-estimée."\n        )\n\n# ---------------------------------------------------------------- Éducation\nst.subheader("Niveau d\'éducation de la mère")\ncov_fenetre = cov[cov["fenetre_analyse"] == FENETRE_EDUCATION]\nst.caption(\n    "Le CDC ne fournit pas de catégorie socioprofessionnelle : l\'éducation sert de substitut du niveau socio-économique. "\n    f"Période {FENETRE_EDUCATION} : tous les États utilisent le certificat de naissance de 2003, "\n    f"et le niveau d\'éducation est connu pour {fr(cov_fenetre.couverture_pct.min())} à {fr(cov_fenetre.couverture_pct.max())} % des naissances. "\n    "Avant 2016, les certificats de 1989 et de 2003 coexistent et ne sont pas comparables."\n)\n\nef = edu_fenetre[edu_fenetre["fenetre_analyse"] == FENETRE_EDUCATION].sort_values("ordre_groupe")\nordre_groupes = ef["groupe_education"].tolist()\nst.markdown(f"**Niveau d\'éducation : toutes les mères et mères de 35+ ({FENETRE_EDUCATION})**")\ncompare = ef.melt(\n    id_vars=["groupe_education", "ordre_groupe"],\n    value_vars=["part_dans_toutes_meres_pct", "part_dans_meres_35_plus_pct"],\n    var_name="population", value_name="part",\n)\ncompare["population"] = compare["population"].map(\n    {"part_dans_toutes_meres_pct": "Toutes les mères", "part_dans_meres_35_plus_pct": "Mères de 35 ans et plus"}\n)\nbarres_cmp = (\n    alt.Chart(compare)\n    .mark_bar()\n    .encode(\n        y=alt.Y("groupe_education:N", sort=ordre_groupes, title=None),\n        x=alt.X("part:Q", title="Répartition (%)"),\n        yOffset="population:N",\n        color=alt.Color("population:N", title=None),\n        tooltip=[alt.Tooltip("groupe_education:N", title="Éducation"),\n                 alt.Tooltip("population:N", title="Population"),\n                 alt.Tooltip("part:Q", title="Part (%)", format=".1f")],\n    )\n)\nst.altair_chart(barres_cmp, width="stretch")\n\n# ---------------------------------------------------------------- Qualité\nwith st.expander("Qualité des données et limites"):\n    concept = ind["concept_age"].iloc[0]\n    st.markdown(\n        f"""\n- **Concept d\'âge** : `{concept}` (âge au dernier anniversaire, d\'après la définition CDC/NCHS).\n- **Contrôles** : données validées avant chargement (Great Expectations) puis après transformation (tests dbt).\n- **Années avec données incomplètes** : {", ".join(str(a) for a in annees_incompletes) or "aucune"} (tranche 50 ans et plus absente, L7).\n- **Rupture 2006-2007** : changement de base WONDER et des règles d\'imputation de l\'âge (L5, L8), non quantifié.\n- **Cellules supprimées** : écart de 0,01 à 0,03 % sur les totaux (L4).\n- **Niveau national uniquement** : pas de détail par État (L6).\n- **Éducation** : analyse limitée à 2016-2024, période où tous les États utilisent le certificat de 2003. Avant, les certificats de 1989 et de 2003 ne sont pas comparables et la couverture est partielle (L9).\n- **Pas de catégorie socioprofessionnelle** dans CDC WONDER (L10). Les niveaux d\'éducation sont regroupés en 4 groupes (docs/06_education_harmonisation.md).\n        """\n    )\n\nwith st.expander("Données"):\n    st.dataframe(ind, width="stretch", hide_index=True)\n', 'app/requirements.txt': 'streamlit\npandas\naltair\n', 'scripts/05_exporter_dashboard_csv.py': '"""Exporte les tables dbt utilisées par le dashboard vers app/data/*.csv (BigQuery -> CSV), avec la date de l\'instantané.\n\nUsage : export GCP_PROJECT=$(gcloud config get-value project) ; python scripts/05_exporter_dashboard_csv.py\nLes fichiers app/data/*.csv sont versionnés : ils alimentent le dashboard publié (Streamlit Community Cloud).\n"""\nimport os\nfrom datetime import date\nfrom pathlib import Path\n\nimport pandas as pd\nfrom google.cloud import bigquery\n\nDATASET = "naissances_dbt"\nTABLES = {\n    "indicateurs": "mart_naissances_tardives_indicateurs",\n    "tranches": "mart_naissances_tranches_natives",\n    "couverture": "mart_education_couverture",\n    "edu_fenetre": "mart_education_par_fenetre",\n}\n\nprojet = os.environ["GCP_PROJECT"]\nclient = bigquery.Client(project=projet)\nsortie = Path("app/data")\nsortie.mkdir(parents=True, exist_ok=True)\n\nfor cle, table in TABLES.items():\n    sql = f"SELECT * FROM `{projet}.{DATASET}.{table}`"\n    df = pd.DataFrame([dict(ligne) for ligne in client.query(sql).result()])\n    df.to_csv(sortie / f"{cle}.csv", index=False)\n    print(f"{cle}.csv : {len(df)} lignes")\n\n(sortie / "instantane.txt").write_text(date.today().isoformat() + "\\n", encoding="utf-8")\nprint("instantane.txt :", date.today().isoformat())\n'}


SECTION_TITRE = "## Dashboard en ligne"
SECTION = """## Dashboard en ligne

Dashboard en ligne : {lien}

Le dashboard publié lit un instantané des tables dbt (`app/data/*.csv`), exporté depuis BigQuery avec
`python scripts/05_exporter_dashboard_csv.py`. En local avec BigQuery : `export GCP_PROJECT=...` puis `streamlit run app/dashboard.py`.

"""
LIGNE_LIEN = re.compile(r"^Dashboard en ligne : .*$", re.M)

# 1) fichiers
if URL is None:
    for chemin, contenu in sorted(FICHIERS.items()):
        p = Path(chemin)
        existait = p.exists()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(contenu, encoding="utf-8")
        print(("REMPLACE " if existait else "CREE     ") + chemin)

    # 2) .gitignore : « data/ » ignorerait aussi app/data/ ; on limite à la racine
    gi = Path(".gitignore")
    if gi.exists():
        texte = gi.read_text(encoding="utf-8")
        lignes = texte.splitlines()
        if "data/" in lignes:
            lignes = ["/data/" if l == "data/" else l for l in lignes]
            gi.write_text("\n".join(lignes) + "\n", encoding="utf-8")
            print("MODIFIE  .gitignore (data/ devient /data/ : app/data/ sera versionné)")
        else:
            print("OK       .gitignore (rien à changer)")
    else:
        print("ABSENT   .gitignore : lance d'abord 07_prepare_github.py")

# 3) README
readme = Path("README.md")
if not readme.exists():
    print("ABSENT   README.md : lance d'abord 07_prepare_github.py")
else:
    texte = readme.read_text(encoding="utf-8")
    lien = f"[{URL}]({URL})" if URL else "(lien à ajouter après le déploiement)"
    if SECTION_TITRE in texte:
        if URL:
            texte = LIGNE_LIEN.sub(lambda m: f"Dashboard en ligne : {lien}", texte, count=1)
            readme.write_text(texte, encoding="utf-8")
            print("MODIFIE  README.md (lien du dashboard mis à jour)")
        else:
            print("DEJA FAIT README.md (section Dashboard en ligne)")
    else:
        bloc = SECTION.format(lien=lien)
        if "## Question" in texte:
            texte = texte.replace("## Question", bloc + "## Question", 1)
        else:
            texte = texte.rstrip("\n") + "\n\n" + bloc
        readme.write_text(texte, encoding="utf-8")
        print("AJOUTE   README.md (section Dashboard en ligne)")

if URL is None:
    print("\nSuite : python scripts/05_exporter_dashboard_csv.py (avec GCP_PROJECT défini) pour créer app/data/*.csv")
