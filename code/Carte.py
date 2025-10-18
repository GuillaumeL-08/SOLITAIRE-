class Carte:
    def __init__(self, couleur, valeur, visible=False) -> None:
        self.couleur = couleur
        self.valeur = valeur
        self.visible = visible

    def __repr__(self) -> str :
        return f"{self.valeur}{self.couleur}" if self.visible else "XX"
