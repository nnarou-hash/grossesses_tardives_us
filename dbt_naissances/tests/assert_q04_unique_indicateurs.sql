select zone_code, annee, count(*) as nb
from {{ ref('mart_naissances_tardives_indicateurs') }}
group by zone_code, annee
having count(*) > 1
