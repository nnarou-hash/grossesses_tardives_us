select annee, tranche_age_native, count(*) as nb
from {{ ref('stg_cdc_naissances') }}
group by annee, tranche_age_native
having count(*) > 1
