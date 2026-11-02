# Registre des limites méthodologiques

| # | Limite | Impact | Mesure prise |
|---|---|---|---|
| L1 | Rénovation des bulletins d'état civil INSEE en 2023 | Rupture possible de la série à partir de 2023 | Signaler 2023-2024 dans le dashboard |
| L2 | Concept d'âge variable selon les pays Eurostat | Écart léger sur les tranches 35+/40+ | Colonne « concept_age » par ligne |
| L3 | Table BigQuery CDC limitée à 2008 | Impossible de couvrir 1995-2024 avec elle | Utiliser CDC WONDER |
| L4 | Cellules supprimées (petits effectifs) dans les exports WONDER croisés | Écart de 0,01 à 0,03 % sur les totaux | Chiffré en règle Q03 |
| L5 | Décrochage entre 2006 et 2007 (14,32 % à 14,19 % de naissances 35+), changement de base WONDER | Rupture potentielle de série | Cause à investiguer, à signaler dans le dashboard |
| L6 | CDC : grain national uniquement (pas d'État) | Pas de comparaison infranationale États-Unis | Extension possible plus tard |
| L7 | CDC : tranche « 50 ans et plus » absente en 1995 et 1996 (règle CDC : jusqu'en 1996, les âges de 50 ans et plus sont traités comme non déclarés et imputés) | Part des 40+ légèrement sous-estimée sur ces 2 années (effectif de l'ordre de la centaine) | Absence conservée et signalée, pas de remplissage par 0 |
| L8 | CDC : règles d'imputation de l'âge modifiées en 2003 (nouveau certificat), puis en 2007 (tous les certificats) | Piste possible pour le décrochage 2006-2007 (L5), non démontrée | Signaler dans le dashboard, à vérifier |
| L9 | CDC : l'éducation des certificats de naissance de 1989 et de 2003 n'est pas comparable ; WONDER recode en « Excluded » selon l'État. Couverture de 50 à 99 % selon l'année | Pas de série continue d'éducation 1995-2024 | Analyse limitée aux fenêtres 1995-2002 et 2016-2024, couverture publiée (mart_education_couverture) |
| L10 | CDC WONDER ne fournit pas de profession ni de catégorie socioprofessionnelle | Le niveau socio-économique est approché par l'éducation uniquement | Éducation utilisée comme substitut, limite affichée dans le dashboard |
| L11 | Rapprochement approximatif des catégories d'éducation entre les deux certificats | Niveaux non comparables entre fenêtres | Comparaison des écarts à l'intérieur de chaque fenêtre uniquement (docs/06_education_harmonisation.md) |
