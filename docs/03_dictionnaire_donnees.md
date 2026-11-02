# Dictionnaire de données : tables finales (États-Unis, CDC WONDER)

## mart_naissances_par_tranche (grain : zone x année x tranche d'âge)

| Colonne | Type | Description | Valeurs attendues | Source(s) | Règle de calcul | Propriétaire |
|---|---|---|---|---|---|---|
| zone_code | STRING | Code de la zone | US | CDC WONDER | Valeur fixe pour l'instant | Nellyta |
| zone_type | STRING | Type de zone | pays | CDC WONDER | Valeur fixe pour l'instant | Nellyta |
| annee | INT64 | Année de naissance | 1995 à 2024 | CDC WONDER | Telle que fournie | Nellyta |
| tranche_age | STRING | Tranche d'âge harmonisée de la mère | <35, 35-39, 40+ | CDC WONDER | Regroupement des 9 tranches natives (voir 02_matrice_sources.md) | Nellyta |
| nb_naissances | INT64 | Naissances vivantes | >= 0 | CDC WONDER | Somme des tranches natives regroupées | Nellyta |
| part_pct | FLOAT64 | Part de la tranche dans les naissances de l'année | 0 à 100 | Calcul | 100 x nb_naissances / total de l'année, arrondi à 2 décimales | Nellyta |
| source_systeme | STRING | Système source | CDC WONDER | Constante | Traçabilité | Nellyta |
| concept_age | STRING | Concept d'âge utilisé par la source | revolu (CDC) | Matrice des sources | Âge au dernier anniversaire, d'après CDC/NCHS (Health, United States) | Nellyta |
| donnee_incomplete | BOOL | Moins de 9 tranches natives présentes pour l'année | true en 1995 et 1996 | Calcul | Somme des tranches natives < 9 (voir L7) | Nellyta |

## mart_naissances_tardives_indicateurs (grain : zone x année)

| Colonne | Type | Description | Règle de calcul |
|---|---|---|---|
| nb_naissances_total | INT64 | Naissances vivantes de l'année | Somme des tranches |
| nb_naissances_35_plus | INT64 | Naissances dont la mère a 35 ans ou plus | Tranches 35-39 et 40+ |
| nb_naissances_40_plus | INT64 | Naissances dont la mère a 40 ans ou plus | Tranche 40+ |
| part_35_plus_pct | FLOAT64 | Part des naissances à 35+ | 100 x 35+ / total, 2 décimales |
| part_40_plus_pct | FLOAT64 | Part des naissances à 40+ | 100 x 40+ / total, 2 décimales |
| donnee_incomplete | BOOL | Voir ci-dessus | Voir ci-dessus |

## mart_naissances_tranches_natives (grain : zone x année x tranche d'âge native)

| Colonne | Type | Description | Règle de calcul |
|---|---|---|---|
| tranche_age_native | STRING | Tranche d'âge CDC (9 tranches de 5 ans) | Telle que fournie |
| ordre_tranche | INT64 | Ordre d'affichage (1 à 9) | Correspondance fixe |
| tranche_age_libelle | STRING | Libellé français de la tranche | Correspondance fixe |
| nb_naissances | INT64 | Naissances vivantes | Somme des cellules WONDER |
| part_pct | FLOAT64 | Part de la tranche dans les naissances de l'année | 100 x nb / total de l'année |
| donnee_incomplete | BOOL | Une tranche native manque pour l'année | Vrai en 1995 et 1996 (L7) |

## mart_education_couverture (grain : zone x année)

| Colonne | Type | Description | Règle de calcul |
|---|---|---|---|
| nb_naissances_total | INT64 | Naissances vivantes de l'année | Somme |
| nb_education_exploitable | INT64 | Naissances avec un niveau d'éducation exploitable | Statut « exploitable » |
| nb_education_exclue | INT64 | Naissances recodées « Excluded » par WONDER | Statut « exclu » |
| nb_education_non_declaree | INT64 | Naissances sans éducation déclarée | Statut « non_declare » |
| couverture_pct | FLOAT64 | Part des naissances avec éducation exploitable | 100 x exploitable / total |
| fenetre_analyse | STRING | 1995-2002, 2016-2024 ou hors_fenetre | Variables dbt, décision D2 |

## mart_education_par_annee (grain : zone x année x groupe d'éducation, fenêtres uniquement)

| Colonne | Type | Description | Règle de calcul |
|---|---|---|---|
| groupe_education | STRING | Moins du lycée, Lycée, Études supérieures sans licence, Licence ou plus | Seed ref_education_harmonisation |
| certificat | STRING | cert_1989 ou cert_2003 | Seed |
| nb_naissances_35_plus | INT64 | Naissances dont la mère a 35 ans ou plus | Tranches 35-39 et 40+ |
| part_35_plus_pct | FLOAT64 | Part de naissances à 35+ dans le groupe | 100 x 35+ / naissances du groupe |

## mart_education_par_fenetre (grain : zone x fenêtre x groupe d'éducation)

| Colonne | Type | Description | Règle de calcul |
|---|---|---|---|
| part_35_plus_pct | FLOAT64 | Part de naissances à 35+ dans le groupe, sur la fenêtre | 100 x 35+ / naissances du groupe |
| part_dans_toutes_meres_pct | FLOAT64 | Poids du groupe parmi toutes les mères | 100 x naissances du groupe / total fenêtre |
| part_dans_meres_35_plus_pct | FLOAT64 | Poids du groupe parmi les mères de 35+ | 100 x 35+ du groupe / total 35+ fenêtre |

Niveaux non comparables entre fenêtres (L11).
