select zone_code, annee, sum(part_pct) as somme_parts
from {{ ref('mart_naissances_par_tranche') }}
group by zone_code, annee
having abs(sum(part_pct) - 100) > 0.1
