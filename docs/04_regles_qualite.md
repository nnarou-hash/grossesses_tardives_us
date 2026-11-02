# Règles de qualité

| ID | Dimension | Règle | Seuil | Outil | Gravité |
|---|---|---|---|---|---|
| Q01 | Complétude | zone_code non nul | 100 % | GE + dbt | Bloquante |
| Q02 | Validité | nb_naissances >= 0 | 100 % | GE + dbt | Bloquante |
| Q03 | Cohérence | somme des tranches = total de la zone | écart < 1 % | dbt | Alerte |
| Q04 | Unicité | un seul enregistrement par zone × année × tranche | 100 % | dbt | Bloquante |
| Q05 | Complétude | 9 tranches d'âge natives présentes par année (CDC) | 100 % | GE + dbt | Alerte (exception documentée : 50+ en 1995-1996, voir L7) |
| Q06 | Cohérence | Fenêtres d'éducation justifiées : couverture >= 97 % dans les fenêtres, < 97 % hors fenêtres | 100 % | dbt | Bloquante |
| Q07 | Cohérence | Total annuel des naissances identique entre données éducation et données par âge | 100 % | dbt | Bloquante |
| Q08 | Complétude | 4 groupes d'éducation présents chaque année des fenêtres | 100 % | dbt | Alerte |
