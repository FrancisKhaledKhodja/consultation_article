import os
import sys
from unittest.mock import patch

print(os.getcwd())
sys.path.append(os.getcwd())

import pytest
from sqlmodel import Session, SQLModel, create_engine
from backend.api import (
    get_all_articles,
    get_all_manufacturers,
    get_all_nomenclatures,
    get_all_articles_with_manufacturers,
    get_all_articles_with_nomenclatures,
    get_all_articles_with_manufacturers_and_nomenclatures,
    get_all_manufacturers_with_articles,
    get_all_nomenclatures_with_articles,
    get_article_by_code,
    get_manufacturer_by_code,
    get_nomenclature_by_code,
    get_manufacturer_by_article,
    get_nomenclature_by_article,
    get_manufacturers_by_article,
    get_nomenclatures_by_article,
    get_manufacturers_with_articles,
    get_nomenclatures_with_articles
)
from creation_base_donnees.models import Article, ArticleManufacturer, Nomenclature

# Données de test
TEST_ARTICLES = [
    {
        "code_article": "ART001",
        "proprietaire_article": "PROP1",
        "type_article": "TYPE1",
        "libelle_court_article": "Article 1"
    },
    {
        "code_article": "ART002",
        "proprietaire_article": "PROP1",
        "type_article": "TYPE2",
        "libelle_court_article": "Article 2"
    },
    {
        "code_article": "ART003",
        "proprietaire_article": "PROP2",
        "type_article": "TYPE1",
        "libelle_court_article": "Article 3"
    }
]

TEST_MANUFACTURERS = [
    {
        "code_article": "ART001",
        "nom_fabricant": "FAB1",
        "reference_article_fabricant": "REF1"
    },
    {
        "code_article": "ART001",
        "nom_fabricant": "FAB2",
        "reference_article_fabricant": "REF2"
    },
    {
        "code_article": "ART002",
        "nom_fabricant": "FAB1",
        "reference_article_fabricant": "REF3"
    }
]

TEST_NOMENCLATURES = [
    {
        "code_article_parent": "ART001",
        "code_article_fils": "ART002",
        "quantite": 2.0
    },
    {
        "code_article_parent": "ART001",
        "code_article_fils": "ART003",
        "quantite": 1.0
    },
    {
        "code_article_parent": "ART002",
        "code_article_fils": "ART003",
        "quantite": 3.0
    }
]

@pytest.fixture(scope="session")
def engine():
    """Crée une base de données SQLite en mémoire pour les tests"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture
def session(engine):
    """Crée une session de test et insère les données de test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    # Création des articles
    for article_data in TEST_ARTICLES:
        article = Article(**article_data)
        session.add(article)
    
    # Création des fabricants
    for manufacturer_data in TEST_MANUFACTURERS:
        manufacturer = ArticleManufacturer(**manufacturer_data)
        session.add(manufacturer)
    
    # Création des nomenclatures
    for nomenclature_data in TEST_NOMENCLATURES:
        nomenclature = Nomenclature(**nomenclature_data)
        session.add(nomenclature)
    
    session.commit()

    yield session

    # Nettoyage après les tests
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(autouse=True)
def mock_session(session, monkeypatch):
    """Mock la session SQLAlchemy pour utiliser notre session de test"""
    def mock_session_init():
        return session
    
    monkeypatch.setattr("backend.api.Session", lambda: session)

def test_get_all_articles(session):
    """Test la récupération de tous les articles"""
    articles = get_all_articles()
    assert isinstance(articles, list)
    assert len(articles) == 3
    for article in articles:
        assert isinstance(article, Article)

def test_get_all_manufacturers(session):
    """Test la récupération de tous les fabricants"""
    manufacturers = get_all_manufacturers()
    assert isinstance(manufacturers, list)
    assert len(manufacturers) == 3
    for manufacturer in manufacturers:
        assert isinstance(manufacturer, ArticleManufacturer)

def test_get_all_nomenclatures(session):
    """Test la récupération de toutes les nomenclatures"""
    nomenclatures = get_all_nomenclatures()
    assert isinstance(nomenclatures, list)
    assert len(nomenclatures) == 3
    for nomenclature in nomenclatures:
        assert isinstance(nomenclature, Nomenclature)

def test_get_article_by_code(session):
    """Test la récupération d'un article par son code"""
    # Test avec un code existant
    article = get_article_by_code("ART001")
    assert isinstance(article, Article)
    assert article.code_article == "ART001"
    
    # Test avec un code inexistant
    article = get_article_by_code("INVALID_CODE")
    assert article is None

def test_get_manufacturer_by_code(session):
    """Test la récupération d'un fabricant par code article"""
    # Test avec un code existant
    manufacturer = get_manufacturer_by_code("ART001")
    assert isinstance(manufacturer, ArticleManufacturer)
    assert manufacturer.code_article == "ART001"
    
    # Test avec un code inexistant
    manufacturer = get_manufacturer_by_code("INVALID_CODE")
    assert manufacturer is None

def test_get_nomenclature_by_code(session):
    """Test la récupération d'une nomenclature par code article"""
    # Test avec un code existant
    nomenclature = get_nomenclature_by_code("ART001")
    assert isinstance(nomenclature, Nomenclature)
    assert nomenclature.code_article_parent == "ART001"
    
    # Test avec un code inexistant
    nomenclature = get_nomenclature_by_code("INVALID_CODE")
    assert nomenclature is None

def test_get_manufacturers_by_article(session):
    """Test la récupération des fabricants pour un article"""
    # Test avec un code existant
    manufacturers = get_manufacturers_by_article("ART001")
    assert isinstance(manufacturers, list)
    assert len(manufacturers) == 2  # ART001 a deux fabricants
    for manufacturer in manufacturers:
        assert isinstance(manufacturer, ArticleManufacturer)
        assert manufacturer.code_article == "ART001"
    
    # Test avec un code inexistant
    manufacturers = get_manufacturers_by_article("INVALID_CODE")
    assert isinstance(manufacturers, list)
    assert len(manufacturers) == 0

def test_get_nomenclatures_by_article(session):
    """Test la récupération des nomenclatures pour un article"""
    # Test avec un code existant
    nomenclatures = get_nomenclatures_by_article("ART001")
    assert isinstance(nomenclatures, list)
    assert len(nomenclatures) == 2  # ART001 a deux nomenclatures enfants
    for nomenclature in nomenclatures:
        assert isinstance(nomenclature, Nomenclature)
        assert nomenclature.code_article_parent == "ART001"
    
    # Test avec un code inexistant
    nomenclatures = get_nomenclatures_by_article("INVALID_CODE")
    assert isinstance(nomenclatures, list)
    assert len(nomenclatures) == 0

def test_get_manufacturers_with_articles(session):
    """Test la récupération des fabricants avec leurs articles"""
    manufacturers = get_manufacturers_with_articles()
    assert isinstance(manufacturers, list)
    assert len(manufacturers) == 3
    for manufacturer in manufacturers:
        assert isinstance(manufacturer, ArticleManufacturer)
        assert hasattr(manufacturer, "article")

def test_get_nomenclatures_with_articles(session):
    """Test la récupération des nomenclatures avec leurs articles"""
    nomenclatures = get_nomenclatures_with_articles()
    assert isinstance(nomenclatures, list)
    assert len(nomenclatures) == 3
    for nomenclature in nomenclatures:
        assert isinstance(nomenclature, Nomenclature)

def test_get_all_articles_with_manufacturers(session):
    """Test la récupération des articles avec leurs fabricants"""
    articles = get_all_articles_with_manufacturers()
    assert isinstance(articles, list)
    assert len(articles) == 3
    for article in articles:
        assert isinstance(article, Article)
        assert hasattr(article, "fabricants")

def test_get_all_articles_with_nomenclatures(session):
    """Test la récupération des articles avec leurs nomenclatures"""
    articles = get_all_articles_with_nomenclatures()
    assert isinstance(articles, list)
    assert len(articles) == 3
    for article in articles:
        assert isinstance(article, Article)

def test_get_all_articles_with_manufacturers_and_nomenclatures(session):
    """Test la récupération des articles avec leurs fabricants et nomenclatures"""
    articles = get_all_articles_with_manufacturers_and_nomenclatures()
    assert isinstance(articles, list)
    assert len(articles) == 3
    for article in articles:
        assert isinstance(article, Article)
        assert hasattr(article, "fabricants")
