import os
import sys
from pathlib import Path
from creation_base_donnees.models import Article, ArticleManufacturer, Nomenclature, Image
from sqlmodel import Session, select, create_engine
from sqlmodel import or_
from sqlmodel import func
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

def get_executable_dir():
    """Retourne le répertoire de l'exécutable"""
    if getattr(sys, 'frozen', False):
        # Si on est dans un exécutable PyInstaller
        return os.path.dirname(sys.executable)
    else:
        # Si on est en développement
        return os.path.dirname(os.path.dirname(__file__))

def get_database_url(db_path=None):
    """
    Retourne l'URL de la base de données
    Si db_path n'est pas spécifié, utilise le chemin par défaut
    """
    try:
        logger.info("Récupération du chemin de la base de données")
        
        # Utiliser le chemin fourni ou lire depuis le fichier settings
        if db_path is None:
            executable_dir = get_executable_dir()
            settings_file = os.path.join(executable_dir, 'database_settings.txt')
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    db_path = f.readline().strip()
                logger.info(f"Chemin de la base de données lu depuis settings: {db_path}")
            else:
                db_path = os.path.join(executable_dir, 'articles.db')
                logger.info(f"Fichier settings non trouvé, utilisation du chemin par défaut: {db_path}")
        
        # Convertir en chemin absolu si ce n'est pas déjà le cas
        db_path = os.path.abspath(db_path)
        logger.info(f"Chemin final de la base de données: {db_path}")
        
        if not os.path.exists(db_path):
            logger.error(f"Base de données non trouvée à {db_path}")
            raise FileNotFoundError(f"Base de données non trouvée à {db_path}")
        
        # Construire et retourner l'URL SQLAlchemy
        url = f"sqlite:///{db_path}"
        logger.info(f"URL de la base de données: {url}")
        return url
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du chemin de la base de données: {str(e)}", exc_info=True)
        raise

# Variable globale pour stocker l'URL de la base de données
DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)

def set_database_path(db_path):
    """
    Permet de changer le chemin de la base de données
    """
    global DATABASE_URL, engine
    DATABASE_URL = get_database_url(db_path)
    engine = create_engine(DATABASE_URL)

def get_session():
    """
    Crée et retourne une nouvelle session de base de données
    """
    return Session(engine)

# Fonction pour récupérer tous les articles
def get_all_articles():
    """
    Récupère tous les articles de la base de données.
    
    Returns:
        List[Article]: Liste de tous les articles
    """
    with get_session() as session:
        return session.exec(select(Article)).all()

# Fonction pour récupérer tous les fabricants
def get_all_manufacturers():
    """
    Récupère tous les fabricants de la base de données.
    
    Returns:
        List[ArticleManufacturer]: Liste de tous les fabricants
    """
    with get_session() as session:
        return session.exec(select(ArticleManufacturer)).all()

# Fonction pour récupérer toutes les nomenclatures
def get_all_nomenclatures():
    """
    Récupère toutes les nomenclatures de la base de données.
    
    Returns:
        List[Nomenclature]: Liste de toutes les nomenclatures
    """
    with get_session() as session:
        return session.exec(select(Nomenclature)).all()

# Fonction pour récupérer tous les articles avec leurs fabricants
def get_all_articles_with_manufacturers():
    """
    Récupère tous les articles avec leurs fabricants associés.
    
    Returns:
        List[Article]: Liste de tous les articles avec leurs fabricants
    """
    with get_session() as session:
        articles = session.exec(select(Article)).all()
        # Charger explicitement la relation fabricants
        for article in articles:
            _ = article.fabricants
        return articles

# Fonction pour récupérer tous les articles avec leurs nomenclatures
def get_all_articles_with_nomenclatures():
    """
    Récupère tous les articles avec leurs nomenclatures associées.
    
    Returns:
        List[Article]: Liste de tous les articles avec leurs nomenclatures
    """
    with get_session() as session:
        # Sélectionner les articles qui sont des parents dans la nomenclature
        stmt = select(Article).join(Nomenclature, Article.code_article == Nomenclature.code_article_parent)
        return session.exec(stmt).all()

# Fonction pour récupérer tous les articles avec leurs fabricants et nomenclatures
def get_all_articles_with_manufacturers_and_nomenclatures():
    """
    Récupère tous les articles avec leurs fabricants et nomenclatures associés.
    
    Returns:
        List[Article]: Liste de tous les articles avec leurs fabricants et nomenclatures
    """
    with get_session() as session:
        articles = session.exec(select(Article)).all()
        # Charger explicitement les relations
        for article in articles:
            _ = article.fabricants
        return articles

# Fonction pour récupérer tous les fabricants avec leurs articles
def get_all_manufacturers_with_articles():
    """
    Récupère tous les fabricants avec leurs articles associés.
    
    Returns:
        List[ArticleManufacturer]: Liste de tous les fabricants avec leurs articles
    """
    with get_session() as session:
        manufacturers = session.exec(select(ArticleManufacturer)).all()
        # Charger explicitement la relation article
        for manufacturer in manufacturers:
            _ = manufacturer.article
        return manufacturers

# Fonction pour récupérer toutes les nomenclatures avec leurs articles
def get_all_nomenclatures_with_articles():
    """
    Récupère toutes les nomenclatures avec leurs articles associés.
    
    Returns:
        List[Nomenclature]: Liste de toutes les nomenclatures avec leurs articles
    """
    with get_session() as session:
        return session.exec(select(Nomenclature)).all()

def get_article_by_code(code_article):
    """
    Récupère un article spécifique à partir de son code article.
    
    Args:
        code_article: Le code de l'article à rechercher
        
    Returns:
        Article: L'article correspondant au code ou None si non trouvé
    """
    try:
        logger.info(f"Recherche de l'article avec le code: {code_article}")
        with get_session() as session:
            query = select(Article).where(Article.code_article == code_article)
            logger.debug(f"Requête SQL: {query}")
            
            article = session.exec(query).first()
            if article:
                logger.info(f"Article trouvé: {article.code_article}")
                return article
            else:
                logger.warning(f"Aucun article trouvé pour le code: {code_article}")
                return None
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de l'article {code_article}: {str(e)}", exc_info=True)
        raise

def get_manufacturer_by_code(code_article):
    """
    Récupère un fabricant spécifique à partir du code article.
    
    Args:
        code_article: Le code de l'article associé au fabricant
        
    Returns:
        ArticleManufacturer: Le fabricant correspondant au code article ou None si non trouvé
    """
    with get_session() as session:
        return session.exec(select(ArticleManufacturer).where(ArticleManufacturer.code_article == code_article)).first()

def get_nomenclature_by_code(code_article):
    """
    Récupère une nomenclature spécifique à partir du code article.
    
    Args:
        code_article: Le code de l'article parent dans la nomenclature
        
    Returns:
        Nomenclature: La nomenclature correspondante au code article ou None si non trouvée
    """
    with get_session() as session:
        return session.exec(select(Nomenclature).where(Nomenclature.code_article_parent == code_article)).first()

def get_manufacturer_by_article(code_article):
    """
    Récupère le fabricant associé à un article spécifique.
    
    Args:
        code_article: Le code de l'article dont on veut le fabricant
        
    Returns:
        ArticleManufacturer: Le fabricant de l'article ou None si non trouvé
    """
    with get_session() as session:
        return session.exec(select(ArticleManufacturer).where(ArticleManufacturer.code_article == code_article)).first()

def get_nomenclature_by_article(code_article):
    """
    Récupère la nomenclature associée à un article spécifique.
    
    Args:
        code_article: Le code de l'article dont on veut la nomenclature
        
    Returns:
        Nomenclature: La nomenclature de l'article ou None si non trouvée
    """
    with get_session() as session:
        return session.exec(select(Nomenclature).where(Nomenclature.code_article_parent == code_article)).first()

def get_manufacturers_by_article(code_article):
    """
    Récupère tous les fabricants associés à un article spécifique.
    
    Args:
        code_article: Le code de l'article dont on veut les fabricants
        
    Returns:
        List[ArticleManufacturer]: Liste des fabricants de l'article
    """
    with get_session() as session:
        return session.exec(select(ArticleManufacturer).where(ArticleManufacturer.code_article == code_article)).all()

def get_nomenclatures_by_article(code_article):
    """
    Récupère toutes les nomenclatures pour un article donné, avec les détails des articles fils.
    
    Args:
        code_article: Le code de l'article dont on veut les nomenclatures
        
    Returns:
        List[dict]: Liste des nomenclatures avec les détails des articles fils
    """
    with get_session() as session:
        # Récupérer les nomenclatures avec les articles fils associés
        results = session.exec(
            select(Nomenclature, Article)
            .where(Nomenclature.code_article_parent == code_article)
            .join(Article, Nomenclature.code_article_fils == Article.code_article)
        ).all()
        
        # Transformer les résultats en une liste d'objets Article avec la quantité
        nomenclatures = []
        for nomenclature, article in results:
            # Copier les attributs de l'article
            article_dict = {
                "code_article": article.code_article,
                "libelle_court_article": article.libelle_court_article,
                "type_article": article.type_article,
                "statut_abrege_article": article.statut_abrege_article,
                "quantite": nomenclature.quantite
            }
            nomenclatures.append(article_dict)
        
        return nomenclatures

def get_manufacturers_with_articles():
    """
    Récupère tous les fabricants avec leurs articles associés.
    
    Returns:
        List[ArticleManufacturer]: Liste des fabricants avec leurs articles
    """
    with get_session() as session:
        manufacturers = session.exec(select(ArticleManufacturer)).all()
        # Charger explicitement la relation article
        for manufacturer in manufacturers:
            _ = manufacturer.article
        return manufacturers

def get_nomenclatures_with_articles():
    """
    Récupère toutes les nomenclatures avec leurs articles associés.
    
    Returns:
        List[Nomenclature]: Liste des nomenclatures avec leurs articles
    """
    with get_session() as session:
        stmt = select(Nomenclature).join(Article, Nomenclature.code_article_parent == Article.code_article)
        return session.exec(stmt).all()

def search_articles(search_term):
    """
    Recherche des articles par mot-clé dans tous les attributs textuels.
    """
    with get_session() as session:
        # Convertir le terme de recherche en minuscules pour une recherche insensible à la casse
        search_pattern = f"%{search_term.lower()}%"
        
        # Rechercher dans tous les champs textuels pertinents
        return session.exec(
            select(Article).where(
                or_(
                    func.lower(Article.code_article).like(search_pattern),
                    func.lower(Article.libelle_court_article).like(search_pattern),
                    func.lower(Article.libelle_long_article).like(search_pattern),
                    func.lower(Article.proprietaire_article).like(search_pattern),
                    func.lower(Article.type_article).like(search_pattern)
                )
            )
        ).all()

def get_article_tree(code_article, level=0, max_depth=10):
    """
    Récupère l'arborescence complète d'un article avec ses nomenclatures.
    Retourne un dictionnaire avec la structure de l'arbre.
    """
    print(f"Recherche de l'arborescence pour l'article {code_article} (niveau {level})")
    
    if level >= max_depth:  # Éviter les boucles infinies
        print(f"Niveau maximum atteint pour {code_article}")
        return None
        
    with get_session() as session:
        # Récupérer l'article
        article = session.exec(select(Article).where(Article.code_article == code_article)).first()
        if not article:
            print(f"Article {code_article} non trouvé")
            return None
            
        print(f"Article trouvé : {article.code_article} - {article.libelle_court_article}")
            
        # Créer le nœud pour cet article
        node = {
            "article": article,
            "children": []
        }
        
        # Récupérer les nomenclatures (articles fils)
        nomenclatures = session.exec(
            select(Nomenclature).where(Nomenclature.code_article_parent == code_article)
        ).all()
        
        print(f"Nombre de nomenclatures pour {code_article}: {len(nomenclatures)}")
        
        # Récursivement obtenir l'arbre pour chaque article fils
        for nomenclature in nomenclatures:
            print(f"Traitement de la nomenclature : parent={code_article}, fils={nomenclature.code_article_fils}, quantité={nomenclature.quantite}")
            child_tree = get_article_tree(nomenclature.code_article_fils, level + 1, max_depth)
            if child_tree:
                node["children"].append({
                    "quantite": nomenclature.quantite,
                    "tree": child_tree
                })
                
        return node

def get_articles_with_nomenclature():
    """
    Récupère tous les articles qui ont des nomenclatures (articles parents).
    """
    print("Recherche des articles avec nomenclature...")
    with get_session() as session:
        # Sélectionner les articles qui sont des parents dans la table nomenclature
        parent_articles = session.exec(
            select(Article)
            .join(Nomenclature, Article.code_article == Nomenclature.code_article_parent)
            .distinct()
        ).all()
        print(f"Nombre d'articles avec nomenclature trouvés : {len(parent_articles)}")
        for article in parent_articles:
            print(f"Article parent trouvé : {article.code_article}")
        return parent_articles

def test_article_nomenclature(code_article):
    """
    Fonction de test pour afficher toutes les informations sur un article et ses nomenclatures.
    """
    with get_session() as session:
        # Vérifier si l'article existe
        article = session.exec(select(Article).where(Article.code_article == code_article)).first()
        if not article:
            print(f"Article {code_article} non trouvé dans la base")
            return
            
        print(f"\nInformations sur l'article {code_article}:")
        print(f"- Libellé court: {article.libelle_court_article}")
        print(f"- Type: {article.type_article}")
        print(f"- Propriétaire: {article.proprietaire_article}")
        
        # Vérifier les nomenclatures où cet article est parent
        print("\nNomenclatures où cet article est parent:")
        parent_noms = session.exec(
            select(Nomenclature).where(Nomenclature.code_article_parent == code_article)
        ).all()
        if parent_noms:
            for nom in parent_noms:
                fils = session.exec(select(Article).where(Article.code_article == nom.code_article_fils)).first()
                print(f"- Article fils: {nom.code_article_fils} (Quantité: {nom.quantite})")
                if fils:
                    print(f"  Libellé: {fils.libelle_court_article}")
        else:
            print("Aucune nomenclature trouvée où cet article est parent")
            
        # Vérifier les nomenclatures où cet article est fils
        print("\nNomenclatures où cet article est fils:")
        fils_noms = session.exec(
            select(Nomenclature).where(Nomenclature.code_article_fils == code_article)
        ).all()
        if fils_noms:
            for nom in fils_noms:
                parent = session.exec(select(Article).where(Article.code_article == nom.code_article_parent)).first()
                print(f"- Article parent: {nom.code_article_parent} (Quantité: {nom.quantite})")
                if parent:
                    print(f"  Libellé: {parent.libelle_court_article}")
        else:
            print("Aucune nomenclature trouvée où cet article est fils")

def print_article_tree(code_article, indent="", is_last=True, parent_indent=""):
    """
    Affiche l'arborescence d'un article dans un format texte avec indentation.
    """
    with get_session() as session:
        # Récupérer l'article
        article = session.exec(select(Article).where(Article.code_article == code_article)).first()
        if not article:
            return
            
        # Afficher l'article courant
        prefix = parent_indent + ("└----" if is_last else "├----")
        if indent == "":  # Article racine
            prefix = ""
            
        print(f"{prefix}{article.code_article} | {article.libelle_court_article} | {article.proprietaire_article} | {article.is_oc} | {article.type_article}")
        
        # Calculer l'indentation pour les enfants
        child_parent_indent = parent_indent + ("    " if is_last else "│   ")
        if indent == "":  # Article racine
            child_parent_indent = ""
            
        # Récupérer les nomenclatures (articles fils)
        nomenclatures = session.exec(
            select(Nomenclature).where(Nomenclature.code_article_parent == code_article)
        ).all()
        
        # Afficher récursivement les articles fils
        for i, nomenclature in enumerate(nomenclatures):
            is_last_child = (i == len(nomenclatures) - 1)
            print_article_tree(nomenclature.code_article_fils, indent + "  ", is_last_child, child_parent_indent)

def get_full_article_tree(code_article):
    """
    Retourne l'arborescence complète d'un article sous forme de chaîne de caractères.
    """
    import io
    from contextlib import redirect_stdout
    
    # Rediriger la sortie standard vers un buffer
    f = io.StringIO()
    with redirect_stdout(f):
        print_article_tree(code_article)
    
    # Récupérer le contenu du buffer
    return f.getvalue()

def get_images_by_article(code_article: str):
    """
    Récupère toutes les images associées à un article.
    
    Args:
        code_article: Le code de l'article dont on veut les images
        
    Returns:
        List[Image]: Liste des images de l'article
    """
    with get_session() as session:
        images = session.exec(
            select(Image).where(Image.code_article == code_article)
        ).all()
        return images
