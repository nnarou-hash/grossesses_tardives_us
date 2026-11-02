-- Q08 : chaque année des fenêtres d'analyse contient les 4 groupes d'éducation.
select annee, count(distinct groupe_education) as nb_groupes
from {{ ref('mart_education_par_annee') }}
group by annee
having count(distinct groupe_education) != 4
