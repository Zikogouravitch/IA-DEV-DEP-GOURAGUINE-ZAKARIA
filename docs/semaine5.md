# Semaine 5 : l'interface, notes du binôme

> Trois questions, quelques phrases chacune. Répondez avec ce que vous avez observé.

## 1. Pourquoi l'interface n'importe-t-elle jamais `predict()` ni le fichier `.joblib` ?

L'interface est un client de l'API : elle envoie `POST /predict` et affiche la réponse, comme n'importe quel programme. Elle ne connaît que `ui/client.py`, qui ne connaît lui-même que l'adresse de l'API et ses codes de réponse.

Conséquence : si on réentraîne le modèle, ou si on déplace l'API sur un autre serveur, la page n'a aucune modification à subir. La décision (seuil d'abstention, validation du texte) reste à un seul endroit, l'API, au lieu d'être dupliquée dans la page.

## 2. Que montre l'interface quand le modèle hésite, et pourquoi est-ce mieux qu'un verdict forcé ?

Pour « xqzvb wlkptr grombu », la page affiche « Je ne sais pas » avec une confiance de 52 %, et un encadré : « La confiance est sous le seuil d'abstention : un humain doit trancher. »

C'est mieux qu'un verdict forcé, car avec 52 % le modèle est presque à pile ou face : afficher « positif » ou « négatif » donnerait une fausse certitude. L'abstention envoie les cas douteux vers un humain et évite une mauvaise décision automatique.

## 3. Que voit l'utilisateur quand l'API tombe ? Et le fichier `data/avis_exemple.csv` : combien d'avis partent vers un humain ?

Quand l'API est arrêtée, la page s'affiche quand même, avec en haut le message d'erreur « API injoignable : lancez d'abord uvicorn api.main:app », visible dès le rechargement, avant même d'analyser un avis (la santé est revérifiée à chaque réexécution).

Pour `avis_exemple.csv`, le résumé est :

```python
{'INDETERMINE': 1, 'NEGATIVE': 2, 'POSITIVE': 3}
```

**1 avis sur 6** part vers un humain (« xqzvb wlkptr grombu », confiance 0.5162).
