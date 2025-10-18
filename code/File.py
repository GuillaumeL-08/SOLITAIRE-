class File:
    def __init__(self):
        self.p = []

    def est_vide(self)  -> list:
        return len(self.p) == 0

    def enfiler(self, elem) -> None:
        self.p.append(elem)

    def tete(self) :
        return self.p[0]

    def defiler(self):
        if not self.est_vide():
            return self.p.pop(0)
        return None

    def taille(self) -> int:
        "retourne la taille de la file"
        return len(self.p)
