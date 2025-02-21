# Factory-IO-x-Flask

Ce projet permet de contrôler une simulation Factory I/O en utilisant le protocole Modbus TCP Server et une interface web via Flask.

## Table des Matières
- [Description](#description)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Architecture du Projet](#architecture-du-projet)
- [Améliorations Possibles](#am%C3%A9liorations-possibles)
- [Auteurs](#auteurs)

## Description
Ce projet utilise un serveur Flask pour fournir une interface web permettant de contrôler des convoyeurs et des trieurs de blocs via Modbus. Il comprend :
- Un serveur Flask qui gère les commandes via API REST
- Une interface web pour envoyer des commandes et afficher les compteurs de blocs traités
- Une connexion à un serveur Modbus pour interagir avec Factory I/O

## Installation

### Prérequis
- Python 3.6+
- Factory I/O configuré avec Modbus
- Flask et PyModbusTCP installés

### Installation des dépendances
```bash
pip install flask pyModbusTCP
```

### Lancement du projet
```bash
python main.py
```
Le serveur Flask s'exécutera sur `http://127.0.0.1:5000/`

## Utilisation
### Interface Web
Une interface web est accessible sur `http://127.0.0.1:5000/`. Elle permet de :
- Démarrer et arrêter les convoyeurs
- Activer les trieurs pour les blocs bleus, verts et gris
- Voir les compteurs de blocs traités

### Driver Python
Permet de contrôler l'usine Factory IO :
- Détecte et augmente le compteur avec le capteur d'objet
- Actionne le bon bras en fonction de la couleur du bloc detecté
- Gère le rangement des bras et le bon flux d'arrivée des blocs avec le capteur de sortie


## Architecture du Projet
- **`driver.py`** : Gère la connexion Modbus, les commandes et le serveur Flask
- **`templates/index.html`** : Interface utilisateur pour le contrôle

## Améliorations Possibles
- Gérer l'automatisation du script pour que l'actionnement manuel n'ait pas de comportement néfaste sur le bon triage des blocs.
- Gérer la reconnexion automatique si la connexion Modbus est perdue
- Ajouter un système d'authentification sur l'appli web pour sécuriser les commandes
- Mettre en place une communication sécurisée HTTPS entre flask et le driver Python (si c'est possible).
- Améliorer l'interface avec un design plus ergonomique

## Auteur
Projet développé par [Adam Bouhrara](https://github.com/Adamou02) dans le cadre d'un projet d'automatisation avec Factory I/O.

