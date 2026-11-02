select 'par_annee' as mart, zone_code, annee as cle, groupe_education, count(*) as nb
from {{ ref('mart_education_par_annee') }}
group by zone_code, annee, groupe_education
having count(*) > 1
union all
select 'par_fenetre' as mart, zone_code, cast(null as int) as cle, groupe_education, count(*) as nb
from {{ ref('mart_education_par_fenetre') }}
group by zone_code, fenetre_analyse, groupe_education
having count(*) > 1
