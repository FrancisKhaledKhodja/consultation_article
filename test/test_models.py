import pytest
from sqlmodel import SQLModel, create_engine, Session, select
import sys
import os

# Ajouter le répertoire parent au path Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from creation_base_donnees.models import Article, ArticleManufacturer, Nomenclature


@pytest.fixture(name="engine")
def engine_fixture():
    """Crée une base de données en mémoire pour les tests"""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """Crée une session de base de données pour les tests"""
    with Session(engine) as session:
        yield session


def test_create_article():
    """Test la création d'un article avec les champs minimaux requis"""
    article = Article(
        code_article="TEST001",
        proprietaire_article="TEST",
        libelle_court_article="Test Article"
    )
    assert article.code_article == "TEST001"
    assert article.proprietaire_article == "TEST"
    assert article.libelle_court_article == "Test Article"
    assert article.is_oc is False  # valeur par défaut
    assert article.is_ol is False  # valeur par défaut


def test_create_article_manufacturer():
    """Test la création d'une association Article-Fabricant"""
    article_manufacturer = ArticleManufacturer(
        code_article="TEST001",
        nom_fabricant="Test Manufacturer",
        reference_article_fabricant="REF001"
    )
    assert article_manufacturer.code_article == "TEST001"
    assert article_manufacturer.nom_fabricant == "Test Manufacturer"
    assert article_manufacturer.reference_article_fabricant == "REF001"


def test_create_nomenclature():
    """Test la création d'une nomenclature"""
    nomenclature = Nomenclature(
        code_article_parent="PARENT001",
        code_article_fils="FILS001",
        quantite=2.0
    )
    assert nomenclature.code_article_parent == "PARENT001"
    assert nomenclature.code_article_fils == "FILS001"
    assert nomenclature.quantite == 2.0


def test_article_relationships(session):
    """Test les relations entre les modèles"""
    # Création des objets
    article = Article(
        code_article="TEST001",
        proprietaire_article="TEST",
        libelle_court_article="Test Article"
    )
    
    manufacturer = ArticleManufacturer(
        code_article="TEST001",
        nom_fabricant="Test Manufacturer",
        reference_article_fabricant="REF001"
    )
    
    # Ajout à la session et commit
    session.add(article)
    session.add(manufacturer)
    session.commit()
    
    # Vérification de la relation
    article_db = session.get(Article, "TEST001")
    assert len(article_db.fabricants) == 1
    assert article_db.fabricants[0].nom_fabricant == "Test Manufacturer"


def test_nomenclature_relationships(session):
    """Test les relations de nomenclature"""
    # Création des articles
    parent = Article(
        code_article="PARENT001",
        proprietaire_article="TEST",
        libelle_court_article="Parent Article"
    )
    
    child = Article(
        code_article="CHILD001",
        proprietaire_article="TEST",
        libelle_court_article="Child Article"
    )
    
    nomenclature = Nomenclature(
        code_article_parent="PARENT001",
        code_article_fils="CHILD001",
        quantite=1.0
    )
    
    # Ajout à la session et commit
    session.add(parent)
    session.add(child)
    session.add(nomenclature)
    session.commit()
    
    # Vérification que la nomenclature est bien créée
    nomenclature_db = session.exec(select(Nomenclature)).first()
    assert nomenclature_db.code_article_parent == "PARENT001"
    assert nomenclature_db.code_article_fils == "CHILD001"
    assert nomenclature_db.quantite == 1.0
