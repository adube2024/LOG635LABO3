from game.board import Board
from game.agent import Agent


# Création du plateau de jeu
board = Board()



print("Le scénario de l'enquête a été généré.\n")

    # Attente utilisateur
input("\nAppuyez sur <Entrée> pour commencer l'enquête...")

    # Création de l'agent avec le board
agent = Agent(board=board)

    # Lancer l’enquête
agent.begin_investigation()