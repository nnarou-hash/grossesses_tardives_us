-- Répartition par tranche d'âge native (9 tranches de 5 ans), zone x année x tranche.

select
    zone_code,
    zone_type,
    annee,
    tranche_age_native,
    case tranche_age_native
        when 'Under 15 years'    then 1
        when '15-19 years'       then 2
        when '20-24 years'       then 3
        when '25-29 years'       then 4
        when '30-34 years'       then 5
        when '35-39 years'       then 6
        when '40-44 years'       then 7
        when '45-49 years'       then 8
        when '50 years and over' then 9
    end as ordre_tranche,
    case tranche_age_native
        when 'Under 15 years'    then 'Moins de 15 ans'
        when '15-19 years'       then '15-19 ans'
        when '20-24 years'       then '20-24 ans'
        when '25-29 years'       then '25-29 ans'
        when '30-34 years'       then '30-34 ans'
        when '35-39 years'       then '35-39 ans'
        when '40-44 years'       then '40-44 ans'
        when '45-49 years'       then '45-49 ans'
        when '50 years and over' then '50 ans et plus'
    end as tranche_age_libelle,
    nb_naissances,
    round(
        100 * nb_naissances
        / nullif(sum(nb_naissances) over (partition by zone_code, annee), 0),
        2
    ) as part_pct,
    count(*) over (partition by zone_code, annee) < {{ var('nb_tranches_natives_attendu') }} as donnee_incomplete
from {{ ref('stg_cdc_naissances') }}
