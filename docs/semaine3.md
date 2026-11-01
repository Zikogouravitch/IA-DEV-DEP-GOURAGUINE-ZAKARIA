# Semaine 3 : l'API, notes du binôme

> Deux questions, quelques phrases chacune. Répondez avec ce que vous avez observé, pas avec le cours.

## 1. Pourquoi l'API refuse-t-elle de démarrer sans `models/sentiment.joblib`, plutôt que de démarrer et de répondre 503 ?

L'API a besoin du modèle sentiment.joblib pour effectuer les prédictions de sentiment. Sans ce fichier, elle ne peut pas fonctionner correctement. Il est donc préférable de bloquer le démarrage immédiatement plutôt que de lancer une API incapable de répondre aux demandes. Cela permet de détecter rapidement le problème.

## 2. Un texte vide est refusé deux fois : par Pydantic, puis par `predict()`. Est-ce redondant ?

Non, ce n'est pas totalement redondant. Pydantic vérifie les données reçues par l'API avant de les traiter, tandis que predict() protège directement la fonction de prédiction. Ainsi, même si predict() est appelée depuis un autre endroit sans passer par l'API, elle reste protégée contre les textes vides.
