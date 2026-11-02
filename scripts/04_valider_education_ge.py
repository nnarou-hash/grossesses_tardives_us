"""Validation Great Expectations des données brutes éducation (CDC WONDER) avant chargement."""
import sys

import great_expectations as gx
import great_expectations.expectations as gxe
import pandas as pd
from great_expectations.checkpoint import UpdateDataDocsAction

CSV = "data/cdc/cdc_naissances_age_education_annee.csv"
TRANCHES = ["Under 15 years", "15-19 years", "20-24 years", "25-29 years", "30-34 years",
            "35-39 years", "40-44 years", "45-49 years", "50 years and over"]
EDUCATIONS = [
    "0 -  8 years", "9 - 11 years", "12 years", "13 - 15 years", "16 years and over",
    "Not stated/Not on certificate", "Excluded",
    "8th grade or less", "9th through 12th grade with no diploma",
    "High school graduate or GED completed", "Some college credit, but not a degree",
    "Associate degree (AA, AS)", "Bachelor's degree (BA, AB, BS)",
    "Master's degree (MA, MS, MEng, MEd, MSW, MBA)",
    "Doctorate (PhD, EdD) or Professional Degree (MD, DDS, DVM, LLB, JD)",
    "Unknown or Not Stated",
]

df = pd.read_csv(CSV)
context = gx.get_context(mode="file", project_root_dir=".")

source = context.data_sources.add_or_update_pandas(name="cdc_pandas")
try:
    asset = source.get_asset("cdc_education")
except Exception:
    asset = source.add_dataframe_asset(name="cdc_education")
try:
    batch_def = asset.get_batch_definition("table_complete")
except Exception:
    batch_def = asset.add_batch_definition_whole_dataframe("table_complete")

expectations = [
    gxe.ExpectColumnValuesToNotBeNull(column="zone_code"),
    gxe.ExpectColumnValuesToNotBeNull(column="annee"),
    gxe.ExpectColumnValuesToNotBeNull(column="tranche_age_native"),
    gxe.ExpectColumnValuesToNotBeNull(column="education_native"),
    gxe.ExpectColumnValuesToNotBeNull(column="nb_naissances"),
    gxe.ExpectColumnValuesToBeInSet(column="zone_type", value_set=["pays"]),
    gxe.ExpectColumnValuesToBeBetween(column="annee", min_value=1995, max_value=2024),
    gxe.ExpectColumnValuesToBeInSet(column="tranche_age_native", value_set=TRANCHES),
    gxe.ExpectColumnValuesToBeInSet(column="education_native", value_set=EDUCATIONS),
    gxe.ExpectColumnValuesToBeBetween(column="nb_naissances", min_value=0),
    gxe.ExpectCompoundColumnsToBeUnique(column_list=["annee", "tranche_age_native", "education_native"]),
]

suite = context.suites.add_or_update(gx.ExpectationSuite(name="cdc_education_raw", expectations=expectations))
validation = context.validation_definitions.add_or_update(
    gx.ValidationDefinition(name="cdc_education_validation", data=batch_def, suite=suite)
)
checkpoint = context.checkpoints.add_or_update(
    gx.Checkpoint(
        name="cdc_education_checkpoint",
        validation_definitions=[validation],
        actions=[UpdateDataDocsAction(name="maj_data_docs")],
    )
)

result = checkpoint.run(batch_parameters={"dataframe": df})
print("Succès global :", result.success)
for vr in result.run_results.values():
    for r in vr.results:
        cfg = r.expectation_config
        col = cfg.kwargs.get("column", cfg.kwargs.get("column_list", ""))
        print(("OK  " if r.success else "KO  "), cfg.type, col)
        if not r.success:
            inattendu = r.result.get("partial_unexpected_list")
            if inattendu:
                print("     valeurs inattendues :", inattendu[:5])

context.build_data_docs()
print("Data Docs : gx/uncommitted/data_docs/local_site/index.html")
sys.exit(0 if result.success else 1)
