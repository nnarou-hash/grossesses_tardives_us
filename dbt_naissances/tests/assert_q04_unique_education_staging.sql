select annee, tranche_age_native, education_native, count(*) as nb
from {{ ref('stg_cdc_naissances_education') }}
group by annee, tranche_age_native, education_native
having count(*) > 1
