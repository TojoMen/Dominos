from gameengine import GameEngine
from player import Player
from gamestatus import GameStatus
from hand import Hand
from terminal_ui import TerminalUI

def main():
    """Fonction principale - boucle de jeu"""
    ui = TerminalUI()
    
    p1 = Player(id="0", name="Tojo")
    p2 = Player(id="1", name="Rindra")
    p3 = Player(id="2", name="Dada")

    engine = GameEngine()
    state = engine.start_game([p1, p2, p3])

    while state.status == GameStatus.IN_PROGRESS:
        current_player = state.players[state.current_player_index]
        moves = engine.get_valid_moves(state)

        # Affichage avec UI
        ui.display_board(state.board.affichage())
        ui.display_player_turn(current_player.name)
        
        hand_display = "\n".join(domino.to_string() for domino in current_player.hand.dominos)
        ui.display_hand(hand_display)

        # Traiter les moves
        if len(moves) == 0:
            ui.display_no_moves()
            ui.get_pass_confirmation()  # Gère la validation avec boucle
            state.consecutive_passes += 1
            winner = engine.check_win(state)
        else:
            # Afficher les moves possibles
            moves_display = [move.domino.to_string() for move in moves]
            ui.display_available_moves(moves_display)

            # Lire le choix avec validation d'erreur
            choix = ui.get_move_choice(len(moves))  # Gère la validation avec boucle
            state = engine.apply_move(state, moves[choix])
            winner = engine.check_win(state)
    
    ui.display_winner(winner.name)

if __name__ == "__main__":
    main()