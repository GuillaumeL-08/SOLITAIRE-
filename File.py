class File:
    def __init__(self):
        self.p = []

    def est_vide(self):
        return len(self.p) == 0

    def tete(self):
        if not self.est_vide():
            return self.p[0]
        return None

    def enfiler(self, elem):
        self.p.append(elem)

    def defiler(self):
        if not self.est_vide():
            return self.p.pop(0)
        return None
