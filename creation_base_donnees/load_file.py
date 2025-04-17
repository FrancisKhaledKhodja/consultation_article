import os
import unidecode
import polars as pl
from time import perf_counter
from string import punctuation
import re



def get_execution_time(func):
    '''
    Calculate the execution time of a function
    '''
    def wrapper(*args, **kargs):        
        t0 = perf_counter()
        result = func(*args, **kargs)
        t1 = perf_counter()
        print("Temps d'execution: {} secondes".format(str(round(t1 - t0, 0))))
        return result
    return wrapper


def transform_string(label: str) -> str:
    '''
    Transform the string in lowercase, remove the punctuation 
    and replace the spaces by an underscore 
    '''
    label = str(label)
    label = label.lower()
    label = label.strip()
    label = unidecode.unidecode(label)
    
    # Remplacer d'abord les caractères spéciaux avec des espaces
    for punc in punctuation:
        if punc == "+":
            label = label.replace(punc, " et ")
        elif punc == "<":
            label = label.replace(punc, " inf ")
        elif punc == ">":
            label = label.replace(punc, " sup ")
        elif punc != "_":
            label = label.replace(punc, " ")

    # Nettoyer les espaces et les underscores
    label = re.sub(r"\s+", "_", label)  # Remplacer les espaces multiples par un underscore
    label = re.sub(r"_+", "_", label)   # Remplacer les underscores multiples par un seul
    label = label.strip("_")            # Supprimer les underscores au début et à la fin

    # Remplacer "ndeg" par "n" s'il est présent
    if "ndeg" in label:
        label = label.replace("ndeg", "n")

    return label


def transform_columns_name(dataframe: pl.DataFrame) -> pl.DataFrame:
    '''
    Transform the header of the dataframe with transform_string function 
    '''
    name_columns = [transform_string(label) for label in dataframe.columns]
    dataframe.columns = name_columns

    return dataframe


def read_excel(folder_path: str, file_name: str, sheet_name: str=None) -> pl.DataFrame:
    '''
    Lit un fichier Excel dans un DataFrame Polars.

    Args:
        folder_path (str): Chemin du dossier contenant le fichier Excel
        file_name (str): Nom du fichier Excel
        sheet_name (str, optional): Nom de la feuille à lire. Si None, lit la première feuille.

    Returns:
        pl.DataFrame: DataFrame contenant les données de la feuille Excel
    '''
    if not (file_name.endswith(".xlsx") or file_name.endswith(".xls")):
        raise Exception("Ce fichier n'est pas un fichier Excel")
    
    file_path = os.path.join(folder_path, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")
    
    try:
        if sheet_name:
            df = pl.read_excel(file_path, sheet_name=sheet_name)
        else:
            df = pl.read_excel(file_path)
    except Exception as e:
        raise Exception(f"Erreur lors de la lecture du fichier Excel: {str(e)}")

    df = transform_columns_name(df)

    return df
