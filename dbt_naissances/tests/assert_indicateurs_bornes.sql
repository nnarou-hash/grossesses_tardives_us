select *
from {{ ref('mart_naissances_tardives_indicateurs') }}
where part_35_plus_pct not between 0 and 100
   or part_40_plus_pct not between 0 and 100
   or part_40_plus_pct > part_35_plus_pct
