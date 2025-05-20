# LE CODE SE TROUVE DANS LA BRANCHE MASTER
TP2 - API REST avec Flask & Neo4j

Ce projet est une API RESTful développée en Python avec Flask, connectée à une base de données Neo4j.  
Il permet de gérer des **utilisateurs**, **posts**, **commentaires**, ainsi que leurs **relations** (amitiés, likes, etc.).

## 🔧 Technologies utilisées

- Python 3
- Flask
- Neo4j
- py2neo
- Docker / Docker Compose
- Git

## 🚀 Fonctionnalités principales

### Utilisateurs
- Créer, lire, modifier, supprimer un utilisateur (CRUD)
- Ajouter ou supprimer un ami
- Vérifier s'ils sont amis ou non
- Voir les amis communs

### Posts
- Créer un post lié à un utilisateur
- Liker / unliker un post
- Afficher les posts d’un utilisateur

### Commentaires
- Ajouter un commentaire à un post
- Liker / unliker un commentaire
- Supprimer ou modifier un commentaire

## ⚙️ Installation

1. **Cloner le projet** :
   ```bash
   git clone https://github.com/Ana34-create/TP2.git
   cd TP2
2 **Installer les dépendances** :

bash
Copier
Modifier
pip install -r requirements.txt
3 **Lancer Neo4j avec Docker Compose** :

docker-compose up
4 **Lancer l’API Flask** :

python app.py
