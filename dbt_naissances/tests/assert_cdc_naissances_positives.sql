select *
from {{ ref('stg_cdc_naissances') }}
where nb_naissances < 0
