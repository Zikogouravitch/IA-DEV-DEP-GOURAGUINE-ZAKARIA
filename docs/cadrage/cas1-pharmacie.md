# Fiche de cadrage : Ordonnances incomplètes en pharmacie

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Détecter les ordonnances auxquelles il manque une information obligatoire avant la délivrance des médicaments.

## Utilisateur final (obligatoire)

Les pharmaciens et les préparateurs au comptoir.

## Approche retenue (obligatoire)

Cocher une seule case :

- [x] Règles métier
- [ ] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

(b) Les champs obligatoires d'une ordonnance sont fixés par la loi : on peut vérifier chaque règle facilement. (d) Une erreur peut mettre la santé du patient en danger, donc le résultat doit être prévisible et expliqué.

## Données nécessaires et leur origine (obligatoire)

Les ordonnances numérisées, et la liste des champs obligatoires fournie par la réglementation (nom du patient, date, signature, médicament, dose, durée).

## Métrique de succès et seuil d'acceptation (obligatoire)

Le rappel sur les ordonnances incomplètes, sur un jeu de test vérifié par des pharmaciens. Acceptation à partir de 0,99.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Une ordonnance incomplète non détectée peut causer une erreur de délivrance. Le pharmacien relit toujours l'ordonnance et décide à la fin.

## Risques éthiques ou de confidentialité (obligatoire)

Ce sont des données de santé très sensibles. Le traitement se fait en interne, avec un accès limité et sans envoi à un service tiers.

## Approche écartée et pourquoi (facultatif)

Modèle génératif seul : il peut inventer ou oublier un champ, et on ne peut pas vérifier son résultat.
