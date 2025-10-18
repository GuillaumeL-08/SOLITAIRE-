import tkinter as tk
import random
from Carte import *
from File import *
from Pile import *

COULEURS = ['♠', '♥', '♦', '♣']
VALEURS = ['A'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']
LARGEUR_CARTE = 60
HAUTEUR_CARTE = 90
ESPACE_X = 20
ESPACE_Y = 20
DEPART_X = 50
DEPART_Y = 150
NOMBRE_PILES = 7

class JeuSolitaire:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.canvas = tk.Canvas(fenetre, width=1000, height=700, bg="darkgreen")
        self.canvas.pack()
        self.cartes = []
        self.tableau = [Pile() for _ in range(NOMBRE_PILES)]
        self.pioche = Pile()
        self.defausse = Pile()
        self.fondations = {couleur: Pile() for couleur in COULEURS}
        self.objets_cartes = {}
        self.donnees_glisser = {
            "item": None,
            "cartes": None,
            "x": 0,
            "y": 0,
            "provenance": None,
            "positions": None
        }
        self.initialiser_jeu()

    def initialiser_jeu(self):
        self.creer_paquet()
        self.distribuer_cartes()
        self.afficher_tout()

    def creer_paquet(self):
        self.cartes = [Carte(couleur, valeur) for couleur in COULEURS for valeur in VALEURS]
        random.shuffle(self.cartes)

    def distribuer_cartes(self):
        for i in range(NOMBRE_PILES):
            for j in range(i + 1):
                carte = self.cartes.pop()
                carte.visible = (j == i)
                self.tableau[i].empiler(carte)
        for carte in self.cartes:
            self.pioche.empiler(carte)
        self.cartes = []

    def obtenir_fondation(self, x, y):
        for i, couleur in enumerate(COULEURS):
            fx = DEPART_X + (3 + i) * (LARGEUR_CARTE + ESPACE_X)
            fy = 20
            if fx <= x <= fx + LARGEUR_CARTE and fy <= y <= fy + HAUTEUR_CARTE:
                return couleur
        return None

    def afficher_tout(self):
        self.canvas.delete("carte")
        self.canvas.delete("texte")

        for i, couleur in enumerate(COULEURS):
            x = DEPART_X + (3 + i) * (LARGEUR_CARTE + ESPACE_X)
            y = 5
            self.canvas.create_text(
                x + LARGEUR_CARTE // 2,
                y,
                text=f"{couleur}",
                font=("Helvetica", 14, "bold"),
                fill="white",
                tags="texte"
            )

        # Pioche
        carte_pioche = self.pioche.sommet()
        self.afficher_carte(DEPART_X, 20, carte_pioche, tag="pioche", face_cachee=True)
        zone_pioche = self.canvas.create_rectangle(
            DEPART_X, 20, DEPART_X + LARGEUR_CARTE, 20 + HAUTEUR_CARTE,
            outline="", fill="", tags=("zone_pioche",)
        )
        self.canvas.tag_bind(zone_pioche, "<Button-1>", lambda e: self.clic_pioche())

        # Défausse
        carte_defausse = self.defausse.sommet()
        self.afficher_carte(DEPART_X + LARGEUR_CARTE + ESPACE_X, 20, carte_defausse, tag="defausse")

        # Fondations
        for i, couleur in enumerate(COULEURS):
            x = DEPART_X + (3 + i) * (LARGEUR_CARTE + ESPACE_X)
            y = 20
            carte_haut = self.fondations[couleur].sommet()
            self.afficher_carte(x, y, carte_haut, tag=f"fondation_{couleur}")
            zone = self.canvas.create_rectangle(
                x, y, x + LARGEUR_CARTE, y + HAUTEUR_CARTE,
                outline="", fill="", tags=(f"zone_fondation_{couleur}",)
            )
            self.canvas.tag_bind(zone, "<ButtonRelease-1>", lambda e, c=couleur: self.deposer_vers_fondation(e, c))

        # Tableau principal
        for index_pile, pile in enumerate(self.tableau):
            x = DEPART_X + index_pile * (LARGEUR_CARTE + ESPACE_X)
            y = DEPART_Y
            for carte in pile.pile:
                self.afficher_carte(x, y, carte, index_pile=index_pile)
                y += ESPACE_Y

    def afficher_carte(self, x, y, carte, tag="carte", face_cachee=False, index_pile=None):
        if carte is None:
            self.canvas.create_rectangle(x, y, x + LARGEUR_CARTE, y + HAUTEUR_CARTE, fill="gray", tags=tag)
            return

        couleur_fond = "blue" if face_cachee or not carte.visible else "white"
        texte = "" if face_cachee or not carte.visible else f"{carte.valeur}{carte.couleur}"

        rect = self.canvas.create_rectangle(
            x, y, x + LARGEUR_CARTE, y + HAUTEUR_CARTE,
            fill=couleur_fond, outline="black", tags=(tag, "carte")
        )
        texte_id = self.canvas.create_text(
            x + LARGEUR_CARTE // 2, y + HAUTEUR_CARTE // 2,
            text=texte, font=("Helvetica", 12, "bold"), tags=(tag, "carte")
        )

        self.objets_cartes[carte] = (rect, texte_id)

        for objet in (rect, texte_id):
            origine = "defausse" if tag == "defausse" else index_pile
            self.canvas.tag_bind(objet, "<ButtonPress-1>", lambda e, c=carte, p=origine: self.debut_glisser(e, c, p))
            self.canvas.tag_bind(objet, "<B1-Motion>", self.mouvement_glisser)
            self.canvas.tag_bind(objet, "<ButtonRelease-1>", self.fin_glisser)

    def debut_glisser(self, event, carte, provenance):
        if not carte.visible:
            return

        cartes_a_bouger = []
        if isinstance(provenance, int):
            pile = self.tableau[provenance].pile
            index = pile.index(carte)
            cartes_a_bouger = pile[index:]
        else:
            cartes_a_bouger = [carte]

        objets = []
        positions = []
        for c in cartes_a_bouger:
            rect, texte = self.objets_cartes[c]
            objets.extend([rect, texte])
            coords = self.canvas.coords(rect)
            positions.append((coords[0], coords[1]))  # sauvegarde la position d’origine

        self.donnees_glisser.update({
            "item": objets,
            "cartes": cartes_a_bouger,
            "x": event.x,
            "y": event.y,
            "provenance": provenance,
            "positions": positions
        })

        for objet in objets:
            self.canvas.tag_raise(objet)

    def mouvement_glisser(self, event):
        cartes = self.donnees_glisser.get("cartes", [])
        if not cartes:
            return

        dx = event.x - self.donnees_glisser["x"]
        dy = event.y - self.donnees_glisser["y"]

        for i, carte in enumerate(cartes):
            rect, texte = self.objets_cartes[carte]
            self.canvas.move(rect, dx, dy)
            self.canvas.move(texte, dx, dy)

        self.donnees_glisser["x"] = event.x
        self.donnees_glisser["y"] = event.y

    def fin_glisser(self, event):
        cartes = self.donnees_glisser.get("cartes", [])
        provenance = self.donnees_glisser["provenance"]
        if not cartes:
            return

        carte_base = cartes[0]
        couleur_fondation = self.obtenir_fondation(event.x, event.y)

        if couleur_fondation is not None:
            # Tentative de déplacement vers une fondation
            self.deplacer_vers_fondation(carte_base, provenance, couleur_fondation)
        else:
            # Tentative de déplacement vers une pile du tableau
            pile_destination = self.obtenir_index_tableau(event.x)
            if pile_destination is not None:
                self.deplacer_sequence_vers_tableau(cartes, provenance, pile_destination)
            else:
                # Retour à la position d’origine si le déplacement est invalide
                self.afficher_tout()

        self.donnees_glisser = {"item": None, "cartes": None, "x": 0, "y": 0, "provenance": None}
        self.afficher_tout()

    def deplacer_vers_fondation(self, carte, provenance, couleur):
        fondation = self.fondations[couleur]

        # ⚠️ Si la fondation est pleine, on sort
        if fondation.taille() >= len(VALEURS):
            return

        # Déterminer la valeur attendue
        valeur_attendue = VALEURS[fondation.taille()]

        # Vérifie que la carte correspond à la couleur et la valeur attendue
        if carte.couleur != couleur or carte.valeur != valeur_attendue:
            return

        # ✅ Déplacer la carte depuis sa source vers la fondation
        if provenance == "defausse":
            if self.defausse.sommet() == carte:
                self.defausse.depiler()
                fondation.empiler(carte)

        elif isinstance(provenance, int):
            pile = self.tableau[provenance]
            if pile.sommet() == carte:
                pile.depiler()
                fondation.empiler(carte)
                if not pile.est_vide():
                    pile.sommet().visible = True


    def deplacer_sequence_vers_tableau(self, cartes, provenance, destination):
        dest = self.tableau[destination]

        # ✅ Déterminer la pile source (tableau ou défausse)
        if provenance == "defausse":
            source = self.defausse
        else:
            source = self.tableau[provenance]

        carte_base = cartes[0]

        # Vérifier si le mouvement est autorisé
        if dest.est_vide():
            if carte_base.valeur != "K":
                return
        else:
            haut = dest.sommet()
            if not self.deplacement_valide(carte_base, haut):
                return

        # Retirer la séquence de la source
        if provenance == "defausse":
            source.depiler()  # On ne déplace qu'une carte depuis la défausse
        else:
            pile_source = source.pile
            index = pile_source.index(carte_base)
            source.pile = pile_source[:index]

        # Empiler la séquence sur la destination
        for c in cartes:
            dest.empiler(c)

        # Retourner la dernière carte visible de la source (si tableau)
        if provenance != "defausse" and not source.est_vide():
            source.sommet().visible = True


    def obtenir_index_tableau(self, x):
        for i in range(NOMBRE_PILES):
            pile_x = DEPART_X + i * (LARGEUR_CARTE + ESPACE_X)
            if pile_x <= x <= pile_x + LARGEUR_CARTE:
                return i
        return None

    def deplacement_valide(self, carte_bougee, carte_cible):
        couleur1 = "rouge" if carte_bougee.couleur in ['♥', '♦'] else "noir"
        couleur2 = "rouge" if carte_cible.couleur in ['♥', '♦'] else "noir"
        if couleur1 == couleur2:
            return False
        valeurs_num = {v: i for i, v in enumerate(VALEURS, start=1)}
        return valeurs_num[carte_bougee.valeur] == valeurs_num[carte_cible.valeur] - 1

    def clic_pioche(self):
        if not self.pioche.est_vide():
            carte = self.pioche.depiler()
            carte.visible = True
            self.defausse.empiler(carte)
        else:
            temp = []
            while not self.defausse.est_vide():
                c = self.defausse.depiler()
                c.visible = False
                temp.append(c)
            for c in temp:
                self.pioche.empiler(c)
        self.afficher_tout()
