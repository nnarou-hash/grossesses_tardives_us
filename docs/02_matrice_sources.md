# Matrice de correspondance des définitions

| Concept | INSEE (France) | Eurostat (Europe) | CDC (États-Unis) | Règle d'harmonisation |
|---|---|---|---|---|
| Unité | Naissances vivantes | Naissances vivantes (signe de vie, hors mort-nés) | Naissances vivantes aux résidentes US | Naissances vivantes |
| Âge de la mère (mode de calcul) | Atteint dans l'année (AGEMERE, T48) et révolu (AGEXACTM, T48bis) | Révolu et/ou atteint selon le pays | Révolu (âge au dernier anniversaire) ; âge déclaré si date de naissance manquante (CDC/NCHS, Health, United States, définition Age) | Révolu en priorité, concept indiqué par ligne |
| Tranches d'âge natives | Âge unique (fichier 2024 : <=17, 18-45, 46+) ; tableaux : 35-39, 40-44, 45-49, 50+ | demo_r_fagec3 : tranches de 5 ans ; autres tables à vérifier | Tranches de 5 ans (WONDER) ; âge unique (fichiers détail) | <35, 35-39, 40+ |
| Niveau géographique | Département de domicile de la mère | Pays, NUTS 2, NUTS 3 | État, comté | Zone + type de zone |
| Années disponibles | Âge : 1994+ (France entière) ; détail jusqu'en 2024 | NUTS 2 : 1990-2023 (à vérifier) ; pays à vérifier | WONDER 1995-2024 ; BigQuery 1969-2008 (à vérifier) | 1995-2024 |
| Lieu : résidence ou occurrence | Naissances en France, domicile de la mère disponible | Région de résidence de la mère | Résidence de la mère | Résidence |
| Licence / réutilisation | À vérifier | À vérifier | Conditions d'usage CDC WONDER à lire | |

## Sources consultées
- INSEE, Les naissances en 2020 (définitions) : https://www.insee.fr/fr/statistiques/5414771
- INSEE, contenu du fichier 2024 : https://www.insee.fr/fr/statistiques/fichier/8610295/Contenu_etatcivil2024_nais2024.pdf
- INSEE, séries longues T48/T48bis : https://www.insee.fr/fr/statistiques/2046492
- Eurostat, métadonnées fertilité : https://ec.europa.eu/eurostat/cache/metadata/en/demo_fer_esms.htm
- CDC WONDER, natalité : https://wonder.cdc.gov/wonder/help/natality.html
- Google, CDC Birth Vital Statistics in BigQuery (2012) : https://research.google/blog/cdc-birth-vital-statistics-in-bigquery/
- CDC/NCHS, Health, United States, définition de l'âge : https://www.cdc.gov/nchs/hus/sources-definitions/age.htm
