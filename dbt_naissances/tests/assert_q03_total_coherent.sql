with stg as (
    select annee, sum(nb_naissances) as total
    from {{ ref('stg_cdc_naissances') }}
    group by annee
),
mart as (
    select annee, sum(nb_naissances) as total
    from {{ ref('mart_naissances_par_tranche') }}
    group by annee
)
select stg.annee, stg.total as total_staging, mart.total as total_mart
from stg
left join mart on stg.annee = mart.annee
where mart.total is null or stg.total != mart.total
