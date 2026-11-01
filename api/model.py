"""Raccord entre l'API et le modèle entraîné au TP2.

L'API n'entraîne rien et ne connaît pas scikit-learn : elle appelle la fonction
predict() de src/predict.py, qui charge models/sentiment.joblib une seule fois.
"""
import sys
from pathlib import Path
from typing import Literal, TypedDict

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
from predict import charger_modele  # noqa: E402  (fonctions du TP2)
from predict import predict as _predict  # noqa: E402

# Sous cette confiance, le modèle ne tranche pas : l'avis part vers un humain (TP4, étape C).
# Valeur choisie avec python src/courbe_seuil.py : voir docs/semaine4.md, partie 3.
SEUIL_ABSTENTION = 0.60

Etiquette = Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]

# Correspondance explicite entre les classes du modèle (TP2) et les étiquettes du contrat de l'API.
CORRESPONDANCE: dict[str, Etiquette] = {"positive": "POSITIVE", "negative": "NEGATIVE"}


class Prediction(TypedDict):
    """Ce que SentimentClassifier.predict renvoie, et ce que l'API sérialise."""

    label: Etiquette
    score: float
    text: str


class SentimentClassifier:
    """Enveloppe du modèle TP2 avec l'interface attendue par l'API."""

    model_name = "tfidf-logreg (TP2, models/sentiment.joblib)"

    def __init__(self) -> None:
        modele = charger_modele()  # échoue immédiatement si le joblib manque : on ne démarre pas sans modèle
        inconnues = set(modele.classes_) - set(CORRESPONDANCE)
        if inconnues:  # vérifié au démarrage : mieux vaut refuser que répondre une étiquette hors contrat
            raise ValueError(f"étiquettes inconnues du modèle : {sorted(inconnues)}")

    def predict(self, text: str) -> Prediction:
        """Renvoie {'label': 'POSITIVE'|'NEGATIVE'|'INDETERMINE', 'score': float, 'text': aperçu}."""
        r = _predict(text)  # lève ValueError si le texte est vide
        label: Etiquette = CORRESPONDANCE[r["label"]]
        if r["score"] < SEUIL_ABSTENTION:
            label = "INDETERMINE"  # le score reste renvoyé : le client voit à quel point le modèle hésite
        return {"label": label, "score": r["score"], "text": text[:100]}


def load_model() -> SentimentClassifier:
    """Construit le classifier (le cache de chargement est dans src/predict.py)."""
    return SentimentClassifier()
