import random

class Board:
    def __init__(self):
        # Listes simples de pièces, suspects et armes
        self.rooms = ["Cuisine", "Bureau", "Garage", "Salon", "Bibliotheque", "Jardin", "Chambre"]
        self.suspects = ["Moutarde", "Peacock", "Scarlett", "Plum", "White", "Black", "Green", "Violet"]
        self.weapons = ["Marteau", "Collier", "Chandelier", "Hache", "Corde", "Fusil", "Couteau"]