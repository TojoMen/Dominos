# 🏗️ Architecture du projet Dominos

## Structure en couches

### 1. **Logique de jeu** (Pure - sans erreurs d'entrée)
- `gameengine.py` : Moteur de jeu (moves valides, vérification de victoire)
- `gamestate.py` : État du jeu
- `board.py`, `player.py`, `hand.py`, etc. : Entités du jeu

### 2. **Interface** (Gestion des erreurs d'entrée)
- `terminal_ui.py` : Interface terminale (pour maintenant)
- À créer : `graphical_ui.py` si évolution vers interface graphique (Tkinter, Pygame, etc.)

### 3. **Point d'entrée**
- `main.py` : Orchestration du jeu + appel à la couche UI

## Avantages de cette architecture

✅ **Gestion d'erreurs centralisée** : Toutes les validations d'entrée sont dans `terminal_ui.py`  
✅ **Logique pure** : Le code GameEngine n'est jamais affecté par les erreurs d'entrée  
✅ **Extensibilité** : Ajouter une interface graphique sans modifier la logique de jeu  
✅ **Testabilité** : Facile de tester GameEngine indépendamment de l'UI  

## Pour évoluer vers une interface graphique

1. Créer `graphical_ui.py` avec la même interface que `terminal_ui.py`
2. Remplacer dans `main.py` : `from terminal_ui import TerminalUI` → `from graphical_ui import GraphicalUI`
3. La logique GameEngine reste inchangée

## Exemple pour Tkinter ou Pygame

```python
class GraphicalUI:
    def __init__(self):
        self.window = tk.Tk()  # ou Pygame
    
    def get_move_choice(self, num_moves):
        # Afficher boutons interactifs
        # Retourner le choix
        pass
    
    # ... autres méthodes identiques à TerminalUI
```
