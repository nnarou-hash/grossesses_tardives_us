-- Part des naissances à 35 ans et plus dans chaque groupe d'éducation, par année,
-- uniquement sur les fenêtres d'analyse à couverture complète.

select
    zone_code,
    zone_type,
    annee,
    {{ fenetre_analyse('annee') }} as fenetre_analyse,
    certificat,
    groupe_education,
    ordre_groupe,
    sum(nb_naissances) as nb_naissances,
    sum(case when tranche_age in ('35-39', '40+') then nb_naissances else 0 end) as nb_naissances_35_plus,
    round(
        100 * sum(case when tranche_age in ('35-39', '40+') then nb_naissances else 0 end)
        / nullif(sum(nb_naissances), 0),
        2
    ) as part_35_plus_pct
from {{ ref('int_cdc_naissances_education_harmonisees') }}
where statut_education = 'exploitable'
  and {{ fenetre_analyse('annee') }} != 'hors_fenetre'
group by zone_code, zone_type, annee, certificat, groupe_education, ordre_groupe
