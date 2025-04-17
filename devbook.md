# Journal de Développement

## Vue d'ensemble du Projet

Ce projet concerne la gestion et la consultation d'articles avec leurs nomenclatures. Il permet de :
- Charger des données depuis des fichiers Excel
- Gérer les articles et leurs fabricants
- Gérer les nomenclatures (relations parent-enfant entre articles)
- Stocker les données dans une base SQLite
- Visualiser les articles et leurs images associées via une interface graphique

## Structure du Projet

```
consultation_article/
├── backend/
│   ├── __init__.py
│   └── api.py                  # API pour accéder à la base de données
├── frontend/
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée de l'interface
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── database.py         # Utilitaires base de données
│   │   ├── error_handlers.py   # Gestion des erreurs
│   │   └── logging_config.py   # Configuration des logs
│   └── views/
│       ├── __init__.py
│       ├── details_panel.py    # Panneau de détails
│       ├── image_panel.py      # Panneau d'images
│       ├── main_window.py      # Fenêtre principale
│       ├── parent_tree_panel.py # Arborescence parent
│       ├── search_panel.py     # Panneau de recherche
│       └── tree_panel.py       # Arborescence complète
├── creation_base_donnees/
│   ├── __init__.py
│   ├── constants.py           # Constantes du projet
│   ├── create_database.py     # Création de la base
│   ├── items.py              # Gestion des articles
│   ├── load_file.py          # Chargement des fichiers
│   └── models.py             # Modèles SQLModel
├── test/
│   ├── test_api.py
│   ├── test_items.py
│   ├── test_load_file.py
│   ├── test_models.py
│   └── test_nomenclatures.py
├── data_input/               # Fichiers Excel source
├── database_sqlite/          # Base de données SQLite
├── deployment/               # Dossier de déploiement
│   ├── consultation_article.exe
│   └── database_settings.txt
├── main.py                  # Point d'entrée principal
├── prepare_deployment.bat   # Script de déploiement
├── pyproject.toml          # Configuration du projet
└── README.md
```

## Étapes de Développement

### 1. Vérification de la Cohérence des Modèles

#### Cohérence entre models.py et items.py
- **Article** : Vérification des champs et relations
  - code_article
  - proprietaire_article
  - is_oc
  - is_ol
- **Nomenclature** : Structure parent-enfant cohérente
- **Manufacturer** : Gestion des fabricants alignée

#### Cohérence entre create_database.py et models.py
- Importation correcte des modèles
- Création des tables via SQLModel
- Import des données respectant la structure
- Gestion des relations many-to-many et parent-enfant
- Types de données cohérents

### 2. Mise en Place des Tests

#### Configuration de l'Environnement de Test
1. Ajout de pytest comme dépendance dans pyproject.toml
2. Configuration de la découverte des tests
3. Configuration des packages

#### Tests de Chargement des Fichiers (test_load_file.py)
- Vérification de la lecture des fichiers Excel
- Validation de la structure des DataFrames

#### Tests des Articles (test_items.py)
1. **test_items_initialization** : Création des DataFrames
2. **test_manufacturer_table** : Table des fabricants
3. **test_oc_ol_identifier** : Identification OC/OL
4. **test_items_columns** : Colonnes essentielles
5. **test_no_duplicate_rows** : Absence de doublons
6. **test_dataframes_info** : Informations des DataFrames

#### Tests des Nomenclatures (test_nomenclatures.py)
1. **test_nomenclatures_initialization** : Vérification de l'initialisation
2. **test_nomenclature_dataframe_structure** : Structure du DataFrame
3. **test_get_list_items_with_nomenclature** : Liste des articles
4. **test_nomenclature_dictionary_structure** : Structure du dictionnaire
5. **test_get_item_nomenclature** : Récupération des nomenclatures
6. **test_dataframe_info** : Informations de debug

#### Tests des Modèles (test_models.py)
1. **test_create_article_from_items** : Création d'articles depuis Items
2. **test_create_manufacturer_from_items** : Création de fabricants depuis Items
3. **test_create_nomenclature_from_nomenclatures** : Création de nomenclatures
4. **test_article_manufacturer_relationship** : Relations Article-Manufacturer
5. **test_article_nomenclature_relationship** : Relations parent-enfant

### 3. Développement de l'Interface Utilisateur

#### Interface PyQt (main.py)
- **Fenêtre principale** : ArticleViewer
  - Barre de recherche avec filtrage en temps réel
  - Table des résultats avec colonnes configurables
  - Affichage détaillé des articles sélectionnés
  - Onglets pour les différentes informations :
    - Détails de l'article
    - Fabricants associés
    - Nomenclatures
    - Images

#### Gestion des Images
- Affichage des images associées aux articles
- Navigation entre les images (précédent/suivant)
- Compteur d'images
- Gestion des cas sans image
- Messages d'information clairs pour l'utilisateur

#### API Backend (api.py)
- Fonctions d'accès à la base de données
- Requêtes optimisées avec SQLModel
- Gestion des relations complexes
- Support pour les images en format binaire

## Points Clés de l'Implémentation

### Gestion des Articles
- Utilisation de Polars pour la manipulation des DataFrames
- Identification automatique des articles OC et OL via la colonne feuille_du_catalogue
- Gestion des relations avec les fabricants via ArticleManufacturer

### Gestion des Nomenclatures
- Structure hiérarchique parent-enfant
- Support des quantités pour chaque article fils
- Facteur multiplicateur pour les quantités

### Base de Données
- Utilisation de SQLModel pour l'ORM
- Relations many-to-many pour Article-Manufacturer avec référence article
- Relations parent-enfant pour les nomenclatures avec quantités

## État Actuel

- ✅ Tous les tests passent avec succès
- ✅ Structure du code cohérente et validée
- ✅ Documentation des tests complète
- ✅ Modèles SQLModel validés avec leurs relations
- ✅ Interface utilisateur fonctionnelle
- ✅ Gestion des images implémentée
- ✅ Logs détaillés pour le débogage

## Améliorations Récentes

### Interface Utilisateur
1. Amélioration de la gestion des erreurs
2. Messages plus descriptifs pour l'utilisateur
3. Meilleure gestion des cas où il n'y a pas d'images
4. Logs détaillés pour faciliter le débogage

### Gestion des Images
1. Validation du code article avant chargement
2. Affichage clair quand aucune image n'est disponible
3. Gestion locale des erreurs sans interruption
4. Compteur d'images mis à jour automatiquement

### 4. Améliorations de l'Interface de Recherche

#### Optimisation de l'Affichage des Résultats
- Simplification de la requête SQL pour une meilleure performance
- Retrait des colonnes non essentielles (fabricants)
- Standardisation de l'affichage avec 5 colonnes principales :
  - Code Article
  - Libellé
  - Statut
  - Type
  - Criticité
- Gestion améliorée des valeurs nulles dans l'affichage

## État Actuel

### Fonctionnalités Implémentées
- Chargement et importation des données depuis Excel
- Interface de recherche avec filtrage
- Affichage des détails des articles
- Gestion des nomenclatures
- Tests unitaires complets

### Prochaines Étapes
- Optimisation des performances de recherche
- Améliorations possibles de l'interface utilisateur :
  - Filtrage par colonne spécifique
  - Système de tri avancé
  - Compteur de résultats
  - Export des résultats
  - Amélioration du style du tableau

## Prochaines Étapes Possibles

1. Optimisation de la lecture des fichiers Excel
2. Ajout de validation des données
3. Amélioration de l'interface utilisateur :
   - Zoom sur les images
   - Filtres avancés pour la recherche
   - Export des résultats
4. Gestion des mises à jour de données
5. Support pour d'autres formats d'images
6. Cache des images pour améliorer les performances
