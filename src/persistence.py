import sqlite3
import json
from pathlib import Path

DB_PATH = Path("dominos.db")

def init_db(db_path: str = DB_PATH):
    """Initialise la base SQLite avec les tables du jeu de dominos."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Activer les foreign keys (désactivées par défaut en SQLite !)
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            game_id TEXT PRIMARY KEY,
            state JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            player_id TEXT NOT NULL,
            player_name TEXT,
            token TEXT,
            UNIQUE(game_id, player_id),
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS moves_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            player_id TEXT,
            move_index INTEGER,
            move_data JSON,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
    print("Base de données initialisée avec succès.")

def save_game(game_id: str, state: dict, db_path: str = DB_PATH):
    """Sauvegarde l'état du jeu dans la base de données."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO games (game_id, state) VALUES (?, ?)
        ON CONFLICT(game_id) DO UPDATE SET state=excluded.state, updated_at=CURRENT_TIMESTAMP
    """, (game_id, json.dumps(state)))

    conn.commit()
    conn.close()

def load_game(game_id: str, db_path: str = DB_PATH):
    """Charge l'état du jeu depuis la base de données."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT state FROM games WHERE game_id = ?", (game_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])
    return None

def save_player_token(game_id: str, player_id: str, player_name: str, token: str, db_path: str = DB_PATH):
    """Sauvegarde les infos du joueur (token d'authentification)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO players (game_id, player_id, player_name, token) VALUES (?, ?, ?, ?)
        ON CONFLICT(game_id, player_id) DO UPDATE SET token=excluded.token, player_name=excluded.player_name
    """, (game_id, player_id, player_name, token))

    conn.commit()
    conn.close()

def get_players_for_game(game_id: str, db_path: str = DB_PATH) -> dict:
    """Récupère tous les joueurs d'une partie avec leurs tokens."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT player_id, player_name, token FROM players WHERE game_id = ? ORDER BY player_id
    """, (game_id,))
    rows = cursor.fetchall()
    conn.close()

    players = {}
    for player_id, player_name, token in rows:
        players[player_id] = {"name": player_name, "token": token}
    return players

def verify_player_token(game_id: str, player_id: str, token: str, db_path: str = DB_PATH) -> bool:
    """Vérifie que le token fourni correspond au joueur."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT token FROM players WHERE game_id = ? AND player_id = ?
    """, (game_id, player_id))
    row = cursor.fetchone()
    conn.close()

    if row and row[0] == token:
        return True
    return False

def save_move_history(game_id: str, player_id: str, move_index: int, move_data: dict = None, db_path: str = DB_PATH):
    """Enregistre un move dans l'historique."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO moves_history (game_id, player_id, move_index, move_data) 
        VALUES (?, ?, ?, ?)
    """, (game_id, player_id, move_index, json.dumps(move_data) if move_data else None))

    conn.commit()
    conn.close()

def load_all_active_games(db_path: str = DB_PATH) -> dict:
    """Charge tous les jeux en cours (pour redémarrage du serveur)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Charger seulement les jeux créés dans les dernières 24h
    cursor.execute("""
        SELECT game_id, state FROM games 
        WHERE datetime(updated_at) > datetime('now', '-24 hours')
        ORDER BY updated_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    games = {}
    for game_id, state_json in rows:
        games[game_id] = json.loads(state_json)
    return games

def delete_game(game_id: str, db_path: str = DB_PATH):
    """Supprime un jeu et tous ses données associées (joueurs, moves)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM games WHERE game_id = ?", (game_id,))
    
    conn.commit()
    conn.close()

def get_game_statistics(game_id: str, db_path: str = DB_PATH) -> dict:
    """Récupère les stats d'une partie (nombre moves, durée, etc)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT created_at, updated_at FROM games WHERE game_id = ?", (game_id,))
    game_row = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) FROM moves_history WHERE game_id = ?", (game_id,))
    move_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT player_id) FROM players WHERE game_id = ?", (game_id,))
    num_players = cursor.fetchone()[0]
    
    conn.close()

    if game_row:
        return {
            "game_id": game_id,
            "created_at": game_row[0],
            "updated_at": game_row[1],
            "num_moves": move_count,
            "num_players": num_players
        }
    return None