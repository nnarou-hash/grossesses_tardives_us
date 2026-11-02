-- Q07 : le total annuel des naissances est identique dans les données éducation et dans les données par âge.
with edu as (
    select annee, sum(nb_naissances) as total
    from {{ ref('stg_cdc_naissances_education') }}
    group by annee
),
age as (
    select annee, sum(nb_naissances) as total
    from {{ ref('stg_cdc_naissances') }}
    group by annee
)
select edu.annee, edu.total as total_education, age.total as total_age
from edu
left join age on edu.annee = age.annee
where age.total is null or edu.total != age.total
