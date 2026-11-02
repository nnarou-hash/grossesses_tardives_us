-- Éducation harmonisée : niveaux natifs (certificats 1989 et 2003) regroupés en 4 groupes
-- via le seed ref_education_harmonisation, croisés avec la tranche d'âge harmonisée.

select
    e.zone_code,
    e.zone_type,
    e.annee,
    {{ tranche_age_harmonisee('e.tranche_age_native') }} as tranche_age,
    r.certificat,
    r.groupe_education,
    r.ordre_groupe,
    r.statut_education,
    sum(e.nb_naissances) as nb_naissances
from {{ ref('stg_cdc_naissances_education') }} as e
left join {{ ref('ref_education_harmonisation') }} as r
    on e.education_native = r.education_native
group by 1, 2, 3, 4, 5, 6, 7, 8
