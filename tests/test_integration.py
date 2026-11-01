"""Tests d'intégration : l'API telle qu'elle tourne vraiment (TP4, étape D).

Les tests du TP3 vérifient des réponses ; ceux-ci vérifient le démarrage de l'API
et son comportement quand le modèle manque ou tombe en panne.
"""
from pathlib import Path

import pytest

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")


def test_demarrage_reel_charge_le_modele():
    """D.1 : un client ouvert par « with » exécute le lifespan."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as client:
        reponse = client.get("/health")
    assert reponse.status_code == 200
    assert "TP2" in reponse.json()["model"]


def test_modele_absent_refuse_de_demarrer(monkeypatch, tmp_path):
    """D.2 : sans fichier modèle, l'API refuse de démarrer (comme le contrôle T20)."""
    from fastapi.testclient import TestClient

    import predict as predict_tp2
    from api.main import app  # importé d'abord : api.model ajoute src/ au chemin de Python

    monkeypatch.setattr(predict_tp2, "MODELE", tmp_path / "absent.joblib")
    predict_tp2.charger_modele.cache_clear()  # sinon le modèle déjà en cache serait réutilisé
    try:
        with pytest.raises(FileNotFoundError):
            with TestClient(app):
                pass
    finally:
        predict_tp2.charger_modele.cache_clear()  # les tests suivants rechargent le vrai modèle


def test_modele_non_charge_donne_503(monkeypatch):
    """D.3 : l'API démarrée, le modèle retiré de app.state : 503 sur /health et /predict."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as client:
        monkeypatch.delattr(app.state, "classifier")  # monkeypatch le remet à la fin du test
        sante = client.get("/health")
        prediction = client.post("/predict", json={"text": "Livraison rapide"})
    assert sante.status_code == 503
    assert prediction.status_code == 503


@pytest.mark.parametrize(
    "erreur",
    [RuntimeError("panne du modèle"), ValueError("bug interne")],
    ids=["RuntimeError", "ValueError"],
)
def test_modele_en_panne_donne_500_sans_message_interne(monkeypatch, erreur):
    """D.4 : quel que soit le type de l'erreur, 500, et le message interne ne sort pas de l'API."""
    from fastapi.testclient import TestClient

    from api.main import app

    def en_panne(texte: str):
        raise erreur

    with TestClient(app) as client:
        monkeypatch.setattr(app.state.classifier, "predict", en_panne)
        reponse = client.post("/predict", json={"text": "Livraison rapide"})
    assert reponse.status_code == 500
    assert str(erreur) not in reponse.text

def test_etiquettes_inconnues_refusees(monkeypatch):
    """Un modèle dont les classes ne sont pas dans la correspondance ne doit pas démarrer."""
    import api.model as module

    class FauxModele:
        classes_ = ["positif", "negatif"]

    monkeypatch.setattr(module, "charger_modele", lambda: FauxModele())
    with pytest.raises(ValueError, match="étiquettes inconnues"):
        module.SentimentClassifier()
