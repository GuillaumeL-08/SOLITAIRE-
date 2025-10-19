class Pile:
    def __init__(self, pile=None):  
        self.pile = pile if pile else []

    def est_vide(self):  
        "Vérifie si la pile est vide"
        return len(self.pile) == 0

    def empiler(self, element): 
        "Ajoute un élément au sommet de la pile"
        self.pile.append(element)

    def depiler(self):
        if not self.est_vide():  
            "Retire et retourne l'élément au sommet de la pile"
            return self.pile.pop()
        return None

    def sommet(self): 
        "Retourne l'élément au sommet de la pile sans le retirer"
        if not self.est_vide():
            return self.pile[-1]
        return None

    def taille(self): 
        "Retourne le nombre d'éléments dans la pile"
        return len(self.pile)

