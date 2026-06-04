import random
from pip_enum import Pip
from domino import Domino
from pioche import Pioche
from board import Board
from move import Move
from player import Player
from gamestatus import GameStatus
from gamestate import GameState
from side import Side

class GameEngine:
    def start_game(self, players: list) -> GameState:
        dominos = []
        pip_values = list(Pip)

        for i in range(len(pip_values)):
            for j in range(i, len(pip_values)):
                dominos.append(Domino(pip_values[i], pip_values[j]))
        random.shuffle(dominos)
        
        for player in players:
            for _ in range(7):
                player.hand.add(dominos.pop())
        
        pioche = Pioche(dominos)
        
        starting_index = 0
        highest_double = -1
        for i, player in enumerate(players):
            for domino in player.hand.dominos:
                if domino.is_double() and domino.left_end.value > highest_double:
                    highest_double = domino.left_end.value
                    starting_index = i
        
        return GameState(board=Board(), pioche=pioche, players=players, current_player_index=starting_index, status=GameStatus.IN_PROGRESS, consecutive_passes=0)


    def get_valid_moves(self, state: GameState) -> list[Move]:
        valid_moves = []
        left = state.board.left_end
        right = state.board.right_end
        playable_domino = state.players[state.current_player_index].hand.playable_tiles(state.board.left_end, state.board.right_end)
        
        for domino in playable_domino:
            if left is None and right is None:
                #print("Debut Tour")
                valid_moves.append(Move(state.current_player_index, domino, side=Side.BOTH, is_pass=False, is_draw=False ))
            if domino.choix_coté(left,right) and left is not None:
                #print("Domino qui peut etre placé a droite ou a gauche")
                valid_moves.append(Move(state.current_player_index, domino, side=Side.BOTH, is_pass=False, is_draw=False ))
            elif domino.left_end == left or domino.right_end == left:
                #print("domino a gauche")
                valid_moves.append(Move(state.current_player_index, domino, side=Side.LEFT, is_pass=False, is_draw=False ))
            elif domino.right_end == right or domino.left_end == right:
                valid_moves.append(Move(state.current_player_index, domino, side=Side.RIGHT, is_pass=False, is_draw=False ))
                #print("domino a droite")
        return valid_moves


    def apply_move(self, state: GameState, move: Move) -> GameState:
        if not move:
            state.consecutive_passes += 1
            print("TSY MANANA DE MPASSE")
            return state
        
        state.board.place(move.domino, move.side)
        state.players[state.current_player_index].hand.remove(move.domino)
        state.consecutive_passes = 0
        
        return state
        


    def check_win(self, state: GameState) -> Player | None:
        if len(state.players[state.current_player_index].hand.dominos) == 0:
            state.status = state.status.FINISHED
            return state.players[state.current_player_index]
        if state.consecutive_passes  == 3:
            totaux = [player.hand.total() for player in state.players]
            state.status = state.status.FINISHED
            return state.players[totaux.index(min(totaux))] #tohizana eto fa nilalao dota
         
        state.current_player_index += 1
        state.current_player_index %= 3 
        return None