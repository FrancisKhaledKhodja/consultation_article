# Consultation Article

Application de gestion et consultation d'articles avec leurs nomenclatures.

## Fonctionnalités

- Recherche d'articles avec filtrage en temps réel
- Affichage des détails des articles (informations, statut, type, criticité)
- Gestion des nomenclatures (relations parent-enfant entre articles)
- Interface graphique intuitive avec PyQt6
- Base de données SQLite pour le stockage des données

## Prérequis

- Python 3.8 ou supérieur
- uv (gestionnaire de paquets Python rapide)

## Installation

1. Cloner le dépôt :
```bash
git clone [URL_DU_DEPOT]
cd consultation_article
```

2. Installer uv si ce n'est pas déjà fait :
```bash
pip install uv
```

3. Installer les dépendances avec uv :
```bash
uv pip install --system
```

## Configuration

1. Placer les fichiers Excel source dans le dossier `data_input/`
2. Configurer les paramètres de la base de données dans `database_settings.txt`

## Utilisation

1. Lancer l'application :
```bash
python main.py
```

2. Interface de recherche :
   - Entrer un terme de recherche dans la barre de recherche
   - Les résultats s'affichent dans le tableau avec 5 colonnes :
     * Code Article
     * Libellé
     * Statut
     * Type
     * Criticité

3. Navigation :
   - Cliquer sur un article pour voir ses détails
   - Utiliser les onglets pour voir différentes informations :
     * Détails de l'article
     * Nomenclatures associées
     * Images (si disponibles)

## Structure du Projet

```
consultation_article/
├── backend/           # API et accès base de données
├── frontend/         # Interface utilisateur PyQt
├── creation_base_donnees/
│   ├── items.py      # Gestion articles/nomenclatures
│   ├── models.py     # Modèles de données
│   └── ...
├── test/            # Tests unitaires
├── data_input/      # Fichiers Excel source
└── database_sqlite/ # Base de données
```

## Tests

Lancer les tests unitaires :
```bash
uv pip install pytest
pytest
```

## Gestion des Dépendances

Le projet utilise Poetry pour la gestion des dépendances, avec uv comme gestionnaire de paquets pour de meilleures performances. Les dépendances sont définies dans `pyproject.toml`.

Pour ajouter une nouvelle dépendance :
```bash
uv pip install <package>
```

## Création de l'Exécutable Windows

Pour créer un exécutable Windows autonome :

1. Installer PyInstaller :
```bash
uv pip install pyinstaller
```

2. Lancer le script de déploiement :
```bash
.\prepare_deployment.bat
```

L'exécutable sera créé dans le dossier `dist/` avec la structure suivante :
```
dist/
├── consultation_article.exe  # Exécutable principal
└── articles.db              # Base de données
```

Note : La base de données doit toujours être dans le même dossier que l'exécutable.

## Documentation Développeur

Pour plus de détails sur le développement, consulter le fichier `devbook.md`.