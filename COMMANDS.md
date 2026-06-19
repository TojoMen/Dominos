# Commandes pour lancer l'API et exécuter les tests

## 1. Installer les dépendances

```bash
# Installer les dépendances Python nécessaires pour l'API et les tests
python3 -m pip install -r requirements.txt
```

## 2. Lancer le serveur FastAPI

```bash
# Démarrer le serveur API en mode développement
# Le serveur sera accessible sur http://127.0.0.1:8000
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

## 3. Vérifier l'API dans le navigateur

```text
# Ouvrir la documentation interactive de FastAPI
http://127.0.0.1:8000/docs
```

## 4. Exécuter les tests unitaires

```bash
# Lancer seulement les tests de l'API
python3 -m pytest tests/test_api.py
```

## 5. Optionnel : rendre le serveur accessible depuis Internet

```bash
# Si vous utilisez ngrok, exposez le port 8000
ngrok http 8000
```

## Notes

- Utiliser `python3` si `python` n'est pas défini sur votre système.
- Le serveur `uvicorn` doit être en cours d'exécution avant d'appeler l'API depuis un autre poste.
- Si vous ajoutez de nouvelles routes ou modifications dans `src/api.py`, relancez `uvicorn` ou laissez `--reload` activé pour recharger automatiquement.
