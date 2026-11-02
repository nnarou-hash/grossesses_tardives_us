-- Parts entre 0 et 100, et poids des groupes totalisant 100 % par fenêtre (tolérance d'arrondi 0,1).
select fenetre_analyse, 'part_hors_bornes' as probleme
from {{ ref('mart_education_par_fenetre') }}
where part_35_plus_pct not between 0 and 100
   or part_dans_toutes_meres_pct not between 0 and 100
   or part_dans_meres_35_plus_pct not between 0 and 100
union all
select fenetre_analyse, 'somme_toutes_meres_differente_de_100' as probleme
from {{ ref('mart_education_par_fenetre') }}
group by fenetre_analyse
having abs(sum(part_dans_toutes_meres_pct) - 100) > 0.1
union all
select fenetre_analyse, 'somme_meres_35_plus_differente_de_100' as probleme
from {{ ref('mart_education_par_fenetre') }}
group by fenetre_analyse
having abs(sum(part_dans_meres_35_plus_pct) - 100) > 0.1
