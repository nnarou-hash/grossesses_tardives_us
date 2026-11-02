select zone_code, annee, tranche_age, count(*) as nb
from {{ ref('mart_naissances_par_tranche') }}
group by zone_code, annee, tranche_age
having count(*) > 1
