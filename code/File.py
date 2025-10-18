class File:
    def __init__(self) -> None:
        "initialise les attributs"
        self.p = []

    def est_vide(self) -> bool:
        "renvoie True si la file est vide sinon False"
        if self.p == []:
            return True
        else:
            return False

    def enfiler(self, elem) -> None:
        "ajoute un elemnt à la file"
        self.p.append(elem)

    def tete(self)  :
        "renvoie le premier élément de la file"
        return self.p[0]

    def defiler(self):
        "renvoie le premier élément de la file puis le supprime de la file"
        if not self.est_vide():
            return self.p.pop(0)
        return None

    def taille(self) -> int:
        "retourne la taille de la file"
        return len(self.p)
