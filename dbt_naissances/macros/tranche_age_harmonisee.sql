{# Regroupe les 9 tranches d'âge natives CDC en <35, 35-39, 40+ (docs/02_matrice_sources.md). #}
{% macro tranche_age_harmonisee(colonne) %}
    case {{ colonne }}
        when 'Under 15 years'     then '<35'
        when '15-19 years'        then '<35'
        when '20-24 years'        then '<35'
        when '25-29 years'        then '<35'
        when '30-34 years'        then '<35'
        when '35-39 years'        then '35-39'
        when '40-44 years'        then '40+'
        when '45-49 years'        then '40+'
        when '50 years and over'  then '40+'
        else 'non_classe'
    end
{% endmacro %}
