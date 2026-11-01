# Semaine 4 : tests approfondis et qualité, notes du binôme

> Une à deux pages. Uniquement des chiffres issus de VOS exécutions.

## 1. Couverture

- Avant (étape A) : 91 %, lignes jamais exécutées : api/main.py 49, 77-79 et 85-87
- Tests au départ : 1 failed, 54 passed, 1 skipped (échec : jeu d'or incomplet, 0 avis sur 20)
- Pour chacune, le comportement qu'aucun test ne vérifiait : ligne 49, le 503 quand le modèle n'est pas chargé ; lignes 77-79, le 500 quand le modèle plante ; lignes 85-87, le lancement direct (bloc __main__), jamais exécuté sous pytest
- Après (étape D) : 100 % (97,40 % avant l'exclusion) ; lignes exclues de la mesure et pourquoi : api/main.py, bloc if __name__ == "__main__" (lancement manuel par uvicorn, jamais exécuté sous pytest ; le comportement de l'API est testé par TestClient)

## 2. Défauts trouvés

| Symptôme | Test qui l'a révélé | Correction |
| --- | --- | --- |
| Un texte de blancs reçoit un 422 dont detail est la chaîne "texte vide", au lieu de la liste standard (le schéma ne le refuse pas, c'est predict() qui le fait) | test_frontieres_du_contrat[espaces-seuls] ; test_propriete_texte_de_blancs_refuse (Falsifying example : texte='\x85') | field_validator sur text dans api/schemas.py : refuse un texte vide une fois ses blancs retirés (strip()), même règle que predict() ; le refus vient de Pydantic, donc la forme standard |
| Des mots inventés reçoivent NEGATIVE à 0,5162, comme une réponse sûre : sans mot connu, il ne reste que l'ordonnée à l'origine de la régression | Essai dans /docs ; test_jeu_or.py (erreurs franches déclarées en xfail) | SEUIL_ABSTENTION = 0,60 dans api/model.py : sous le seuil, l'étiquette devient INDETERMINE et le score est conservé |
| Une panne ValueError("bug interne") du modèle répond 422 avec le message interne, au lieu d'un 500 : le message interne fuit vers le client | test_modele_en_panne_donne_500_sans_message_interne[ValueError] (assert 422 == 500) | Suppression du except ValueError dans api/main.py : depuis l'étape B, un texte invalide est refusé par Pydantic, donc un ValueError venant de predict() est un bug interne ; toute panne répond 500 |

## 3. Seuil d'abstention

- Trois points de la courbe : 0,50 -> 58 réponses, 7 erreurs, 0 vers un humain ; 0,60 -> 42 réponses, 2 erreurs, 16 vers un humain (28 %) ; 0,70 -> 37 réponses, 0 erreur, 21 vers un humain (36 %)
- Seuil retenu : 0,60 ; part des avis envoyés à un humain : 16 sur 58, soit 28 % ; justification : à 0,50 le modèle répond à tout et se trompe 7 fois sur 58 ; à 0,60 il n'en commet plus que 2 (5 erreurs évitées) pour 16 avis relus par un humain. Au-delà, le gain devient faible : 0,65 évite une erreur de plus pour un avis relu en plus, et 0,70 supprime les dernières erreurs mais envoie 36 % des avis à un humain, ce qui réduit l'intérêt du modèle. 0,60 est aussi au-dessus de 0,5162, la confiance renvoyée pour des mots inventés, donc ce défaut est réglé. Réserve : ces chiffres viennent de 58 avis, et le seuil est choisi sur ce même jeu de test ; le jeu d'or, fait d'avis jamais vus, dira si ce choix tient. Il montre que ce seuil envoie 65 % des avis de mon jeu d'or vers un humain (voir partie 4).

## 4. Jeu d'or

- Bilan (python src/bilan_jeu_or.py) : justes 4, abstentions 13, erreurs franches déclarées 3 (sur 20 avis)
- Ce que ces chiffres disent du modèle : le modèle ne tranche correctement que 4 avis sur 20 et en envoie 13 (65 %) vers un humain, contre 28 % sur le jeu de test de la courbe (16 sur 58). Des avis évidents comme « Le produit fonctionne parfaitement depuis trois semaines » reçoivent une confiance de 0,50 : le vocabulaire du jeu de démonstration est petit (316 termes) et mes avis utilisent probablement d'autres mots, donc le modèle hésite. Parmi les 7 avis où il répond, 3 sont des erreurs franches, avec des confiances de 0,70, 0,65 et 0,61, toutes au-dessus du seuil de 0,60 : l'abstention rattrape les cas où le modèle hésite, pas ceux où il se trompe avec assurance (mot positif qui l'emporte après « mais », négation non vue, mot « ignoré » absent de l'entraînement : 0 occurrence dans demo_reviews.csv, réponse POSITIVE à 0,6527). La mesure de la courbe (2 erreurs sur 58) était donc sans doute optimiste : le jeu de test vient du même jeu de démonstration que l'entraînement. Réserve : la moitié de mon jeu d'or est faite d'avis difficiles, donc l'écart avec la courbe (65 % contre 28 % d'abstentions) n'est pas uniquement dû au modèle.

## 5. Outils statiques

- Remarques au départ : ruff 15 (11 attendues + 4 dans ui/ : I001 dans app.py, E741 x3 dans helpers.py), mypy 0 (Success: no issues found in 4 source files)
- Parmi les défauts de la partie 2, combien ruff et mypy avaient-ils signalés ? Qu'en concluez-vous ? Aucun des trois pour sa cause réelle : mypy ne signalait rien au départ (0 remarque), et ruff n'a rien dit sur le 422 en chaîne ni sur les mots inventés, car le code était valide et bien typé. Pour la panne ValueError renvoyée en 422 avec le message interne, ruff avait signalé B904 sur la ligne du raise HTTPException(422), mais pour une autre raison (raise sans from), pas pour la fuite du message : c'est une coïncidence de ligne, pas une détection. J'en conclus que ruff et mypy repèrent le style et les types, pas le comportement : les trois défauts ont été trouvés par les tests (hypothèse, jeu d'or, tests d'intégration). Les deux familles d'outils sont complémentaires : les outils statiques empêchent le retour de classes d'erreurs (imports inutiles, zip sans strict, étiquette hors contrat grâce au Literal), les tests vérifient le comportement.
- Remarques à l'arrivée : ruff 0 (All checks passed), mypy 0 ; tests : 85 passed, 3 xfailed ; couverture 100 %
