-- Harmonisation : 9 tranches natives CDC regroupées en <35, 35-39, 40+
-- (règle d'harmonisation décrite dans docs/02_matrice_sources.md ; macro tranche_age_harmonisee).

select
    zone_code,
    zone_type,
    annee,
    {{ tranche_age_harmonisee('tranche_age_native') }} as tranche_age,
    'CDC WONDER' as source_systeme,
    'revolu' as concept_age,
    sum(nb_naissances) as nb_naissances,
    count(*) as nb_tranches_natives
from {{ ref('stg_cdc_naissances') }}
group by 1, 2, 3, 4, 5, 6
