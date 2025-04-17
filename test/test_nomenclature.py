from backend.api import get_session
from sqlmodel import select
from creation_base_donnees.models import Article, Nomenclature
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_nomenclature():
    test_code = "TDF160417"
    
    with get_session() as session:
        # 1. Vérifier l'article
        article = session.exec(
            select(Article).where(Article.code_article == test_code)
        ).first()
        
        if article:
            logger.info(f"\nArticle trouvé:")
            logger.info(f"Code: {article.code_article}")
            logger.info(f"Libellé: {article.libelle_court_article}")
            logger.info(f"Type: {article.type_article}")
        else:
            logger.error(f"Article {test_code} non trouvé!")
            return
            
        # 2. Vérifier toutes les nomenclatures où cet article est parent
        logger.info("\nRecherche des articles fils:")
        nomenclatures_parent = session.exec(
            select(Nomenclature).where(Nomenclature.code_article_parent == test_code)
        ).all()
        
        if nomenclatures_parent:
            logger.info(f"Nombre d'articles fils: {len(nomenclatures_parent)}")
            for n in nomenclatures_parent:
                fils = session.exec(
                    select(Article).where(Article.code_article == n.code_article_fils)
                ).first()
                if fils:
                    logger.info(f"- {fils.code_article} ({fils.libelle_court_article}) - Quantité: {n.quantite}")
                else:
                    logger.warning(f"- Article fils {n.code_article_fils} non trouvé dans la base!")
        else:
            logger.warning("Aucun article fils trouvé")
            
        # 3. Vérifier toutes les nomenclatures où cet article est fils
        logger.info("\nRecherche des articles parents:")
        nomenclatures_fils = session.exec(
            select(Nomenclature).where(Nomenclature.code_article_fils == test_code)
        ).all()
        
        if nomenclatures_fils:
            logger.info(f"Nombre d'articles parents: {len(nomenclatures_fils)}")
            for n in nomenclatures_fils:
                parent = session.exec(
                    select(Article).where(Article.code_article == n.code_article_parent)
                ).first()
                if parent:
                    logger.info(f"- {parent.code_article} ({parent.libelle_court_article}) - Quantité: {n.quantite}")
                else:
                    logger.warning(f"- Article parent {n.code_article_parent} non trouvé dans la base!")
        else:
            logger.warning("Aucun article parent trouvé")

if __name__ == "__main__":
    test_nomenclature()
