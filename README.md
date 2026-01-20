# snek_neural_network

Ce projet est un jeu Snake 3D contrôlé par une IA utilisant PPO (Proximal Policy Optimization) avec PyTorch et Pygame.

## Fonctionnalités principales
- Environnement Snake 3D avec obstacles et cibles dynamiques
- Vue isométrique (pseudo-3D) avec Pygame
- Récompenses pour atteindre la cible, punitions pour rester bloqué ou collision
- Réinitialisation de la cible et des obstacles après chaque réussite
- Entraînement de l'IA avec PPO (PyTorch)
- Boucle d'entraînement et visualisation en temps réel

## Structure du projet
- `env3d.py` : environnement Snake 3D
- `renderer.py` : affichage isométrique
- `renderer3d.py` : affichage 3D avec moderngl
- `ppo_agent.py` : agent PPO (PyTorch)
- `train.py` : boucle d'entraînement et d'évaluation

## Dépendances
- PyTorch
- Pygame
- NumPy
- moderngl
- pyrr

## Lancement
Installez les dépendances puis lancez :

```
pip install torch pygame numpy moderngl pyrr
python train.py
```

## Personnalisation
- La taille de la grille, le nombre d'obstacles et les hyperparamètres PPO sont modifiables dans le code.

## TODO
- Sauvegarde/chargement du modèle
- Statistiques d'entraînement
- Tests unitaires

