-- Q06 : les fenêtres d'analyse ont une couverture >= seuil, les années hors fenêtre une couverture < seuil.
select annee, couverture_pct, fenetre_analyse
from {{ ref('mart_education_couverture') }}
where (fenetre_analyse != 'hors_fenetre' and couverture_pct < {{ var('seuil_couverture_education') }})
   or (fenetre_analyse = 'hors_fenetre' and couverture_pct >= {{ var('seuil_couverture_education') }})
