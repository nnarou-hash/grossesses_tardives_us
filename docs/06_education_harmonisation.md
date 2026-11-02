# Éducation de la mère : harmonisation et décisions

## Contexte
- CDC WONDER fournit l'éducation de la mère (pas de profession ni de catégorie socioprofessionnelle). L'éducation sert de substitut du niveau socio-économique.
- Le CDC indique que l'éducation du certificat de naissance de 2003 n'est **pas comparable** à celle du certificat de 1989. WONDER recode donc en « Excluded » les naissances selon le certificat utilisé par l'État de résidence.
- 1995-2002 : tous les États utilisent le certificat de 1989. 2003-2006 : les États passés au certificat de 2003 sont exclus. 2007-2015 : les États restés au certificat de 1989 sont exclus. Depuis 2016 : tous les États utilisent le certificat de 2003.
- Nombre d'États ou zones exclus (documentation WONDER) : 2 en 2003, 19 en 2006, 30 en 2007, 2 en 2015, aucun depuis 2016.

## Décisions (validées)
| # | Décision | Justification |
|---|---|---|
| D1 | 4 groupes d'éducation : moins du lycée, lycée, études supérieures sans licence, licence ou plus | Rapprochement approximatif des deux certificats (voir table ci-dessous). Hypothèse documentée, car le CDC juge les deux certificats non comparables |
| D2 | Analyse sur deux fenêtres à couverture complète : 1995-2002 et 2016-2024. Les années 2003-2015 ne figurent que dans le graphique de couverture | Entre 2003 et 2015, l'éducation n'est disponible que pour un sous-ensemble d'États qui change chaque année (non aléatoire) |
| D3 | Indicateurs : part de naissances à 35+ dans chaque groupe d'éducation, et répartition par éducation des mères de 35+ | Mesure l'écart de maternité tardive selon le niveau d'éducation |

Règle d'usage : on compare les écarts **dans** une fenêtre, jamais les niveaux **entre** fenêtres.

## Table de correspondance (seed dbt : ref_education_harmonisation)
| Certificat 1989 (1995-2006) | Certificat 2003 (2007-2024) | Groupe harmonisé |
|---|---|---|
| 0-8 ans ; 9-11 ans | 8th grade or less ; 9th-12th grade, no diploma | Moins du lycée |
| 12 ans | High school graduate or GED | Lycée |
| 13-15 ans | Some college, no degree ; Associate degree | Études supérieures sans licence |
| 16 ans et plus | Bachelor ; Master ; Doctorate or professional degree | Licence ou plus |
| Not stated/Not on certificate | Unknown or Not Stated | Non déclaré (exclu des analyses) |
| Excluded | Excluded | Exclu (exclu des analyses) |

## Contrôles qualité associés
- Q06 : couverture >= 97 % dans les fenêtres d'analyse, < 97 % hors fenêtres (justifie D2).
- Q07 : le total annuel des naissances est identique entre les données éducation et les données par âge.
- Q08 : les 4 groupes d'éducation sont présents chaque année des fenêtres.

## Source
- CDC WONDER, documentation natalité (section Maternal Education) : https://wonder.cdc.gov/wonder/help/natality.html
