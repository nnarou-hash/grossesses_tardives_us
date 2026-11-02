import sys
import pandas as pd
import great_expectations as gx
import great_expectations.expectations as gxe
from great_expectations.checkpoint import UpdateDataDocsAction

CSV = "data/cdc/cdc_naissances_age_annee.csv"
TRANCHES = ["Under 15 years", "15-19 years", "20-24 years", "25-29 years", "30-34 years",
            "35-39 years", "40-44 years", "45-49 years", "50 years and over"]

df = pd.read_csv(CSV)
context = gx.get_context(mode="file", project_root_dir=".")

source = context.data_sources.add_or_update_pandas(name="cdc_pandas")
try:
    asset = source.get_asset("cdc_naissances")
except Exception:
    asset = source.add_dataframe_asset(name="cdc_naissances")
try:
    batch_def = asset.get_batch_definition("table_complete")
except Exception:
    batch_def = asset.add_batch_definition_whole_dataframe("table_complete")

expectations = [
    # Q01 Complétude
    gxe.ExpectColumnValuesToNotBeNull(column="zone_code"),
    gxe.ExpectColumnValuesToNotBeNull(column="annee"),
    gxe.ExpectColumnValuesToNotBeNull(column="tranche_age_native"),
    gxe.ExpectColumnValuesToNotBeNull(column="nb_naissances"),
    # Validité
    gxe.ExpectColumnValuesToBeInSet(column="zone_type", value_set=["pays"]),
    gxe.ExpectColumnValuesToBeBetween(column="annee", min_value=1995, max_value=2024),
    gxe.ExpectColumnValuesToBeInSet(column="tranche_age_native", value_set=TRANCHES),
    # Q02 nb_naissances >= 0
    gxe.ExpectColumnValuesToBeBetween(column="nb_naissances", min_value=0),
    # Q04 Unicité année x tranche
    gxe.ExpectCompoundColumnsToBeUnique(column_list=["annee", "tranche_age_native"]),
    # Q05 Complétude des tranches : 30 ans x 9 tranches = 270, exception documentée L7 (268)
    gxe.ExpectTableRowCountToBeBetween(min_value=268, max_value=270),
]

suite = context.suites.add_or_update(
    gx.ExpectationSuite(name="cdc_naissances_raw", expectations=expectations)
)
validation = context.validation_definitions.add_or_update(
    gx.ValidationDefinition(name="cdc_naissances_validation", data=batch_def, suite=suite)
)
checkpoint = context.checkpoints.add_or_update(
    gx.Checkpoint(
        name="cdc_naissances_checkpoint",
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

context.build_data_docs()
print("Data Docs :", "gx/uncommitted/data_docs/local_site/index.html")
sys.exit(0 if result.success else 1)
