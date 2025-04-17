"""Utilitaires pour la base de données"""
from sqlmodel import create_engine
from pathlib import Path

def get_engine():
    """Retourne le moteur de base de données"""
    # Obtient le chemin absolu du projet
    project_root = Path(__file__).parent.parent.parent.absolute()
    
    # Chemin absolu de la base de données
    db_path = project_root / "database_sqlite" / "articles.db"
    
    # Crée l'URL de connexion
    database_url = f"sqlite:///{db_path}"
    
    # Crée le moteur de base de données
    engine = create_engine(
        database_url,
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    return engine
