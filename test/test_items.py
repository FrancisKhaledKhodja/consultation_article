import os
import sys

sys.path.append(os.getcwd())

import pytest
import polars as pl
from creation_base_donnees.items import Items
from creation_base_donnees.constants import folder_path_input, file_name_521, sheet_names_521



@pytest.fixture
def items_instance():
    """Fixture pour créer une instance de Items pour les tests"""
    return Items(folder_path_input, file_name_521, sheet_names_521)


def test_items_initialization(items_instance):
    """Test l'initialisation de la classe Items"""
    assert isinstance(items_instance.items_df, pl.DataFrame)
    assert isinstance(items_instance.manufacturer_df, pl.DataFrame)
    assert len(items_instance.dfs) == len(sheet_names_521)


def test_manufacturer_table(items_instance):
    """Test la création de la table des fabricants"""
    required_columns = ["code_article", "nom_fabricant", "reference_article_fabricant"]
    for col in required_columns:
        assert col in items_instance.manufacturer_df.columns
    assert items_instance.manufacturer_df.shape[0] > 0


def test_oc_ol_identifier(items_instance):
    """Test l'identification des articles OC et OL"""
    assert "is_oc" in items_instance.items_df.columns
    assert "is_ol" in items_instance.items_df.columns
    assert items_instance.items_df["is_oc"].dtype == pl.Boolean
    assert items_instance.items_df["is_ol"].dtype == pl.Boolean


def test_items_columns(items_instance):
    """Test la présence des colonnes essentielles dans le DataFrame des articles"""
    required_columns = [
        "code_article",
        "proprietaire_article",
        "type_article",
        "libelle_court_article",
        "feuille_du_catalogue",
        "is_oc",
        "is_ol"
    ]
    for col in required_columns:
        assert col in items_instance.items_df.columns


def test_no_duplicate_rows(items_instance):
    """Test qu'il n'y a pas de doublons dans les DataFrames"""
    # Test sur le DataFrame principal
    original_count = items_instance.items_df.shape[0]
    unique_count = items_instance.items_df.unique().shape[0]
    assert original_count == unique_count, "Il y a des doublons dans items_df"

    # Test sur le DataFrame des fabricants
    original_manu_count = items_instance.manufacturer_df.shape[0]
    unique_manu_count = items_instance.manufacturer_df.unique().shape[0]
    assert original_manu_count == unique_manu_count, "Il y a des doublons dans manufacturer_df"


def test_dataframes_info(items_instance):
    """Test et affiche les informations sur les DataFrames"""
    # Test sur le DataFrame principal
    assert items_instance.items_df.shape[0] > 0, "Le DataFrame items_df est vide"
    print(f"\nDimension de la table items_df: {items_instance.items_df.shape}")
    print("Schema de la table items_df:")
    print(items_instance.items_df.schema)

    # Test sur le DataFrame des fabricants
    assert items_instance.manufacturer_df.shape[0] > 0, "Le DataFrame manufacturer_df est vide"
    print(f"\nDimension de la table manufacturer_df: {items_instance.manufacturer_df.shape}")
    print("Schema de la table manufacturer_df:")
    print(items_instance.manufacturer_df.schema)