-- Agrégat par fenêtre d'analyse et groupe d'éducation :
--  - part_35_plus_pct : part de naissances à 35+ dans le groupe
--  - part_dans_toutes_meres_pct : poids du groupe parmi toutes les mères
--  - part_dans_meres_35_plus_pct : poids du groupe parmi les mères de 35+
-- Les niveaux ne sont pas comparables d'une fenêtre à l'autre (définitions d'éducation différentes).

with fenetre as (
    select
        zone_code,
        zone_type,
        fenetre_analyse,
        certificat,
        groupe_education,
        ordre_groupe,
        sum(nb_naissances) as nb_naissances,
        sum(nb_naissances_35_plus) as nb_naissances_35_plus
    from {{ ref('mart_education_par_annee') }}
    group by zone_code, zone_type, fenetre_analyse, certificat, groupe_education, ordre_groupe
)

select
    zone_code,
    zone_type,
    fenetre_analyse,
    certificat,
    groupe_education,
    ordre_groupe,
    nb_naissances,
    nb_naissances_35_plus,
    round(100 * nb_naissances_35_plus / nullif(nb_naissances, 0), 2) as part_35_plus_pct,
    round(
        100 * nb_naissances
        / nullif(sum(nb_naissances) over (partition by zone_code, fenetre_analyse), 0),
        2
    ) as part_dans_toutes_meres_pct,
    round(
        100 * nb_naissances_35_plus
        / nullif(sum(nb_naissances_35_plus) over (partition by zone_code, fenetre_analyse), 0),
        2
    ) as part_dans_meres_35_plus_pct
from fenetre
