import os
import sys

sys.path.append(os.getcwd())

import pytest
import polars as pl
from creation_base_donnees.load_file import read_excel
from creation_base_donnees.constants import folder_path_input, file_name_521, sheet_names_521


@pytest.mark.parametrize("sheet_name", sheet_names_521)
def test_read_excel_521(sheet_name):
    """Test la lecture du fichier 521 pour chaque feuille"""
    df = read_excel(folder_path_input, file_name_521, sheet_name)
    assert isinstance(df, pl.DataFrame)
    assert df.shape[0] > 0 and df.shape[1] > 0
    print(f"\nTest de la feuille: {sheet_name}")
    print(f"Dimension du Dataframe: {df.shape}")
    print("Schema du Dataframe:")
    print(df.schema)
