from gameengine import GameEngine
from player import Player
from gamestatus import GameStatus
from hand import Hand

p1 = Player(id="0", name="Tojo")
p2 = Player(id="1", name="Rindra")
p3 = Player(id="2", name="Dada")

engine = GameEngine()

state = engine.start_game([p1, p2, p3])

while state.status == GameStatus.IN_PROGRESS:
    current_player = state.players[state.current_player_index]
    moves = engine.get_valid_moves(state)

    print("PLATEAU :")
    print(state.board.affichage())
    print(f"\nTour de {current_player.name}")
    print("Ta main :")

    for domino in current_player.hand.dominos:
         print(domino.to_string())

    # Afficher les moves possibles
    print("Moves possibles :")
    for i, move in enumerate(moves):
        print(f"  {i} — {move.domino.to_string()}")

     # Lire le choix
    choix = int(input("Ton choix : "))
    state = engine.apply_move(state, moves[choix])
    winner = engine.check_win(state)
print("winner is :" + winner.name)