from JeuSolitaire import *

if __name__=="__main__":
    fenetre = tk.Tk()
    fenetre.title("Solitaire - Tableau en files avec images")
    jeu = JeuSolitaire(fenetre)
    fenetre.mainloop()
