-- Indicateurs par zone et par année : part des naissances à 35+ et à 40+.

select
    zone_code,
    zone_type,
    annee,
    sum(nb_naissances) as nb_naissances_total,
    sum(case when tranche_age in ('35-39', '40+') then nb_naissances else 0 end) as nb_naissances_35_plus,
    sum(case when tranche_age = '40+' then nb_naissances else 0 end) as nb_naissances_40_plus,
    round(
        100 * sum(case when tranche_age in ('35-39', '40+') then nb_naissances else 0 end)
        / nullif(sum(nb_naissances), 0),
        2
    ) as part_35_plus_pct,
    round(
        100 * sum(case when tranche_age = '40+' then nb_naissances else 0 end)
        / nullif(sum(nb_naissances), 0),
        2
    ) as part_40_plus_pct,
    source_systeme,
    concept_age,
    sum(nb_tranches_natives) < {{ var('nb_tranches_natives_attendu') }} as donnee_incomplete
from {{ ref('int_cdc_naissances_harmonisees') }}
group by zone_code, zone_type, annee, source_systeme, concept_age
