from src.gameengine import GameEngine
from src.player import Player
from src.gamestatus import GameStatus
from src.terminal_ui import TerminalUI

WIN_SCORE = 120


def main():
    """Fonction principale - boucle de parties"""
    ui = TerminalUI()
    
    players = [
        Player(id="0", name="Tojo"),
        Player(id="1", name="Rindra"),
        Player(id="2", name="Dada"),
    ]

    engine = GameEngine()

    while max(player.score for player in players) <= WIN_SCORE:
        state = engine.start_game(players)
        winner = None

        while state.status == GameStatus.IN_PROGRESS:
            current_player = state.players[state.current_player_index]
            moves = engine.get_valid_moves(state)

            ui.display_board(state.board.affichage())
            ui.display_player_turn(current_player.name)

            hand_display = "\n".join(domino.to_string() for domino in current_player.hand.dominos)
            ui.display_hand(hand_display)

            if len(moves) == 0:
                ui.display_no_moves()
                ui.get_pass_confirmation()
                state.consecutive_passes += 1
                winner = engine.check_win(state)
            else:
                moves_display = [move.domino.to_string() for move in moves]
                ui.display_available_moves(moves_display)
                choix = ui.get_move_choice(len(moves))
                state = engine.apply_move(state, moves[choix])
                winner = engine.check_win(state)

        ui.display_hand_totals(state.players)

        if winner is not None:
            engine.calculate_scores(state, winner)
            ui.display_match_winner(winner.name)
            ui.display_scores(players, title="Scores cumulatifs :")
        else:
            ui.display_draw()

    overall_winner = max(players, key=lambda player: player.score)
    ui.display_final_champion(overall_winner.name, overall_winner.score)


if __name__ == "__main__":
    main()