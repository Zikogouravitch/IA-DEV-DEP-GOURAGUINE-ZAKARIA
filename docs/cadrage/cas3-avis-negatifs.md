# Fiche de cadrage : Priorisation des avis négatifs

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Classer les avis clients négatifs par priorité pour traiter les plus urgents en premier.

## Utilisateur final (obligatoire)

L'équipe du service client.

## Approche retenue (obligatoire)

Cocher une seule case :

- [ ] Règles métier
- [x] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

(a) L'équipe a déjà traité des avis passés, qui servent d'exemples étiquetés. (c) Il y a beaucoup d'avis, et un classifieur coûte très peu par avis. (d) Une erreur de priorité est facile à corriger par un agent.

## Données nécessaires et leur origine (obligatoire)

Un export des anciens avis négatifs avec le niveau de priorité donné par l'équipe, depuis l'outil de gestion des avis. Les noms et les contacts sont supprimés.

## Métrique de succès et seuil d'acceptation (obligatoire)

F1 macro sur un jeu de test tenu à l'écart. Acceptation à partir de 0,85, avec un rappel d'au moins 0,90 sur la classe « urgent ».

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Un avis mal classé est corrigé par l'agent. Le changement de priorité sert ensuite à réentraîner le modèle.

## Risques éthiques ou de confidentialité (obligatoire)

Les avis peuvent contenir des noms ou des coordonnées. On anonymise avant le traitement et on garde le modèle en interne.

## Approche écartée et pourquoi (facultatif)

Règles par mots-clés : elles ratent beaucoup d'avis qui expriment la colère sans ces mots.
