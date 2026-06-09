"""
Terminal UI - Gestion de l'interface utilisateur et des entrées
Séparation claire entre logique de jeu et présentation
"""

class TerminalUI:
    """Gère toute l'interaction avec l'utilisateur via terminal"""
    
    @staticmethod
    def get_move_choice(num_moves: int) -> int:
        """
        Demande à l'utilisateur de choisir un move valide
        
        Args:
            num_moves: nombre de moves possibles (0 à num_moves-1)
        
        Returns:
            int: index du move choisi
        
        Raises:
            ValueError: si l'entrée n'est pas valide
        """
        while True:
            try:
                choix = input("Ton choix : ").strip()
                choix_int = int(choix)
                
                # Vérifier que le choix est dans la plage valide
                if 0 <= choix_int < num_moves:
                    return choix_int
                else:
                    print(f"❌ Erreur : choix entre 0 et {num_moves - 1}")
                    
            except ValueError:
                print("❌ Erreur : veuillez entrer un nombre valide")
    
    @staticmethod
    def get_pass_confirmation() -> bool:
        """
        Demande confirmation pour passer son tour
        
        Returns:
            bool: True si l'utilisateur confirme (tape PASS)
        """
        while True:
            choix = input("Écris PASS pour passer ton tour : ").strip().upper()
            if choix == "PASS":
                return True
            else:
                print("❌ Erreur : tapez PASS pour confirmer")
    
    @staticmethod
    def display_board(board_str: str):
        """Affiche le plateau"""
        print("PLATEAU :")
        print(board_str)
    
    @staticmethod
    def display_player_turn(player_name: str):
        """Affiche le début du tour du joueur"""
        print(f"\n🎮 Tour de {player_name}")
    
    @staticmethod
    def display_hand(hand_str: str):
        """Affiche la main du joueur"""
        print("Ta main :")
        print(hand_str)
    
    @staticmethod
    def display_available_moves(moves_list: list):
        """Affiche les moves possibles"""
        print("Moves possibles :")
        for i, move_str in enumerate(moves_list):
            print(f"  {i} — {move_str}")
    
    @staticmethod
    def display_no_moves():
        """Affiche message si aucun move n'est possible"""
        print("⚠️  Aucun move possible, tu dois passer ton tour.")
    
    @staticmethod
    def display_winner(winner_name: str):
        """Affiche le gagnant"""
        print(f"\n🏆 Le gagnant est : {winner_name}")
    
    @staticmethod
    def display_error(error_msg: str):
        """Affiche un message d'erreur"""
        print(f"❌ Erreur : {error_msg}")
