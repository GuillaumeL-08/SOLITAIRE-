class Pile:
    def __init__(self, pile=None):
        self.pile = pile if pile else []

    def est_vide(self):
        return len(self.pile) == 0

    def empiler(self, element):
        self.pile.append(element)

    def depiler(self):
        if not self.est_vide():
            return self.pile.pop()
        return None

    def sommet(self):
        if not self.est_vide():
            return self.pile[-1]
        return None

    def taille(self):
        return len(self.pile)
