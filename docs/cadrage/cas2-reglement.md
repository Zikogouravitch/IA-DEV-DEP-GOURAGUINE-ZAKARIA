# Fiche de cadrage : Questions sur le règlement intérieur

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Répondre aux questions des personnes sur le règlement intérieur, avec la source de la réponse.

## Utilisateur final (obligatoire)

Les employés (ou les étudiants) qui posent leurs questions sur les règles.

## Approche retenue (obligatoire)

Cocher une seule case :

- [ ] Règles métier
- [ ] Machine learning
- [x] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

(b) Chaque réponse cite l'article du règlement, donc on peut la vérifier. (a) Il n'y a pas de données étiquetées de questions et de réponses, mais le texte du règlement existe déjà.

## Données nécessaires et leur origine (obligatoire)

Le texte officiel et à jour du règlement intérieur, fourni par la direction ou les ressources humaines.

## Métrique de succès et seuil d'acceptation (obligatoire)

Le pourcentage de réponses correctes avec le bon article cité, sur 50 questions de test. Acceptation à partir de 90 %.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Une mauvaise réponse peut mener à une erreur de comportement ou à un conflit. Si le système ne trouve pas la réponse, il renvoie vers les ressources humaines.

## Risques éthiques ou de confidentialité (obligatoire)

Les questions peuvent contenir des informations personnelles. On ne garde pas les questions avec les noms, et on utilise seulement la version à jour du règlement.

## Approche écartée et pourquoi (facultatif)

Modèle génératif seul : il ne connaît pas notre règlement et peut inventer des règles.
