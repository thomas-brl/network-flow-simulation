# Importation des libraries
import tkinter as tk
from datetime import datetime as dt
import random as rd
from time import time

# Initialisation du taux du lien et sa liste de paquets transmis
lien = []

# Classe Source
class Source():
    def __init__(self, capacite_buffer, taux_arrivee, id):
        self.id = id # Initialisation de l'identifiant de la Source
        self.buffer = Buffer(capacite_buffer) # Initialisation du Buffer de la Source
        self.taux_arrivee = taux_arrivee # Initialisation du temps d'arrivée de la Source
        self.arrivee_poisson = self.temps_poisson() # Initialisation du temps d'arrivée avec la loi de poisson
        self.nbr_transmis, self.nbr_perdus = 0,0 # Initialisation du nombre de paquets transmis et paquets perdus

    def temps_poisson(self): # Fonction qui renvoie le temps d'arrivée selon la loi de poisson
        return rd.expovariate(self.taux_arrivee)

    def generer_paquet(self): # Fonction qui genère un paquet de la Source et le renvoie
        paquet = Paquet(self.id) # Initialisation de l'identifiant de la Source
        temps_actuel = dt.now()
        paquet.temps_arrivee = f"{temps_actuel.hour}.{temps_actuel.minute}.{temps_actuel.second}" # Initialisation du temps d'arrivée du paquet
        return paquet

    def envoyer_paquet_buffer(self): # Fonction qui envoie un paquet au Buffer
        if time() >= self.arrivee_poisson:
            paquet = self.generer_paquet() # Création du paquet
            if self.buffer.arrivee(paquet): # Vérification si le Buffer est plein ou pas
                temps_actuel = dt.now()
                paquet.temps_arrivee = f"{temps_actuel.hour}.{temps_actuel.minute}.{temps_actuel.second}" # Initialisation du temps d'arrivée du paquet dans le Buffer
                self.arrivee_poisson = self.temps_poisson() # Actualisation du temps d'attente
                self.nbr_transmis += 1 # Incrémentation du nombre de paquets transmis
            else:
                self.buffer.ajout_paquet_perdu(paquet) # Ajout du paquet à la liste des paquets perdus du Buffer
                self.nbr_perdus += 1 # Incrémentation du nombre de paquets perdus

# Classe Buffer
class Buffer():
    def __init__ (self, capacite):
        self.capacite = capacite # Initialisation de la capacité du Buffer
        self.file_attente = [] # Initialisation de la liste de la file d'attente du Buffer
        self.paquet_perdu = [] # Initialisation de la liste des paquets perdus du Buffer

    def ajout_paquet_perdu(self, paquet): # Fonction qui ajoute un paquet perdu à la liste des paquets perdus
        self.paquet_perdu.append(paquet)

    def arrivee(self, paquet): # Fonction qui prend en charge l'arrivée d'un paquet dans le Buffer
        if len(self.file_attente) < self.capacite: # Vérification si le Buffer est plein
            self.file_attente.append(paquet) # Ajout du paquet à la file d'attente
            return True # Retourne True ou False pour la Source
        else:
            return False

    def envoyer_vers_lien(self): # Fonction qui envoie le paquet vers le lien
        paquet_transmis = self.retrait_paquet() # Retrait du paquet arrivé le premier dans le Buffer
        if paquet_transmis is not None: # Vérifie si le paquet existe
            lien.append(paquet_transmis) # Ajout du paquet à la liste de paquets transmis

    def retrait_paquet(self): # Fonction qui retire un paquet de la liste d'attente
        if self.file_attente: # Vérification si la file d'attente du Buffer est vide
            paquet = self.file_attente.pop(0) # Retrait du premier paquet arrivé dans le Buffer
            temps_actuel = dt.now() # Actualisation du temps actuel
            paquet.temps_depart = f"{temps_actuel.hour}.{temps_actuel.minute}.{temps_actuel.second}" # Ajout du temps de départ du paquet
            return paquet
        else:
            return None

    def charge_file_attente(self): # Fonction qui renvoie la taille de la liste d'attente
        return len(self.file_attente)
    
    def charge_paquet_perdu(self): # Fonction qui renvoie la taille de la liste paquet perdus
        return len(self.paquet_perdu)

# Classe Paquet
class Paquet():
    numero_id = 0
    def __init__(self, source):
        Paquet.numero_id += 1 # Initialisation du numero du paquet
        self.id = Paquet.numero_id
        self.contenu = self.generer_contenu_paquet() # Initialisation du contenu du paquet
        self.taille = len(self.contenu) # Initialisation de la taille du paquet
        self.source = source # Initalisation du numéro de la Source du paquet

    def charge_taille(self): # Fonction qui renvoie la taille du contenu du paquet
        return self.taille

    def generer_contenu_paquet(self): # Fonction qui crée le contenu du paquet (des emojis)
        taille_paquet = rd.randint(1, 7)
        emojis = [chr(i) for i in range(127744, 128303)] + [chr(j) for j in range(128512, 128592)]
        return [rd.choice(emojis) for _ in range(taille_paquet)]

# Classe Reseau
class Reseau():
    def __init__(self, parametres_lambda, capacites_buffers, capacite_buffer_princ, strategie):
        self.buffer_principal = Buffer(capacite_buffer_princ) # Initialisation du Buffer principal (capacité modifiable)
        self.sources = [Source(capacite, parametre_lambda, i) for i, (parametre_lambda, capacite) in enumerate(zip(parametres_lambda, capacites_buffers), start=1)] # Initialisation de la liste des Sources
        self.buffers = [source.buffer for source in self.sources] # Initialisation de la liste des Buffers de chaque Source
        self.strategie = strategie # Initialisation de la stratégie choisie
        self.indice_tour_de_role = 0 # Initialisation de l'indice pour la stratégie du tour de rôle

    def taux_perte_reseau(self): # Fonction qui calcule le taux de perte du réseau
        paquets_arrives = self.buffer_principal.charge_file_attente() + sum([i.charge_file_attente() for i in self.buffers]) + len(lien)
        paquets_perdus_sources = sum([i.charge_paquet_perdu() for i in self.buffers])
        paquets_perdus_principal = self.buffer_principal.charge_paquet_perdu()
        paquets_perdus_total = paquets_perdus_sources + paquets_perdus_principal
        paquets_totaux = paquets_perdus_total + paquets_arrives
        if paquets_arrives != 0:
            taux_perte = paquets_perdus_total / paquets_totaux
        else:
            taux_perte = 0
        return round(taux_perte * 100, 2)

    def transmission_paquet(self): # Fonction qui fait transmettre un paquet du Buffer principal vers le lien
        self.buffer_principal.envoyer_vers_lien()

    def choix_paquet(self): # Fonction qui appelle les stratégie en fonction du chiffre qu'on entre
        if self.strategie == 1:
            return self.strategie_max_paquets()
        elif self.strategie == 2:
            return self.strategie_tour_de_role()
        elif self.strategie == 3:
            return self.strategie_aleatoire()
        else:
            return None
   
    def retirer_paquets_sources(self): # Fonction qui retire un paquet à chaque Sources pour les transmettre au Buffer principal
        for source in self.sources:
            paquet = source.buffer.transmission_paquet() # Retrait du paquet de chaque Buffer
            if paquet is not None: # Si le paquet existe
                self.buffer_principal.file_attente.append(paquet)

    # Fonction de la stratégie la file d’attente choisie est celle contenant le plus grand nombre de paquets
    def strategie_max_paquets(self):
        if all(buffer.charge_file_attente() == 0 for buffer in self.buffers):
            return None 
        buffer_avec_max_paquets = max(self.buffers, key=lambda buffer: buffer.charge_file_attente())
        paquet_choisi = buffer_avec_max_paquets.retrait_paquet()
        return paquet_choisi if paquet_choisi else None

    # Fonction de la stratégie d'un paquet est pris de chaque file d’attente, à tour de rôle
    def strategie_tour_de_role(self):
        source_choisie = self.sources[self.indice_tour_de_role]
        self.indice_tour_de_role = (self.indice_tour_de_role + 1) % len(self.sources)
        if source_choisie.buffer.file_attente:
            paquet_choisi = source_choisie.buffer.file_attente.pop(0)
            paquet_choisi.temps_depart = f"{dt.now().hour}.{dt.now().minute}.{dt.now().second}"
            self.buffer_principal.arrivee(paquet_choisi)

    # Fonction de la stratégie la file d’attente est choisie de manière aléatoire
    def strategie_aleatoire(self):
        buffers_non_vide = [buffer for buffer in self.buffers if buffer.charge_file_attente() > 0]
        if not buffers_non_vide:
            return None
        buffer_choisi = rd.choice(buffers_non_vide)
        paquet_choisi = buffer_choisi.file_attente[0]
        temps_actuel = dt.now()
        paquet_choisi.temps_depart = f"{temps_actuel.hour}.{temps_actuel.minute}.{temps_actuel.second}"
        self.buffer_principal.arrivee(paquet_choisi)
        buffer_choisi.file_attente.remove(paquet_choisi)

# Classe Interface
class Interface:
    def __init__(self, master, reseau): # Initialisation de tout les éléments de l'interface graphique
        self.master = master
        self.reseau = reseau
        self.sources = self.reseau.sources
        self.buffer_princ = self.reseau.buffer_principal
        master.title("Réseau de communication")
        self.fenetre_princ = tk.Frame(master)
        self.fenetre_princ.pack(fill=tk.BOTH, expand=True)
        self.buffer_fenetre = tk.Frame(self.fenetre_princ)
        self.buffer_fenetre.grid(row=0, column=0, sticky="nsew")
        label_buffer_princ = tk.Label(self.buffer_fenetre, text=f"Buffer principal",bg="#212121",fg="white",font=("Helvetica", "20", "bold"))
        label_buffer_princ.pack(side=tk.TOP, fill=tk.BOTH)
        self.buffer_canvas = tk.Canvas(self.buffer_fenetre,bg="#212121")
        self.buffer_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.creer_source_buffers()
        self.dessiner_buffer()
        self.arrivee_paquet_buffer_sources()
        self.temps_paquet_transmission()
        self.temps_paquet_transmission_buffer()

    def creer_source_buffers(self): # Fonction qui crée l'affichage des canevas de tous les Buffers
        for i, source in enumerate(self.sources):
            buffer_fenetre = tk.Frame(self.fenetre_princ,bg="#212121")
            buffer_fenetre.grid(row=0, column=i+1, sticky="nsew")
            setattr(self, f"buffer_source{i+1}", buffer_fenetre)
            self.fenetre_princ.columnconfigure(i+1, weight=1)
            self.fenetre_princ.rowconfigure(0, weight=1)
            label_source = tk.Label(buffer_fenetre, text=f"Buffer de la source {i+1}\nTaux d'arrivée : {round(source.taux_arrivee,2)}\nCapacité : {source.buffer.capacite}",bg="#212121",fg="white",font=("Helvetica", f"{70//len(self.sources)}", "bold"))
            label_source.pack(side=tk.TOP, fill=tk.BOTH)
            buffer_canvas = tk.Canvas(buffer_fenetre,bg="#212121")
            buffer_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            setattr(self, f"buffer_canvas_source{i+1}", buffer_canvas)

    def dessiner_buffer(self): # Fonction qui dessine les paquets des Buffers
        self.buffer_canvas.delete("all")
        couleurs = ["#ff8000", "yellow","#59ff00", "green", "#00ffb3", "cyan", "blue", "#a200ff", "magenta", "red"]
        espacement = 5
        x,y = 0,0
        taille_max = 0
        # Dessine pour le Buffer principal
        for index, paquet in enumerate(self.buffer_princ.file_attente):
            largeur_texte, largeur_contenu = 120, 40*paquet.taille
            largeur = max(largeur_texte,largeur_contenu)
            taille = 50
            couleur = couleurs[(paquet.source) % len(couleurs)]
            if x + largeur > self.buffer_canvas.winfo_width():
                x = 0
                y += taille_max + espacement
                taille_max = 0
            self.buffer_canvas.create_rectangle(x, y, x + largeur, y + taille, fill=couleur)
            text_x = x + 5
            text_y = y + 5
            self.buffer_canvas.create_text(text_x, text_y, anchor="nw", text=f"ID paquet : {paquet.id}\n{paquet.contenu}", fill="black", font=("Helvetica", "13", "bold"))
            x += largeur + espacement
            taille_max = max(taille_max, taille)
        self.buffer_canvas.config(scrollregion=self.buffer_canvas.bbox("all"))
        # Dessine pour chaque Buffer de chaque Source
        for i, source in enumerate(self.sources):
            buffer_canvas = getattr(self, f"buffer_canvas_source{i+1}")
            buffer_canvas.delete("all")
            x,y = 0,0
            taille_max = 0
            for index, paquet in enumerate(source.buffer.file_attente):
                largeur = 50 + 10 * len(str(paquet.id))
                taille = 30
                couleur = couleurs[source.id % len(couleurs)]
                if x + largeur > buffer_canvas.winfo_width():
                    x = 0
                    y += taille_max + espacement
                    taille_max = 0
                buffer_canvas.create_rectangle(x, y, x + largeur, y + taille, fill=couleur)
                text_x = x + 5
                text_y = y + 5
                buffer_canvas.create_text(text_x, text_y, anchor="nw", text=f"ID : {paquet.id}", fill="black", font=("Helvetica", "15", "bold"))
                x += largeur + espacement
                taille_max = max(taille_max, taille)
            buffer_canvas.config(scrollregion=buffer_canvas.bbox("all"))

    def arrivee_paquet_buffer_sources(self): # Fonction qui pour chaque Sources effectue la fonction ci dessous
        for source in self.sources:
            self.temps_paquet(source)

    def temps_paquet(self, source): # Fonction qui pour une Source dessine indéfiniement les paquets de son Buffer et attend un temps determiné par poisson
        delai = source.temps_poisson()
        source.envoyer_paquet_buffer()
        self.dessiner_buffer()
        self.master.after(int(delai * 1000), self.temps_paquet, source) # Fonction qui boucle indéfiniement en s'appelant elle-même

    def temps_paquet_transmission(self): # Fonction qui 
        paquet_transmis = self.reseau.transmission_paquet()
        delai_transmis = 0
        if paquet_transmis is not None:
            delai_transmis = int(1000 + paquet_transmis * 15)
            print(int(paquet_transmis))
            self.dessiner_buffer()
        else:
            delai_transmis = 3000
        self.master.after(delai_transmis, self.temps_paquet_transmission)

    def temps_paquet_transmission_buffer(self):
        paquet_a_transmettre = self.reseau.choix_paquet()
        delai_transmis = 0
        if paquet_a_transmettre is not None:
            if self.buffer_princ.charge_file_attente() < self.buffer_princ.capacite:
                self.buffer_princ.file_attente.append(paquet_a_transmettre)
                delai_transmis = int(1000 + paquet_a_transmettre.taille)
                self.dessiner_buffer()
            else:
                self.buffer_princ.paquet_perdu.append(paquet_a_transmettre)
        else:
            delai_transmis = 1000
        self.master.after(delai_transmis, self.temps_paquet_transmission_buffer)

    def calculer_attente_moyenne(self): # Fonction calculant l'attente moyenne des paquets
        total_attente = 0
        total_paquets = self.buffer_princ.charge_file_attente()
        for paquet in self.buffer_princ.file_attente:
            temps_arrivee = paquet.temps_arrivee.split(".")
            temps_depart = paquet.temps_depart.split(".")
            attente = (int(temps_depart[0]) * 3600 + int(temps_depart[1]) * 60 + int(temps_depart[2])) - (int(temps_arrivee[0]) * 3600 + int(temps_arrivee[1]) * 60 + int(temps_arrivee[2]))
            total_attente += attente
        if total_paquets > 0:
            attente_moyenne = round(total_attente / total_paquets ,3)
            return attente_moyenne
        else:
            return 0

    def fermer(self): # Fonction qui s'execute lorsque la fenêtre graphique est fermée
        attente_moyenne, taux_perte = self.calculer_attente_moyenne(), self.reseau.taux_perte_reseau() # Calcule de l'attente moyenne et du taux de perte
        print("")
        print(f"Temps d'attente moyen : {attente_moyenne} secondes | Taux de perte : {taux_perte}%") # Affichage de l'attente moyenne et du taux de perte dans le terminal
        print("")
        self.master.destroy() # Fermeture de la fenêtre


"""↓ Paramètres modifiables en-dessous ↓"""

# Création du nombre de Sources
nbr_sources = rd.randint(1, 10)

# Création des listes du taux d'arrivée et de la capacité de chaque Source 
les_taux, les_capacites = [], []

# Création du taux d'arrivée minimal et maximal d'une Source
min_taux,max_taux = 0.5, 1.5

# Création de la capacité minimale et maximale d'une Source
min_capacite, max_capacite = 1, 99

# Création de la capacité du Buffer principal
capacite_buffer_principal = 20

# Ajout de valeurs aléatoires pour les taux d'arrivée de chaque Source
for _ in range(nbr_sources):
    les_taux.append(rd.uniform(min_taux, max_taux))

# Ajout de valeurs aléatoires pour les capacités des Buffers de chaque Source
for _ in range(nbr_sources):
    les_capacites.append(rd.randint(min_capacite, max_capacite))

# Création de l'indice de la stratégie choisie
indice_strategie_choisie = None

while indice_strategie_choisie not in ["1","2","3"]:
    print("")
    # Entrée de la stratégie choisie
    indice_strategie_choisie = input("Choisissez une stratégie en entrant un chiffre parmis les suivants (1, 2, 3) :\n 1 = Plus grand nombre de paquets | 2 = Tour de rôles | 3 = Aléatoire : ")
indice_strategie_choisie = int(indice_strategie_choisie) # Transforme le string entré en entier
le_reseau = Reseau(les_taux, les_capacites, capacite_buffer_principal, indice_strategie_choisie) # Création du Réseau
base_tk = tk.Tk() # Création de la base graphique tkinter
base_tk.state("zoomed") # Plein écran de la fenêtre
interface = Interface(base_tk, le_reseau) # Création de l'Interface
base_tk.protocol("WM_DELETE_WINDOW", interface.fermer) # Permet de lancer la fonction fermer lors de la fermeture de la fenêtre
base_tk.mainloop() # Démarrage de la fenêtre graphique