# Importation des librairies
import flet as ft
import random as rd
import threading as th
import time

# Classe Source
class Source:
    numero_id = 0
    def __init__(self):
        Source.numero_id += 1
        self.id = Source.numero_id # Initialisation du numéro de la Source

    def generer_paquet(self): # Fonction qui genère un paquet de la Source et le renvoie
        paquet = Paquet(self.id) # Initialisation de l'identifiant de la Source
        return paquet

# Classe Buffer
class Buffer:
    numero_id = 0
    def __init__(self, capacite):
        Buffer.numero_id += 1
        self.id = Buffer.numero_id # Initialisation du numéro du Buffer
        self.capacite = capacite # Initialisation de la capacité du Buffer
        self.file_attente = [] # Initialisation de la liste d'attente du Buffer
        self.nbr_transmis = 0 # Création du nombre de paquets transmis
        self.nbr_perte = 0 # Création du nombre de paquets perdus

    def arrivee(self, paquet): # Fonction qui traite l'arrivée d'un paquet
        if len(self.file_attente) < self.capacite: # Si le buffer n'est pas plein
            self.file_attente.append(paquet) # Ajout du paquet à la file d'attente
        else:
            print(f"Paquet de la source {paquet.source_id}, de taille {paquet.taille} rejeté") # Sinon le paquet est rejeté
            self.nbr_perte += 1 # Incrémentation du nombre de paquets perdus

    def charge_file_attente(self): # Fonction renvoyant la charge de la file d'attente
        return len(self.file_attente)

    def charge_nbr_transmis(self): # Fonction renvoyant le nombre de paquets transmis
        return self.nbr_transmis

    def charge_nbr_perdu(self): # Fonction renvoyant le nombre de paquets perdus
        return self.nbr_perte
    
    def taux_perte(self): # Fonction renvoyant le taux de perte de paquets
        if self.nbr_transmis > 0: # Vérification  du nombre de paquets transmis pour éviter la division par zéro
            return round(self.nbr_perte/self.nbr_transmis,2)
        return 0

    def transmission(self): # Fonction qui transmet le premier paquet de la liste d'attente du Buffer au lien
        if self.file_attente:
            self.nbr_transmis += 1 # Incrémentation du nombre de paquets transmis
            return self.file_attente.pop(0)
        else:
            return None

# Classe Paquet
class Paquet:
    def __init__(self, source_id):
        self.source_id = source_id # Initialisation du numéro de la Source du paquet
        self.taille = rd.randint(1, 50) # Initialisation de la taille du paquet

# Initialisation des variables globales utilisées pour l'interface graphique
thread = None
lambda_globale = 1
demarrage = False

# Fonction créant l'interface graphique
def main(page: ft.Page):
    page.title = "Réseau"
    page.window_full_screen = True

    # Paramètres modifiables du réseau
    global demarrage, thread
    taux_transmission_lien = rd.randint(0,25) # Initialisation du taux de transmission du lien
    print("Taux du lien : ",taux_transmission_lien)
    buffer = Buffer(rd.randint(5,45)) # Initialisation du Buffer
    sources = [Source() for _ in range(rd.randint(1,5))] # Initialisation des sources (une à cinq sources) 

    # Éléments de l'interface
    texte_transmis = ft.Text(f"Nombre de paquets transmis : {buffer.charge_nbr_transmis()}",size=30, weight="w500",color="green")
    texte_lambda = ft.Text(f"Taux d'arrivée (λ) : {lambda_globale}", size=20, weight="w500")
    slider_lambda = ft.Slider(min=0.1, max=10, divisions=20, value=lambda_globale, on_change=lambda e: actualisation_lambda(e.control.value))
    texte_buffer = ft.Text(f"Paquets dans le Buffer ({buffer.charge_file_attente()})\nCapacité : {buffer.capacite}:",size=40, weight="w500",color="yellow")
    buffer_container = ft.Container(content=ft.Row(),width=buffer.capacite * 38,height=70,bgcolor="black",border_radius=5,padding=5)
    texte_perdus = ft.Text(f"Nombre de paquets perdus : {buffer.charge_nbr_perdu()}",size=30, weight="w500",color="red")
    texte_taux_perte = ft.Text(f"Taux de perte de paquet : {buffer.taux_perte()}%",size=30, weight="w500",color="blue")

    # Fonction actualisant les éléments de l'interface
    def actualisation_texte():
        texte_buffer.value = f"Paquets dans le Buffer ({buffer.charge_file_attente()}):"
        buffer_container.content.controls = [ft.Container(bgcolor="#999900", padding=5, border_radius=5, content=ft.Text(str(p.taille), size=16, weight="w500"), data=p) for p in buffer.file_attente]
        texte_transmis.value = f"Nombre de paquets transmis : {buffer.charge_nbr_transmis()}"
        texte_perdus.value = f"Nombre de paquets perdus : {buffer.charge_nbr_perdu()}"
        texte_taux_perte.value = f"Taux de perte de paquet : {buffer.taux_perte()}%"
        page.update()

    # Fonction traitant l'arrivée des paquets
    def gestion_arrivee(event):
        paquet = rd.choice(sources).generer_paquet() # Crée un paquet 
        if paquet.taille <= taux_transmission_lien: # Envoie directement le paquet si sa taille est inférieur à celle du lien
            print(f"Paquet de la source {paquet.source_id}, de taille {paquet.taille} transmis")
        else:
            buffer.arrivee(paquet) # Envoie le paquet au Buffer
            actualisation_texte()

    # Fonction traitant la transmission des paquets
    def gestion_transmission(event):
        paquet = buffer.transmission() # Retire le paquet arrivé en premier dans le Buffer
        if paquet is not None: # Le transmet si le paquet existe
            print(f"Paquet de la source {paquet.source_id}, de taille {paquet.taille} transmis")
            actualisation_texte()
        else:
            print("Buffer vide")

    # Fonction traitant l'actualisation du taux d'arrivée lambda
    def actualisation_lambda(new_lambda):
        global lambda_globale, thread
        lambda_globale = round(new_lambda,1)
        texte_lambda.value = f"Taux d'arrivée (λ) : {lambda_globale}"
        if thread is not None: # Arrêt du thread si il existe
            thread.join()
        thread = th.Thread(target=thread_arrivee) # Recrée un thread avec la nouvelle valeur de lambda
        thread.start()
        page.update()

    # Fonction faite pour le thread prenant en charge l'arrivée des paquets selon la loi de Poisson
    def thread_arrivee():
        global lambda_globale, demarrage
        while demarrage: # Effectue le processus indéfiniement
            temps_attente = round(rd.expovariate(lambda_globale), 2) # Temps d'attente de la loi de Poisson
            time.sleep(temps_attente) # Attente du temps de poisson
            gestion_arrivee(None)

    # Fonction faite pour le thread prenant en charge la transmission des paquets chaque seconde
    def thread_transmission():
        global demarrage
        while demarrage: # Effectue indéfiniement la transmission d'un paquet chaque seconde 
            time.sleep(1)
            gestion_transmission(None)

    # Initialisation des threads qui feront l'arrivée des paquets et leur transmission
    thread1 = th.Thread(target=thread_arrivee)
    thread2 = th.Thread(target=thread_transmission)

    # Fonction du bouton Démarrer de l'interface graphique démarrant le processus du réseau
    def demarrer(event):
        global demarrage
        demarrage = True
        thread1.start()
        thread2.start()

    # Fonction du bouton Quitter de l'interface graphique fermant la fenêtre graphique
    def quitter(event):
        page.window_close()

    # Ajout des éléments à l'interface graphique
    page.views.append(ft.Column([
        ft.Row([texte_transmis, texte_buffer, texte_perdus],ft.MainAxisAlignment.SPACE_EVENLY),
        ft.Row([buffer_container],ft.MainAxisAlignment.CENTER),
        ft.Row([
            ft.ElevatedButton("Démarrer", on_click=demarrer),
            ft.ElevatedButton("Arrivée", on_click=gestion_arrivee),
            ft.Column([texte_lambda,slider_lambda]),
            ft.ElevatedButton("Transmission", on_click=gestion_transmission),
            ft.ElevatedButton("Quitter", on_click=quitter),
        ],ft.MainAxisAlignment.SPACE_AROUND),
        ft.Row([texte_taux_perte],ft.MainAxisAlignment.CENTER)],
        spacing=150))

    # Actualisation de l'interface graphique
    page.update()

# Lancement de l'interface graphique
ft.app(target=main)