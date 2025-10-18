import tkinter as tk
import random
import os
from PIL import Image, ImageTk
from Carte import *
from File import *
from Pile import *

COULEURS = ['♠', '♥', '♦', '♣']
VALEURS = ['A'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']
FEN_WIDTH = 1000
FEN_HEIGHT = 700
NOMBRE_PILES = 7

LARGEUR_CARTE = int(FEN_WIDTH / (NOMBRE_PILES + 5)) 
HAUTEUR_CARTE = int(LARGEUR_CARTE * 1.5)
ESPACE_X = int(LARGEUR_CARTE * 0.3)
ESPACE_Y = int(HAUTEUR_CARTE * 0.3)
DEPART_X = ESPACE_X
DEPART_Y = HAUTEUR_CARTE + ESPACE_Y

def est_rouge(couleur):
    return couleur in ('♥', '♦')

class JeuSolitaire:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.canvas = tk.Canvas(fenetre, width=1000, height=700, bg="darkgreen")
        self.canvas.pack()
        self.cartes = []

        # Tableau en files, autres piles restent des Pile
        self.tableau = [File() for _ in range(NOMBRE_PILES)]
        self.pioche = Pile()
        self.defausse = Pile()
        self.fondations = {c: Pile() for c in COULEURS}

        self.objets_cartes = {}
        self.donnees_glisser = {"items": None, "cartes": None, "x": 0, "y": 0, "provenance": None}

        # Chargement des images
        nom_couleur = {'♣':'trefle', '♠':'pique', '♥':'coeur', '♦':'carreau'}
        nom_valeur = {'A':'as', 'J':'valet', 'Q':'dame', 'K':'roi'}

        # Chargement des images cartes visibles
        self.images_cartes = {}
        for couleur in COULEURS:
            for valeur in VALEURS:
                val = nom_valeur.get(valeur, valeur)
                coul = nom_couleur[couleur]
                nom_fichier = f"{val}_{coul}.gif"  # ou .png si nécessaire
                chemin = os.path.join("cartes", nom_fichier)
                try:
                    img = Image.open(chemin)
                    # Redimensionner à la taille des cartes
                    img = img.resize((LARGEUR_CARTE, HAUTEUR_CARTE), Image.Resampling.LANCZOS)
                    self.images_cartes[f"{valeur}{couleur}"] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Image manquante ou erreur: {chemin} ({e})")


        # Image face cachée
        try:
            img = Image.open(os.path.join("cartes", "back.jpeg"))
            img = img.resize((LARGEUR_CARTE, HAUTEUR_CARTE), Image.Resampling.LANCZOS)
            self.img_face_cachee = ImageTk.PhotoImage(img)
        except Exception as e:
            self.img_face_cachee = None
            print("Image back.jpeg manquante ou erreur:", e)


        self.initialiser_jeu()

    def initialiser_jeu(self):
        self.creer_paquet()
        self.distribuer_cartes()
        self.afficher_tout()

    def creer_paquet(self):
        self.cartes = [Carte(c, v) for c in COULEURS for v in VALEURS]
        random.shuffle(self.cartes)

    def distribuer_cartes(self):
        for i in range(NOMBRE_PILES):
            for j in range(i + 1):
                carte = self.cartes.pop()
                carte.visible = (j == i)
                self.tableau[i].enfiler(carte)
        for carte in self.cartes:
            self.pioche.empiler(carte)
        self.cartes = []

    # ---------- Affichage ----------
    def afficher_tout(self):
            # On efface uniquement les anciennes cartes et textes pour tout redessiner
            self.canvas.delete("carte")
            self.canvas.delete("texte")

            # --- Fondations ---
            for i, couleur in enumerate(COULEURS):
                x = DEPART_X + (3 + i) * (LARGEUR_CARTE + ESPACE_X)
                y = 20

                self.canvas.create_text(
                    x + LARGEUR_CARTE//2, y - 10,
                    text=couleur,
                    font=("Helvetica", 16, "bold"),
                    fill="white",
                    tags="texte"
                )

                carte_haut = self.fondations[couleur].sommet()
                self.afficher_carte(x, y, carte_haut, tag=f"fondation_{couleur}")

            # --- Pioche ---
            carte_pioche = self.pioche.sommet()
            self.afficher_carte(DEPART_X, 20, carte_pioche, tag="pioche", face_cachee=(not self.pioche.est_vide()))

            # Zone cliquable pour piocher
            zone_pioche = self.canvas.create_rectangle(
                DEPART_X, 20, DEPART_X + LARGEUR_CARTE, 20 + HAUTEUR_CARTE,
                outline="", fill="", tags="zone_pioche"
            )
            self.canvas.tag_bind(zone_pioche, "<Button-1>", lambda e: self.clic_pioche())

            # --- Défausse (afficher les 3 dernières cartes) ---
            cartes_defausse = self.defausse.pile[-3:]
            x0 = DEPART_X + LARGEUR_CARTE + ESPACE_X
            for i, carte in enumerate(cartes_defausse):
                draggable = (i == len(cartes_defausse) - 1)
                self.afficher_carte(
                    x0 + i * 20, 20, carte,
                    tag="defausse",
                    index_pile=None if not draggable else "defausse"
                )

            # --- Tableau principal ---
            for idx_file, file in enumerate(self.tableau):
                x = DEPART_X + idx_file * (LARGEUR_CARTE + ESPACE_X)
                y = DEPART_Y
                for carte in file.p:
                    self.afficher_carte(x, y, carte, index_pile=idx_file)
                    y += ESPACE_Y

    def afficher_carte(self, x, y, carte, tag="carte", face_cachee=False, index_pile=None, draggable=True):
            if carte is None:
                self.canvas.create_rectangle(x, y, x+LARGEUR_CARTE, y+HAUTEUR_CARTE, fill="gray", tags=tag)
                return

            img = self.img_face_cachee if face_cachee or not carte.visible else \
                self.images_cartes.get(f"{carte.valeur}{carte.couleur}", self.img_face_cachee)

            if img is None:
                rect = self.canvas.create_rectangle(
                    x, y, x+LARGEUR_CARTE, y+HAUTEUR_CARTE,
                    fill="white", tags=(tag, "carte")
                )
            else:
                img_id = self.canvas.create_image(x, y, anchor="nw", image=img, tags=(tag, "carte"))
                self.objets_cartes[carte] = (img_id,)

                if draggable and index_pile is not None:
                    self.canvas.tag_bind(img_id, "<ButtonPress-1>", lambda e, c=carte, p=index_pile: self.debut_glisser(e, c, p))
                    self.canvas.tag_bind(img_id, "<B1-Motion>", self.mouvement_glisser)
                    self.canvas.tag_bind(img_id, "<ButtonRelease-1>", self.fin_glisser)

    # ---------- Drag & Drop ----------
    def debut_glisser(self, event, carte, provenance):
        if not carte.visible:
            return

        # Déterminer la provenance
        if self.pioche.sommet() == carte:
            provenance = "pioche"
        elif self.defausse.sommet() == carte:
            provenance = "defausse"
        # sinon provenance est déjà un index (tableau)

        # Si carte dans le tableau, prendre toutes les cartes visibles à partir de celle-ci
        cartes_a_bouger = [carte]
        if isinstance(provenance, int):
            file_source = self.tableau[provenance]
            idx = file_source.p.index(carte)
            cartes_a_bouger = file_source.p[idx:]

        # Récupérer les objets canvas correspondants
        items = []
        for c in cartes_a_bouger:
            items.extend(self.objets_cartes.get(c, ()))

        # 🔹 S'assurer que la carte (ou le groupe) est au-dessus de toutes les autres
        for obj in items:
            self.canvas.tag_raise(obj)

        # 🔹 Enregistrer les données du drag
        self.donnees_glisser.update({
            "items": items,
            "cartes": cartes_a_bouger,
            "x": event.x,
            "y": event.y,
            "provenance": provenance
        })


    def mouvement_glisser(self, event):
        data = self.donnees_glisser
        if not data["items"]: return
        dx = event.x - data["x"]
        dy = event.y - data["y"]
        for obj in data["items"]:
            self.canvas.move(obj, dx, dy)
        data["x"], data["y"] = event.x, event.y

    def fin_glisser(self, event):
        data = self.donnees_glisser
        cartes = data.get("cartes")
        provenance = data.get("provenance")
        if not cartes:
            return

        carte_principale = cartes[0]
        deplacement_valide = False

        # Vérifier si on lâche sur une fondation
        couleur_fond = self.obtenir_fondation(event.x, event.y)
        if couleur_fond:
            ancien_taille = self.fondations[couleur_fond].taille()
            self.deplacer_vers_fondation(carte_principale, provenance, couleur_fond)
            if self.fondations[couleur_fond].taille() > ancien_taille:
                deplacement_valide = True

        else:
            # Sinon, sur le tableau
            pile_idx = self.obtenir_index_tableau(event.x)
            if pile_idx is not None:
                ancien_taille = self.tableau[pile_idx].taille()
                self.deplacer_vers_tableau(carte_principale, provenance, pile_idx)
                if self.tableau[pile_idx].taille() > ancien_taille:
                    deplacement_valide = True

        # 🔹 Si le déplacement n’est pas valide → remettre la carte dans sa pile d’origine
        if not deplacement_valide:
            if provenance == "defausse":
                for c in cartes:
                    if c not in self.defausse.pile:
                        self.defausse.empiler(c)
            elif provenance == "pioche":
                for c in cartes:
                    if c not in self.pioche.pile:
                        self.pioche.empiler(c)
            elif isinstance(provenance, int):
                file_source = self.tableau[provenance]
                for c in cartes:
                    if c not in file_source.p:
                        file_source.enfiler(c)

        # 🔹 Supprimer les images temporaires du drag
        if data["items"]:
            for obj in data["items"]:
                self.canvas.delete(obj)

        # 🔹 Réinitialiser le drag et redessiner
        self.donnees_glisser = {"items": None, "cartes": None, "x": 0, "y": 0, "provenance": None}
        self.afficher_tout()

    def obtenir_fondation(self, x, y):
        for i,couleur in enumerate(COULEURS):
            fx = DEPART_X + (3+i)*(LARGEUR_CARTE+ESPACE_X)
            fy = 20
            if fx <= x <= fx+LARGEUR_CARTE and fy <= y <= fy+HAUTEUR_CARTE:
                return couleur
        return None

    def obtenir_index_tableau(self, x):
        for i in range(NOMBRE_PILES):
            pile_x = DEPART_X + i*(LARGEUR_CARTE+ESPACE_X)
            if pile_x <= x <= pile_x+LARGEUR_CARTE:
                return i
        return None

    # ---------- Déplacements logiques ----------
    def deplacer_vers_fondation(self, carte, provenance, couleur):
        fond = self.fondations[couleur]
        valeur_attendue = VALEURS[fond.taille()]
        if carte.couleur != couleur or carte.valeur != valeur_attendue:
            return

        if provenance in ("defausse", "pioche"):
            # La carte doit être le sommet de la défausse
            if self.defausse.sommet() == carte:
                self.defausse.depiler()
                fond.empiler(carte)
        elif isinstance(provenance,int):
            pile = self.tableau[provenance]
            if pile.p and pile.p[-1]==carte:
                pile.p.pop()
                fond.empiler(carte)
                if pile.p:
                    pile.p[-1].visible=True


    def deplacer_vers_tableau(self, carte, provenance, destination):
        dest = self.tableau[destination]

        # déterminer la source
        if provenance == "defausse":
            source = self.defausse
        elif provenance == "pioche":
            source = self.pioche
        elif isinstance(provenance, int):
            source = self.tableau[provenance]
        else:
            return

        # --- extraire les cartes à bouger ---
        cartes_a_bouger = []
        if isinstance(source, Pile):
            if source.sommet() != carte:
                return
            cartes_a_bouger = [source.depiler()]

        elif isinstance(source, File):
            # On vide la file jusqu’à trouver la carte
            tampon = File()
            trouve = False
            while not source.est_vide():
                c = source.defiler()
                if c == carte or trouve:
                    trouve = True
                    cartes_a_bouger.append(c)
                else:
                    tampon.enfiler(c)
            # on remet les cartes du tampon dans la source
            while not tampon.est_vide():
                source.enfiler(tampon.defiler())

        # --- vérification du mouvement ---
        if dest.est_vide():
            if cartes_a_bouger[0].valeur != "K":
                for c in cartes_a_bouger:
                    source.enfiler(c)
                    return
        else:
            haut = dest.p[-1]
            if not self.deplacement_valide(cartes_a_bouger[0], haut):
                for c in cartes_a_bouger:
                    if isinstance(source, File):
                        source.enfiler(c)
                    else:  # Pile
                        source.empiler(c)
                return

        # --- déplacement vers la destination ---
        for c in cartes_a_bouger:
            if isinstance(dest, File):
                dest.enfiler(c)
            else:  # Pile
                dest.empiler(c)

        # --- rendre visible la nouvelle carte de la source ---
        if isinstance(source, File) and not source.est_vide():
            source.p[-1].visible = True
        elif isinstance(source, Pile) and not source.est_vide():
            source.sommet().visible = True


    def deplacement_valide(self, carte_bougee, carte_cible):
        couleur1 = "rouge" if carte_bougee.couleur in ['♥','♦'] else "noir"
        couleur2 = "rouge" if carte_cible.couleur in ['♥','♦'] else "noir"
        if couleur1 == couleur2: return False
        valeurs_num = {v:i for i,v in enumerate(VALEURS,1)}
        return valeurs_num[carte_bougee.valeur] == valeurs_num[carte_cible.valeur]-1

    # ---------- Pioche ----------
    def clic_pioche(self):
        if not self.pioche.est_vide():
            nb = min(3, self.pioche.taille())
            for _ in range(nb):
                carte = self.pioche.depiler()
                carte.visible = True
                self.defausse.empiler(carte)
        else:
            # Remettre la défausse dans la pioche
            while not self.defausse.est_vide():
                carte = self.defausse.depiler()
                carte.visible = False
                self.pioche.empiler(carte)
        self.afficher_tout()
