-- Couverture de l'éducation par année : part des naissances dont le niveau d'éducation est exploitable
-- (ni « Exclu » par WONDER, ni non déclaré). Justifie le choix des fenêtres d'analyse.

with base as (
    select
        zone_code,
        zone_type,
        annee,
        sum(nb_naissances) as nb_naissances_total,
        sum(case when statut_education = 'exploitable' then nb_naissances else 0 end) as nb_education_exploitable,
        sum(case when statut_education = 'exclu' then nb_naissances else 0 end) as nb_education_exclue,
        sum(case when statut_education = 'non_declare' then nb_naissances else 0 end) as nb_education_non_declaree
    from {{ ref('int_cdc_naissances_education_harmonisees') }}
    group by zone_code, zone_type, annee
)

select
    zone_code,
    zone_type,
    annee,
    nb_naissances_total,
    nb_education_exploitable,
    nb_education_exclue,
    nb_education_non_declaree,
    round(100 * nb_education_exploitable / nullif(nb_naissances_total, 0), 2) as couverture_pct,
    {{ fenetre_analyse('annee') }} as fenetre_analyse
from base
