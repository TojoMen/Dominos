Doc perso — Dominos API (usage personnel)

1) But du document

Ce document répertorie les commandes et le flux pour tester le jeu multijoueur localement, explique les endpoints utilisés, et indique comment rendre le dépôt GitHub privé.

2) Endpoints principaux

- POST /games
  - Crée une nouvelle partie et retourne `game_id`.
- POST /games/{game_id}/join
  - Rejoint une partie (corps JSON: `{ "player_name": "Alice" }`). Retourne `player_id`.
- POST /games/{game_id}/start
  - Démarre la partie (nécessite >= 2 joueurs).
- GET /games/{game_id}/state
  - Retourne l'état actuel de la partie.
- GET /games/{game_id}/moves
  - Liste les coups valides pour le joueur courant.
- POST /games/{game_id}/move
  - Joue un coup (corps JSON: `{ "player_id": "0", "move_index": 1, "side": "left" }`).

3) Script `curl` (fichier scripts/e2e_curl.sh)

- Usage rapide:

```bash
# Assurez-vous d'avoir jq installé
# Par défaut le script utilise http://127.0.0.1:8000
SERVER=http://127.0.0.1:8000 ./scripts/e2e_curl.sh

# Pour ngrok, par exemple:
# SERVER=https://abcd.ngrok.io ./scripts/e2e_curl.sh
```

- Ce que fait le script:
  1. Crée une partie (`POST /games`) et lit `game_id`.
  2. Fait joindre deux joueurs (`Alice`, `Bob`) et récupère leurs `player_id`.
  3. Démarre la partie (`POST /games/{game_id}/start`).
  4. Récupère la liste des coups valides (`GET /games/{game_id}/moves`).
  5. Récupère l'état (`GET /games/{game_id}/state`) pour déterminer `current_player_id`.
  6. Envoie un `POST /games/{game_id}/move` en jouant l'index 0 pour le joueur courant.
  7. Affiche l'état final.

4) Remarques pratiques

- Le script suppose que `jq` est installé pour parser les JSON (macOS: `brew install jq`).
- Si tu veux simuler d'autres séquences, modifie le script pour passer d'autres `player_name` ou `move_index`.
- Chaque `join` renvoie maintenant un `token` unique pour le joueur.
- Pour `POST /games/{game_id}/move`, il faut fournir à la fois `player_id` et `token` : cela empêche un client non autorisé d'envoyer un coup pour un autre joueur.

5) Authentification minimale utilisée

- Quand un joueur rejoint, le serveur crée un `token` UUID.
- Le token est stocké dans `game_player_tokens[game_id][player_id]`.
- Lors d'un `move`, le serveur vérifie que le `token` envoyé correspond bien au `player_id` et à la partie.
- Si le token est manquant ou invalide, la requête est rejetée avec `403 Invalid or missing token for player.`

6) Rendre le dépôt GitHub privé

Option A — Interface web GitHub:
- Aller sur la page du dépôt sur github.com.
- Cliquer sur `Settings` → `General` → `Danger Zone` → `Change repository visibility` → `Make private`.

Option B — avec l'outil `gh` (GitHub CLI):

```bash
# Installer gh: https://cli.github.com/
# Assurez-vous d'être authentifié: gh auth login
gh repo edit <owner>/<repo> --visibility private
```

Remarques:
- Rendre un repo privé empêche l'accès public, mais les collaborateurs restent capables d'y accéder selon les permissions.
- Si le repo est déjà forké publiquement, les forks publiques restent publiques.

6) Prochaine étape recommandée

- Ajouter un token simple sur `POST /games/{game_id}/join` (renvoyer token UUID) et exiger `Authorization` ou `token` dans `POST /move`.
- Implémenter un petit client CLI pour faciliter les tests multi-machines.

---
Fichier créé automatiquement: `scripts/e2e_curl.sh` et `doc_perso.md`.
