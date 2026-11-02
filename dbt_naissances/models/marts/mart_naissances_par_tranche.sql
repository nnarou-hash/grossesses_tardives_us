-- Table finale (grain zone x année x tranche d'âge), avec la part de chaque tranche.

select
    zone_code,
    zone_type,
    annee,
    tranche_age,
    nb_naissances,
    round(
        100 * nb_naissances
        / nullif(sum(nb_naissances) over (partition by zone_code, annee), 0),
        2
    ) as part_pct,
    source_systeme,
    concept_age,
    sum(nb_tranches_natives) over (partition by zone_code, annee)
        < {{ var('nb_tranches_natives_attendu') }} as donnee_incomplete
from {{ ref('int_cdc_naissances_harmonisees') }}
