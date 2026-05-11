# Simulation de flux réseau

## Description

Ce projet simule un réseau de communication à commutation de paquets afin d’étudier les stratégies de gestion de flux à l’entrée d’un réseau. Il modélise le comportement de paquet générés par des sources, leur stockage dans des buffers, ainsi que leur transmission vers un lien de communication, tout en analysant les performances du système.

---

## Objectif

Le projet vise à :
- simuler l’arrivée de paquets selon un processus de Poisson (λ)
- gérer des files d’attente (buffers) de capacité limitée
- analyser le taux de perte de paquets
- comparer différentes stratégies de gestion de flux

---

## Architecture de l’application

Le projet est composé de deux parties principales :

- `partie1.py` : structures abstraites de données et simulation de base
- `partie2.py` : stratégies avancées de gestion des files d’attente

Chaque partie repose sur trois classes principales :
- `Source` : génération des paquets
- `Buffer` : file d’attente de stockage
- `Paquet` : unité de données du réseau

---

## Analyse des performances

Le système permet de comparer les stratégies en fonction :
- du taux de perte des paquets
- du temps moyen d’attente
- de l'efficacité globale du réseau

---

## Partie 1 (`partie1.py`)

### Fonctionnement du système

Le réseau est composé d’une source et d’un buffer :

1. La source génère des paquets selon une loi de Poisson
2. Les paquets sont stockés dans le buffer de capacité limitée
3. Si le buffer est plein, les paquets entrants sont perdus
4. Les paquets présents dans le buffer sont ensuite transmis vers le lien

Les paramètres du système sont modifiables via l’interface graphique Flet.

### Utilisation :

Lors de l’exécution de `partie1.py`, une interface graphique s’ouvre avec :

- **Démarrer** : lance la simulation
- **Arrivée** : ajoute manuellement un paquet dans le buffer
- **Slider** : ajuste le taux d’arrivée des paquets (λ)
- **Transmission** : envoie un paquet du buffer vers le lien
- **Quitter** : arrête la simulation

---

## Partie 2 (`partie2.py`)

### Stratégies de gestion 

Dans cette deuxième partie, trois stratégies sont implémentées afin de limiter le nombre de paquets perdus :

1. File la plus remplie
   - sélection du buffer secondaire contenant le plus de paquets
2. Tour à tour
   - sélection alternée entre les buffers
3. Aléatoire
   - sélection d’un buffer secondaire de manière aléatoire

### Fonctionnement du système

Le réseau fonctionne avec plusieurs sources, plusieurs buffers secondaires, et un buffer principal :

1. Les sources génèrent des paquets selon une loi de Poisson, qu'elles transmettent à leurs buffers secondaires
2. Les paquets sont stockés dans des buffers secondaires de capacité limitée
3. Si un buffer secondaire est plein, les paquets qu'il reçoit sont perdus
4. Les paquets des buffers secondaires sont ensuite transmis vers le buffer principal de capacité limité, puis vers le lien

Les paramètres modifiables sont situés dans le code (lignes 300 à 325).

### Utilisation :
Lors du lancement de `partie2.py`, la stratégie doit être choisie dans le terminal :

- `1` : file la plus remplie
- `2` : tour à tour
- `3` : aléatoire

Puis appuyer sur **Entrée**.

La simulation se déroule ensuite automatiquement sur l'interface graphique Tkinter.

Lors de l'arrêt de la simulation, les résultats sont affichés dans le terminal :
- temps moyen d'attente
- taux de perte des paquets
