import os
import sys

sys.path.append(os.getcwd())

import pytest
import polars as pl
from creation_base_donnees.items import Nomenclatures
from creation_base_donnees.constants import folder_path_input, file_name_531, sheet_name_531


@pytest.fixture
def nomenclatures_instance():
    """Fixture pour créer une instance de Nomenclatures pour les tests"""
    return Nomenclatures(folder_path_input, file_name_531, sheet_name_531)


def test_nomenclatures_initialization(nomenclatures_instance):
    """Test l'initialisation de la classe Nomenclatures"""
    assert isinstance(nomenclatures_instance.df, pl.DataFrame)
    assert hasattr(nomenclatures_instance, "nomenclature_dictionnary")
    assert isinstance(nomenclatures_instance.nomenclature_dictionnary, dict)


def test_nomenclature_dataframe_structure(nomenclatures_instance):
    """Test la structure du DataFrame des nomenclatures"""
    required_columns = [
        "article",
        "article_eqpt_article_fils",
        "art_et_art_fils_eqpt_quantite"
    ]
    for col in required_columns:
        assert col in nomenclatures_instance.df.columns
    assert nomenclatures_instance.df.shape[0] > 0


def test_get_list_items_with_nomenclature(nomenclatures_instance):
    """Test la récupération de la liste des articles avec nomenclature"""
    items_with_nomenclature = nomenclatures_instance._get_list_items_with_nomenclature(nomenclatures_instance.df)
    assert isinstance(items_with_nomenclature, list)
    assert len(items_with_nomenclature) > 0
    # Vérifie que la liste est triée
    assert items_with_nomenclature == sorted(items_with_nomenclature)


def test_nomenclature_dictionary_structure(nomenclatures_instance):
    """Test la structure du dictionnaire des nomenclatures"""
    assert len(nomenclatures_instance.nomenclature_dictionnary) > 0
    
    # Vérifie la structure pour chaque article parent
    for parent_code, children in nomenclatures_instance.nomenclature_dictionnary.items():
        assert isinstance(parent_code, str)
        assert isinstance(children, list)
        assert len(children) > 0
        
        # Vérifie la structure pour chaque article fils
        for child in children:
            assert isinstance(child, dict)
            assert "code_article" in child
            assert "quantite" in child
            assert isinstance(child["code_article"], str)
            assert isinstance(child["quantite"], (int, float))


def test_get_item_nomenclature(nomenclatures_instance):
    """Test la récupération de la nomenclature d'un article"""
    # Prend le premier article parent comme exemple
    parent_code = next(iter(nomenclatures_instance.nomenclature_dictionnary))
    
    # Test sans paramètres optionnels
    nomenclature = nomenclatures_instance.get_item_nomenclature(parent_code)
    assert isinstance(nomenclature, dict)
    assert "code_article" in nomenclature
    assert "quantite" in nomenclature
    assert "article_fils" in nomenclature
    assert isinstance(nomenclature["article_fils"], list)
    
    # Test avec paramètres optionnels (multiplying_factor uniquement)
    nomenclature_with_params = nomenclatures_instance.get_item_nomenclature(
        parent_code,
        multiplying_factor=2
    )
    assert isinstance(nomenclature_with_params, dict)
    assert nomenclature_with_params["quantite"] == 2  # Quantité de base est 1, donc * 2 = 2


def test_dataframe_info(nomenclatures_instance):
    """Test et affiche les informations sur le DataFrame des nomenclatures"""
    print(f"\nDimension du DataFrame des nomenclatures: {nomenclatures_instance.df.shape}")
    print("Schema du DataFrame des nomenclatures:")
    print(nomenclatures_instance.df.schema)
    
    print("\nNombre d'articles parents avec nomenclature:", 
          len(nomenclatures_instance.nomenclature_dictionnary))
    
    # Affiche un exemple de nomenclature
    parent_code = next(iter(nomenclatures_instance.nomenclature_dictionnary))
    print(f"\nExemple de nomenclature pour l'article {parent_code}:")
    print(nomenclatures_instance.get_item_nomenclature(parent_code))