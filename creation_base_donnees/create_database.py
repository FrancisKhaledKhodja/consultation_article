import logging
import os
import sys
import io

sys.path.append(os.getcwd())

import re
from pathlib import Path
from PIL import Image as PILImage
from sqlmodel import SQLModel, Session, create_engine
from creation_base_donnees.models import Article, ArticleManufacturer, Nomenclature, Image
from creation_base_donnees.items import Items, Nomenclatures
import polars as pl
from creation_base_donnees.constants import folder_photo, folder_sqlite


# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def resize_image(image_bytes, max_size=(700, 700)):
    """Redimensionne une image tout en conservant son ratio d'aspect.
    
    Args:
        image_bytes (bytes): L'image en format bytes
        max_size (tuple): La taille maximale (largeur, hauteur)
    
    Returns:
        bytes: L'image redimensionnée en format bytes
    """
    # Ouvre l'image depuis les bytes
    img = PILImage.open(io.BytesIO(image_bytes))
    
    # Convertit en RGB si nécessaire (pour les images PNG avec transparence)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Calcule les nouvelles dimensions en conservant le ratio
    ratio = min(max_size[0] / img.width, max_size[1] / img.height)
    if ratio < 1:  # Seulement si l'image est plus grande que max_size
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, PILImage.Resampling.LANCZOS)
    
    # Convertit l'image redimensionnée en bytes
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)
    return output.getvalue()


def create_database():
    """Crée la base de données et les tables"""
    # Obtient le chemin absolu du projet
    project_root = Path(__file__).parent.parent.absolute()
    print(project_root)
    logger.info(f"Racine du projet : {project_root}")
    
    # Chemin absolu de la base de données
    db_path = project_root / folder_sqlite / "articles.db"
    logger.info(f"Création de la base de données à : {db_path}")
    
    # Crée le répertoire s'il n'existe pas
    db_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Dossier créé : {db_path.parent}")
    
    # Crée l'URL de connexion
    database_url = f"sqlite:///{db_path}"
    logger.info(f"URL de connexion : {database_url}")
    
    # Crée le moteur de base de données
    engine = create_engine(
        database_url,
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    # Crée les tables
    logger.info("Création des tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Tables créées avec succès")
    
    return engine


def import_data(engine):
    """Importe les données depuis le fichier Excel"""
    # Obtient le chemin absolu du projet
    project_root = Path(__file__).parent.parent.absolute()
    
    # Configure les chemins et charge les données
    data_path = project_root / "data_input"
    logger.info(f"Chargement des données depuis : {data_path}")
    
    file_name = "521 - (PIM) - REFERENTIEL ARTICLES.xlsx"
    logger.info(f"Fichier Excel : {file_name}")
    
    items = Items(str(data_path), file_name, ["ARTICLES PIM", "ARTICLES PIM - TRANSPORT"])
    
    with Session(engine) as session:
        # Import des articles
        logger.info("Import des articles...")
        
        # Vérifie les doublons dans le DataFrame
        duplicate_codes = items.items_df.filter(pl.col("code_article").is_duplicated())
        if len(duplicate_codes) > 0:
            logger.warning(f"Codes articles en doublon trouvés :")
            for row in duplicate_codes.iter_rows(named=True):
                logger.warning(f"Code article en doublon : {row['code_article']}")
        
        # Utilise unique() pour ne garder que les premières occurrences
        items.items_df = items.items_df.unique(subset=["code_article"], keep="first")
        
        articles = {}  # Dictionnaire pour stocker les articles par code
        seen_codes = set()  # Ensemble pour suivre les codes articles déjà vus
        for row in items.items_df.iter_rows(named=True):
            code_article = row["code_article"]
            if code_article in seen_codes:
                logger.warning(f"Code article en doublon ignoré : {code_article}")
                continue
            seen_codes.add(code_article)
            
            article = Article(
                code_article=row["code_article"],
                proprietaire_article=row["proprietaire_article"],
                type_article=row["type_article"],
                libelle_court_article=row["libelle_court_article"],
                libelle_long_article=row["libelle_long_article"],
                description_famille_d_achat=row["description_famille_d_achat"],
                commentaire_technique=row["commentaire_technique"],
                commentaire_logistique=row.get("commentaire_logistique"),
                statut_abrege_article=row["statut_abrege_article"],
                cycle_de_vie_achat=row["cycle_de_vie_achat"],
                cycle_de_vie_de_production_pim=row["cycle_de_vie_de_production_pim"],
                feuille_du_catalogue=row["feuille_du_catalogue"],
                description_de_la_feuille_du_catalogue=row["description_de_la_feuille_du_catalogue"],
                famille_d_achat_feuille_du_catalogue=row["famille_d_achat_feuille_du_catalogue"],
                catalogue_consommable=row["catalogue_consommable"],
                criticite_pim=row["criticite_pim"],
                famille_immobilisation=row.get("famille_immobilisation"),
                categorie_immobilisation=row.get("categorie_immobilisation"),
                categorie_inv_accounting=row["categorie_inv_accounting"],
                suivi_par_num_serie_oui_non=row["suivi_par_num_serie_oui_non"] == "OUI",
                stocksecu_inv_oui_non=row["stocksecu_inv_oui_non"] == "OUI",
                article_hors_normes=row["article_hors_normes"] == "OUI",
                peremption=row["peremption"] == "OUI",
                retour_production=row["retour_production"] == "OUI",
                is_oc=row["is_oc"],
                is_ol=row["is_ol"],
                a_retrofiter=row.get("a_retrofiter") == "OUI",
                # Champs logistiques
                affretement=row.get("affretement") == "OUI",
                fragile=row.get("fragile") == "OUI",
                poids_article=float(row["poids_article"]) if row.get("poids_article") else None,
                volume_article=float(row["volume_article"]) if row.get("volume_article") else None,
                hauteur_article=float(row["hauteur_article"]) if row.get("hauteur_article") else None,
                longueur_article=float(row["longueur_article"]) if row.get("longueur_article") else None,
                largeur_article=float(row["largeur_article"]) if row.get("largeur_article") else None,
                matiere_dangereuse=row.get("matiere_dangereuse") == "OUI",
                md_code_onu=row.get("md_code_onu"),
                md_groupe_emballage=row.get("md_groupe_emballage"),
                md_type_colis=row.get("md_type_colis"),
                prix_achat_prev=float(row["prix_achat_prev"]) if row["prix_achat_prev"] else None,
                pump=float(row["pump"]) if row["pump"] else None,
                prix_eur_catalogue_article=float(row["prix_EUR_catalogue_article"]) if row["prix_EUR_catalogue_article"] else None,
                compte_cg_achat=row.get("compte_cg_achat"),
                delai_approvisionnement=int(float(row["delai_approvisionnement"])) if row.get("delai_approvisionnement") else None,
                delai_de_reparation_contractuel=int(float(row["delai_de_reparation_contractuel"])) if row.get("delai_de_reparation_contractuel") else None,
                point_de_commande=int(row["point_de_commande"]) if row.get("point_de_commande") else None,
                quantite_a_commander=int(row["quantite_a_commander"]) if row.get("quantite_a_commander") else None,
                qte_cde_minimum_point_de_reappro=int(row["qte_cde_minimum_point_de_reappro"]) if row.get("qte_cde_minimum_point_de_reappro") else None,
                qte_minimum_ordre_de_commande=int(row["qte_minimum_ordre_de_commande"]) if row.get("qte_minimum_ordre_de_commande") else None,
                qte_maximum_ordre_de_commande=int(row["qte_maximum_ordre_de_commande"]) if row.get("qte_maximum_ordre_de_commande") else None,
                qte_min_de_l_article=int(row["qte_min_de_l_article"]) if row.get("qte_min_de_l_article") else None,
                qte_max_de_l_article=int(row["qte_max_de_l_article"]) if row.get("qte_max_de_l_article") else None,
                qte_cde_maximum_quantite_d_ordre_de_commande=int(row["qte_cde_maximum_quantite_d_ordre_de_commande"]) if row.get("qte_cde_maximum_quantite_d_ordre_de_commande") else None,
                lieu_de_reparation_pim=row["lieu_de_reparation_pim"],
                description_lieu_de_reparation=row["description_lieu_de_reparation"],
                rma=row["rma"],
                role_responsable_et_equipement=row["role_responsable_et_equipement"],
                mnemonique=row["mnemonique"],
                date_creation_article=row.get("date_creation_article"),
                nom_createur_article=row.get("nom_createur_article"),
                date_derniere_modif_article=row.get("date_derniere_modif_article"),
                auteur_derniere_modif_article=row.get("auteur_derniere_modif_article")
            )
            session.add(article)
            articles[row["code_article"]] = article
        
        # Commit pour obtenir les IDs des articles
        session.commit()
        logger.info(f"{len(articles)} articles importés")
        
        # Import des fabricants
        logger.info("Import des fabricants...")
        manufacturers_dict = {}  # Dictionnaire pour stocker les références fabricant par code article
        for row in items.manufacturer_df.iter_rows(named=True):
            if row["nom_fabricant"] and row["code_article"]:  # Ne crée que les associations avec un nom et code article non nuls
                article_manufacturer = ArticleManufacturer(
                    code_article=row["code_article"],
                    nom_fabricant=row["nom_fabricant"],
                    reference_article_fabricant=row["reference_article_fabricant"]
                )
                session.add(article_manufacturer)
                if row["code_article"] not in manufacturers_dict:
                    manufacturers_dict[row["code_article"]] = []
                manufacturers_dict[row["code_article"]].append(article_manufacturer)
        
        # Commit pour sauvegarder les associations article-fabricant
        session.commit()
        logger.info(f"{len(manufacturers_dict)} articles avec fabricants importés")
        
        # Import des nomenclatures
        logger.info("Import des nomenclatures...")
        nomenclatures = Nomenclatures(str(data_path), "531 - Nomenclature Equipement.xlsx", "Nomenclature Fils")
        nomenclatures_count = 0
        
        for row in nomenclatures.df.filter(
            (pl.col("art_et_art_fils_eqpt_quantite").is_not_null()) 
            & (pl.col("article") != pl.col("article_eqpt_article_fils"))
            & (pl.col("art_et_art_fils_eqpt_quantite") > 0)
        ).iter_rows(named=True):
            nomenclature = Nomenclature(
                code_article_parent=row["article"],
                code_article_fils=row["article_eqpt_article_fils"],
                quantite=float(row["art_et_art_fils_eqpt_quantite"])
            )
            session.add(nomenclature)
            nomenclatures_count += 1
        
        session.commit()
        logger.info(f"{nomenclatures_count} nomenclatures créées")

        # import des photos
        logger.info("Import des images...")
        photo_count = 0
        extensions_photo = {"jpeg", "jpg", "png"}
        pattern_code_art = r"[A-Z]{3}\d{4}\d{2}"

        liste_files = os.listdir(folder_photo)
        liste_photos = [file for file in liste_files if os.path.isfile(os.path.join(folder_photo, file)) and file.lower().split(".")[1] in extensions_photo]

        for photo in liste_photos:
            with open(os.path.join(folder_photo, photo), "rb") as f:
                response = re.search(pattern_code_art, photo)
                if response:
                    code_article = photo[response.start():response.end()]
                    image_bytes = f.read()
            if response:
                image = Image(code_article=code_article, image=resize_image(image_bytes))
                session.add(image)
                photo_count += 1
        session.commit()
        logger.info(f"{photo_count} images importées")


def main():
    """Point d'entrée principal"""
    try:
        # Crée la base de données
        engine = create_database()
        
        # Importe les données
        import_data(engine)
        
        logger.info("Base de données créée et données importées avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de la base de données : {str(e)}")
        raise
    finally:
        # Ferme toutes les connexions
        if 'engine' in locals():
            engine.dispose()


if __name__ == "__main__":
    main()
