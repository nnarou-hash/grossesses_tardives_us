-- Staging : une ligne par année x tranche d'âge native (CDC WONDER).
-- Seuls les types sont fixés et les colonnes renommées ; aucune règle métier ici.

select
    cast(zone_code as string)            as zone_code,
    cast(zone_type as string)            as zone_type,
    cast(annee as int64)                 as annee,
    cast(tranche_age_native as string)   as tranche_age_native,
    cast(nb_naissances as int64)         as nb_naissances,
    cast(source_base as string)          as source_base
from {{ source('naissances_raw', 'cdc_naissances_age_annee') }}
