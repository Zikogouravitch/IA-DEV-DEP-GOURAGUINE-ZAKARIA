# Compte rendu global des TP1 à TP3

**Binôme :** Zakaria Gouraguine (Zikogouravitch) et Anass Aadoud (anass0031)
**Dépôt :** https://github.com/Zikogouravitch/sentiment-app
**Date :** 12/10/2026

## 1. Le besoin et son cadrage
 
Une équipe relation client reçoit des milliers d'avis par jour et les traite dans l'ordre d'arrivée. Le besoin est de faire remonter les avis négatifs en tête de file, pour que les clients mécontents soient traités en premier. Le problème est volontairement simple côté modèle : la difficulté est dans la reproductibilité, les tests et le passage à l'utilisateur.
 
Pour le cas 3 (prioriser les avis négatifs), nous avons retenu le **machine learning**, avec la grille à quatre critères :
 
- **(a) Données étiquetées :** les étiquettes sont gratuites (polarité ou note associée à chaque avis).
- **(c) Coût par requête :** le volume est élevé, il faut un traitement automatique peu coûteux.
- **(d) Conséquence d'une erreur :** une erreur coûte un client traité en retard, pas une catastrophe.
Les deux autres cas confirment la logique de l'arbre de choix : les ordonnances incomplètes relèvent de **règles métier** ((a) pas d'étiquettes, (b) explicabilité, (d) erreur grave), et le règlement intérieur d'un **RAG** ((b) citer l'article, (a) pas d'étiquettes, (c) volume faible).
 
## 2. L'architecture du dépôt
 
Un seul dépôt, `sentiment-app`, du premier au dernier jour, avec trois kits posés les uns sur les autres :
 
| Dossier | Contenu |
|---|---|
| `src/` | `make_demo`, `train`, `evaluate`, `predict` (TP2) |
| `ui/` | `app.py` (affichage) et `helpers.py` (logique, importable sans Streamlit) (TP3) |
| `tests/` | 45 tests à l'arrivée : environnement (23), cadrage (12), git (3), modèle (4), interface (3) |
| `scripts/` | `check_setup`, `setup`, `init_depot`, `verif_clone`, `new_cadrage` |
| `docs/` | fiches de cadrage, `semaine2.md`, `semaine3.md`, ce compte rendu |
| `models/` | `.gitkeep` et `metrics.json` |
| `data/` | `sample_reviews.csv` (`demo_reviews.csv` est régénérable) |
 
**Versionné :** le code, les tests, les fiches, la CI (`.github/workflows/ci.yml`), `models/metrics.json`. **Non versionné :** le venv, le jeu de démonstration `demo_reviews.csv` et le modèle `models/sentiment.joblib`. Ces trois artefacts se reconstruisent en une commande.
 
**Pourquoi `models/metrics.json` est-il dans Git alors que `models/sentiment.joblib` ne l'est pas ?** Le modèle est un fichier binaire volumineux (le vocabulaire Allociné compte 149 529 termes), qui alourdirait définitivement l'historique, et il se régénère par `python src/train.py`. La mesure, elle, est un petit fichier texte lisible, qui garde la trace de la qualité obtenue à chaque version. C'est aussi ce qui permet à la CI de fonctionner sans jamais avoir le modèle : les deux tests de prédiction sont ignorés, les deux tests de qualité lisent `metrics.json`. L'intégration continue vérifie donc qu'un modèle acceptable a été produit, sans le transporter.
 
## 3. Le modèle
 
**Données.** Jeu de démonstration de 290 avis (145 par classe, généré par `src/make_demo.py`), puis 20 000 avis publics Allociné. **Découpage.** `train_test_split` avant toute vectorisation, pour que le jeu de test ne fuite pas dans l'entraînement, avec `random_state=42` pour la reproductibilité. **Pipeline.** Un `Pipeline` scikit-learn qui enferme le vectoriseur et le classifieur dans un seul objet.
 
| Évaluation | Modèle entraîné sur | Vocabulaire | F1 macro | Exactitude | Rappel négatif |
|---|---|---|---|---|---|
| Test démonstration (58 avis) | démonstration (290 avis) | 316 termes | 0,879 | 0,879 | 0,931 |
| Test Allociné (4 000 avis) | Allociné (16 000 avis) | 149 529 termes | 0,9205 | 0,9205 | 0,9113 |
| Test démonstration (58 avis) | Allociné (16 000 avis) | 149 529 termes | 0,676 | 0,690 | 0,897 |
 
La deuxième ligne vient de notre `models/metrics.json`, les autres de `python src/evaluate.py`. Le modèle n'a pas changé entre les lignes : ce sont les données. La mesure sur Allociné est crédible car elle porte sur 4 000 avis au lieu de 58. En revanche, le modèle Allociné appliqué aux 58 avis de démonstration tombe à 0,676 de F1 : sa qualité ne se transfère pas hors de son domaine.
 
Matrice de confusion du modèle entraîné sur la démonstration, sur ses 58 avis de test (lignes : étiquette réelle, colonnes : prédiction) :
 
| | negative | positive |
|---|---|---|
| **negative** | 27 | 2 |
| **positive** | 5 | 24 |
 
- **Ligne « negative »** : sur 29 avis négatifs, 27 sont retrouvés (rappel 93,1 %) et 2 sont classés positifs. Ce sont les erreurs les plus coûteuses : un client mécontent est traité en retard.
- **Ligne « positive »** : sur 29 avis positifs, 24 sont bien classés (rappel 82,8 %) et 5 sont classés négatifs. Ce sont des fausses alertes : un agent relit un avis pour rien.
Pour comparaison, matrice du modèle Allociné sur ces mêmes 58 avis (lignes : étiquette réelle, colonnes : prédiction) :
 
| | negative | positive |
|---|---|---|
| **negative** | 26 | 3 |
| **positive** | 15 | 14 |
 
- **Ligne « negative »** : sur 29 avis négatifs, 26 sont retrouvés (rappel 89,7 %) et 3 sont classés positifs. Ce sont les erreurs les plus coûteuses : un client mécontent est traité en retard.
- **Ligne « positive »** : sur 29 avis positifs, seuls 14 sont bien classés (rappel 48,3 %) et 15 sont classés négatifs. Ce sont des fausses alertes : un agent relit un avis pour rien.
- **Précision négative** : 63,4 % (26/41). Un avis annoncé négatif sur trois est en réalité positif.
## 4. L'analyse des erreurs
 
**Modèle entraîné sur la démonstration (TP2).** 7 erreurs sur 58 : 2 négatifs classés positifs et 5 positifs classés négatifs. Les trois exemples affichés par `evaluate.py` sont tous des avis mitigés, construits en deux moitiés opposées (« … sauf que ensuite … »). Exemple tiré de nos données : « Service impeccable et livraison en avance sur le papier, sauf que ensuite produit cassé… » est négatif, mais le modèle répond positif. Le mécanisme : le sac de mots compte les mots positifs et négatifs puis tranche, mais n'a pas d'ordre. Il ne voit pas le retournement, alors que l'étiquette suit la seconde moitié, celle qui conclut.
 
**Modèle Allociné sur les mêmes 58 avis.** 18 erreurs sur 58 : 3 négatifs classés positifs et 15 positifs classés négatifs. Deux mécanismes se combinent.
 
1. **Le retournement.** « Produit cassé à l'arrivée sur le papier, mais finalement excellent rapport qualité prix. » est positif, mais le modèle répond négatif. Le sac de mots compte les mots positifs et négatifs puis tranche, mais n'a pas d'ordre : il ne voit pas que « mais finalement » renverse le sens et que l'étiquette suit la seconde moitié.
2. **Le décalage de domaine.** « Le vendeur a répondu en moins d'une heure. » est positif et sans retournement, pourtant classé négatif. Le modèle a été entraîné sur des critiques de films et le vocabulaire du commerce en ligne lui est mal connu.
**Sur le fichier complet via l'interface** (`demo_reviews.csv`, 290 avis, modèle Allociné) :
 
| Étiquette réelle \ Prédiction | negative | positive |
|---|---|---|
| **negative** (145) | 133 | 12 |
| **positive** (145) | 77 | 68 |
 
L'exactitude est de **69,3 %**, cohérente avec les 69,0 % mesurés sur les 58 avis de test (contre 92,05 % sur Allociné). Le rappel négatif reste bon (133/145, soit 91,7 %), mais la précision négative n'est que de 63,3 % (133/210). L'interface annonce 210 négatifs au lieu de 145 : l'écart de 65 avis est exactement le solde de 77 positifs classés négatifs moins 12 négatifs classés positifs.
 
Le mécanisme principal ici est un **décalage de domaine** : le modèle a été entraîné sur des critiques de films et appliqué à des avis clients. Ce n'est pas seulement un problème d'avis mitigés : « Le vendeur a répondu en moins d'une heure » (étiquette positive) est classé négatif avec 80,8 % de confiance, alors que le vocabulaire du commerce en ligne est mal connu du modèle. À l'inverse, « Commande jamais reçue et remboursement en attente, comme prévu » (étiquette négative) est classé positif avec 54 % : l'ironie n'est pas vue.
 
**Ce qu'il faudrait pour corriger.** Entraîner sur des avis clients étiquetés, et utiliser un modèle qui tient compte de l'ordre des mots (par exemple un transformeur) pour les retournements et l'ironie. Ce n'était pas le sujet de la séance : l'objectif du TP2 était un modèle reproductible, évalué correctement, dont on sait pourquoi il se trompe, pas un bon modèle.
 
Limites du fichier : 98 lignes sont en double (192 avis distincts) et 130 avis sont mitigés ou neutres, ce qui le rend plus difficile qu'un flux réel.
 
## 5. L'interface et le seuil d'incertitude
 
L'interface Streamlit (`ui/app.py`) a deux onglets utiles : un avis isolé, et un fichier CSV (métriques, graphique de répartition, tableau trié négatifs en tête, export). Le seuil `SEUIL_INCERTITUDE` (dans `ui/helpers.py`) fixe la confiance en dessous de laquelle un avis est marqué « à vérifier » et renvoyé à un agent. Mesure sur `demo_reviews.csv` (290 avis, 89 erreurs au total) :
 
| Seuil | Avis envoyés à un agent | Erreurs encore non vérifiées | Erreurs interceptées |
|---|---|---|---|
| 0,50 | 0 (0 %) | 89 | 0 % |
| 0,60 | 117 (40,3 %) | 55 | 34 (38 %) |
| 0,75 | 234 (80,7 %) | 17 | 72 (81 %) |
 
Ces chiffres ont été recalculés par nos soins avec le script `verif_seuils.py`, qui charge `models/sentiment.joblib` et prédit sur le fichier choisi.
 
Trois constats. À 0,50, aucun avis n'est vérifié : avec deux classes, la confiance est toujours d'au moins 0,5. Le 234 « à vérifier » de notre capture correspond à un seuil de 0,75. Enfin, sur ce fichier, la confiance est peu informative (0,641 en moyenne sur les erreurs contre 0,654 sur les bonnes réponses), si bien que la part d'erreurs interceptées est presque égale à la part d'avis envoyés.
 
**Contrôle complémentaire sur `sample_reviews.csv` (30 avis, 9 erreurs).**
 
| Seuil | Avis envoyés à un agent | Erreurs encore non vérifiées | Erreurs interceptées |
|---|---|---|---|
| 0,50 | 0 (0 %) | 9 | 0 % |
| 0,60 | 7 (23,3 %) | 5 | 4 (44 %) |
| 0,75 | 21 (70,0 %) | 0 | 9 (100 %) |
 
Ici la confiance est nettement plus informative : 0,610 en moyenne sur les erreurs contre 0,745 sur les bonnes réponses. Les 21 avis « à vérifier » de notre capture sur ce fichier confirment aussi que l'interface tournait alors avec un seuil de 0,75. Mais 30 avis et 9 erreurs, c'est trop peu pour conclure : un seul avis change le résultat de plusieurs points. Nous retenons seulement que l'utilité du seuil dépend de la nature des avis, ce que `demo_reviews.csv` (fichier généré, avec doublons et avis mitigés) ne permet pas de voir.
 
**Seuil retenu : 0,75.** Le cas 3 dit qu'une erreur est peu grave, mais un négatif classé positif retarde un client mécontent, et nous préférons les intercepter. À 0,75, sur `sample_reviews.csv`, les 9 erreurs sont toutes interceptées en n'envoyant que 70 % des avis (21 sur 30) à un agent. Sur `demo_reviews.csv`, 81 % des erreurs sont interceptées, mais au prix de 80,7 % des avis (234 sur 290) envoyés à un agent : la charge humaine est lourde et l'automatisation apporte peu. Nous acceptons ce coût tant que le modèle n'est pas ré-entraîné sur des avis clients, et nous aurions choisi 0,60 si l'équipe relation client ne pouvait pas absorber cette charge.
 
## 6. Ce qui a échoué
Nos résultats d'`evaluate.py` (18 erreurs sur 58, F1 de 0,676) ne correspondaient pas à ceux du sujet (7 erreurs sur 58, F1 de 0,879) : le modèle chargé était celui d'Allociné, entraîné après le TP2, et non celui de la démonstration. Nous avons aussi constaté un échec de nature différente : sur `demo_reviews.csv`, l'interface annonce 210 négatifs (72,4 %) alors que le fichier en contient 145 (50 %). Le F1 de 0,92 mesuré sur Allociné ne se transfère pas à nos données.
 
## 7. Ce que vous feriez autrement
 
- Entraîner ou affiner le modèle sur des avis clients plutôt que sur des critiques de films : c'est la correction la plus rentable d'après notre analyse.
- Mesurer la qualité sur un jeu étiqueté du domaine cible, et pas seulement sur le jeu de test Allociné.
- Gérer une classe « neutre », absente aujourd'hui alors que le fichier en contient.
- Utiliser un modèle sensible à l'ordre des mots pour traiter les retournements et l'ironie.
- Calibrer la confiance du modèle, puis choisir le seuil sur un jeu étiqueté en traçant le taux d'avis envoyés à un agent contre le taux d'erreurs restantes.
- Supprimer les doublons du fichier de démonstration avant toute évaluation.
## 8. Répartition du travail
 
| Membre | Ce qu'il a pris en charge |
|---|---|
| Zakaria Gouraguine | TP1 : son commit personnel dans le tableau du binôme. TP3 : commit et push de l'interface Streamlit.|
| zack | TP1 : son commit personnel dans le tableau du binôme. TP2 : commit et push du modèle, des métriques et des tests.  |
