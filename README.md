# Dominos
Jeu de Dominos 1v1v1 (version sans pioche)

## API FastAPI

Pour lancer le serveur et tester l'API :

```bash
python -m pip install -r requirements.txt
uvicorn src.api:app --reload
```

Puis ouvrir :

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

### Séquence de test

1. `POST /start` pour démarrer une partie.
2. `GET /state` pour voir l'état du jeu.
3. `GET /moves` pour lister les coups possibles.
4. `POST /move` avec `{"move_index": 0}` pour jouer un coup.
5. `GET /state` pour vérifier l'état mis à jour.
