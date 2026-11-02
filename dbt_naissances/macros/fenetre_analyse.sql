{# Étiquette de la fenêtre d'analyse de l'éducation, selon l'année (variables dans dbt_project.yml). #}
{% macro fenetre_analyse(colonne) %}
    case
        when {{ colonne }} between {{ var('fenetre_1_debut') }} and {{ var('fenetre_1_fin') }}
            then '{{ var("fenetre_1_debut") }}-{{ var("fenetre_1_fin") }}'
        when {{ colonne }} between {{ var('fenetre_2_debut') }} and {{ var('fenetre_2_fin') }}
            then '{{ var("fenetre_2_debut") }}-{{ var("fenetre_2_fin") }}'
        else 'hors_fenetre'
    end
{% endmacro %}
