from JeuSolitaire import *
# Lancement du jeu
if __name__=="__main__":
    fenetre = tk.Tk()
    fenetre.title("Solitaire")
    jeu = JeuSolitaire(fenetre)
    fenetre.mainloop()
