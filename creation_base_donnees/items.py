from .load_file import get_execution_time, read_excel
import polars as pl



class Items():
    
    _MANUFACTURER_COLUMN_NAMES = ["code_article", "nom_fabricant", "reference_article_fabricant"]
    @get_execution_time
    def __init__(self, folder_path: str, file_name: str, sheet_names: list[str]):
        """
        Initialisation de la classe Items.

        Effectue les opérations suivantes :
        - Lit les feuilles du fichier Excel dans des DataFrames Polars
        - Identifie les articles OC et OL
        - Crée la table des fabricants
        - Crée le dictionnaire des articles et de leurs fabricants
        - Supprime les colonnes fabricants
        - Supprime les doublons
        - Fusionne les DataFrames
        - Supprime les colonnes dupliquées
        - Renomme des colonnes spécifiques
        """
        self.dfs = []
        for sheet_name in sheet_names:
            df = read_excel(folder_path, file_name, sheet_name)
            print("Colonnes disponibles:", df.columns)  # Debug
            self.dfs.append(df)
        self.items_df = self.dfs[0]
        self._create_manufacturer_table()
        self._remove_manufacturer_columns()
        self._remove_duplicate_rows()
        self._merge_dataframes()
        self._remove_duplicate_columns()
        self._rename_specific_columns()
        self._oc_ol_identifier()


    def _create_manufacturer_table(self):
        """
        Crée une table des fabricants à partir des colonnes nom_fabricant et reference_article_fabricant
        """
        cols = ["code_article", "nom_fabricant", "reference_article_fabricant"]
        self.manufacturer_df = self.items_df.select(cols)


    def _remove_manufacturer_columns(self):
        """
        Supprime les colonnes nom_fabricant et reference_article_fabricant
        """
        self.items_df = self.items_df.drop(["nom_fabricant", "reference_article_fabricant"])


    def _remove_duplicate_columns(self):
        """
        Supprime les colonnes dupliquées provenant de la jointure.

        La jointure avec la table des fabricants crée des colonnes dupliquées
        (par exemple, "nom_fabricant_right" et "nom_fabricant_left"). Cette
        méthode supprime ces colonnes dupliquées.
        """
        self.items_df = self.items_df.drop(pl.col("^.*_right$"))


    def _remove_duplicate_rows(self):
        self.items_df = self.items_df.unique()
        self.dfs[1] = self.dfs[1].unique()
        self.manufacturer_df = self.manufacturer_df.unique()


    def _merge_dataframes(self):
        """
        Merge the dataframe containing the items dimensions with the main dataframe.

        This method merge the dataframe containing the items dimensions with the main dataframe
        on the "code_article" column. After the merge, the dataframe containing the items dimensions
        is deleted.

        """
        self.items_df = self.items_df.join(self.dfs[1], how="left", on="code_article") # dataframe with the dimensions of the items


    def _to_excel(self, file_name_excel):
        """
        Export the main dataframe to an Excel file.

        This method takes a file name and path as argument and export the
        main dataframe to an Excel file at this location.

        Parameters
        ----------
        file_name_excel : str
            The file name and path of the Excel file to be created.
        """
        self.items_df.write_excel(file_name_excel)

    def _rename_specific_columns(self):
        dict_columns_name = {"proprietaire_article_champs_calcule": "proprietaire_article", 
                             "pump_champs_calcule": "pump"}
        self.items_df = self.items_df.rename(dict_columns_name)


    def _oc_ol_identifier(self):
        """
        Identifie les articles OC et OL
        """
        self.items_df = (
            self.items_df
            .with_columns(
                pl.col("feuille_du_catalogue")
                .map_elements(
                    lambda x: True if x == "EMI.AM.OC" else False, return_dtype=pl.Boolean
                    )
                .alias("is_oc"),
                pl.col("feuille_du_catalogue")
                .map_elements(
                    lambda x: True if x == "EMI.AM.OL" else False, return_dtype=pl.Boolean
                    )
                .alias("is_ol")
                )
            )


    def _making_dictionnary(self):
        self.items_manufacturer_dictionnary = {}
        for row in self.manufacturer_df.iter_rows(named=True):
            if row["code_article"] not in self.items_manufacturer_dictionnary:
                self.items_manufacturer_dictionnary[row["code_article"]] = [{"nom_fabricant": row["nom_fabricant"], 
                                                                            "reference_article_fabricant": row["reference_article_fabricant"]}]
            else:
                self.items_manufacturer_dictionnary[row["code_article"]].append({"nom_fabricant": row["nom_fabricant"], 
                                                                                 "reference_article_fabricant": row["reference_article_fabricant"]})
        self.items_dictionnary = {row["code_article"]: row for row in self.items_df.iter_rows(named=True)}
        for item in self.items_dictionnary:
            if item in self.items_manufacturer_dictionnary:
                self.items_dictionnary[item]["fabricants"] = self.items_manufacturer_dictionnary[item]


class Nomenclatures():
    
    def __init__(self, folder_path, file_name, sheet_name):
        self.df = read_excel(folder_path, file_name, sheet_name)
        self.nomenclature_dictionnary =  self._making_nomenclature_dictionnary()


    def _get_list_items_with_nomenclature(self, df: pl.DataFrame) -> list[str]:
        """
        From the dataframe df, identify the items with a nomenclature:
        an item with at least one child item
        """
        list_items_with_nomenclature = (
            
            df.filter(
            (pl.col("art_et_art_fils_eqpt_quantite").is_not_null()) 
            & (pl.col("article") != pl.col("article_eqpt_article_fils"))
            & (pl.col("art_et_art_fils_eqpt_quantite") > 0)
                )
                .group_by("article")
                .agg(
                    pl.col("article_eqpt_article_fils").count()
                    )
                    .select(pl.col("article"))
                    .to_series()
                    .to_list()
                    )
        
        return sorted(list_items_with_nomenclature)


    def _making_nomenclature_dictionnary(self) -> dict:
        """
        Making a dictionnary with as key the 'father' article and in value
        a list of dictionnary with in key the 'son' article and in value
        the quantity.
        """
        nomenclature_dictionnary = {}
        list_items_with_nomenclature = self._get_list_items_with_nomenclature(self.df)
        for item in list_items_with_nomenclature:
            nomenclature_dictionnary[item] = []
            df_item = (
                self.df.filter(
                    (pl.col("article") == item) 
                    & ((pl.col("art_et_art_fils_eqpt_quantite").is_not_null()) 
                       & (pl.col("art_et_art_fils_eqpt_quantite") > 0)))
                       .iter_rows(named=True)
                       )
            for row in df_item:
                nomenclature_dictionnary[item].append({"code_article": row["article_eqpt_article_fils"], "quantite": row["art_et_art_fils_eqpt_quantite"]})

        return nomenclature_dictionnary


    def get_item_nomenclature(self, item_code: str, item_parent: str=None, multiplying_factor: int=1, counter: int=None) -> dict:
        """
        return a dictionnary representing the hierarchy or nomenclature of the item
        
        """
        if counter is None:
            counter = 0
        counter += 1
        if counter > 10:
            return {}
        nomenclature = {}
        nomenclature["code_article"] = item_code
        if item_parent is not None:
            for row in self.nomenclature_dictionnary[item_parent]:
                if row["code_article"] == item_code:
                    nomenclature["quantite"] = row["quantite"] * multiplying_factor
        else:
            nomenclature["quantite"] = 1 * multiplying_factor
        if item_code in self.nomenclature_dictionnary:
            nomenclature["article_fils"] = []
            for code_article_fils in self.nomenclature_dictionnary[item_code]:
                nomenclature["article_fils"].append(self.get_item_nomenclature(code_article_fils["code_article"], item_code, nomenclature["quantite"], counter))
        return nomenclature
