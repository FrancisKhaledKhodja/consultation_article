from backend.api import get_session
from sqlmodel import select
from creation_base_donnees.models import Article, Nomenclature
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def get_all_parents(session, code_article, depth=0, max_depth=10):
    """Récupère récursivement tous les parents d'un article"""
    if depth >= max_depth:
        return []
        
    parents = []
    # Trouver les parents directs
    parent_relations = session.exec(
        select(Nomenclature, Article)
        .join(Article, Article.code_article == Nomenclature.code_article_parent)
        .where(Nomenclature.code_article_fils == code_article)
    ).all()
    
    for nomenclature, parent in parent_relations:
        parent_info = {
            'code': parent.code_article,
            'libelle': parent.libelle_court_article,
            'quantite': nomenclature.quantite,
            'niveau': depth
        }
        parents.append(parent_info)
        # Récursivement trouver les parents des parents
        grandparents = get_all_parents(session, parent.code_article, depth + 1, max_depth)
        parents.extend(grandparents)
        
    return parents

def test_hierarchy():
    test_codes = ["TDF156522", "TDF157807", "TDF160417"]
    
    with get_session() as session:
        for code in test_codes:
            logger.info(f"\nTest de la hiérarchie pour {code}:")
            article = session.exec(select(Article).where(Article.code_article == code)).first()
            if article:
                logger.info(f"Article: {article.code_article} - {article.libelle_court_article}")
                
                # Trouver tous les parents
                parents = get_all_parents(session, code)
                if parents:
                    logger.info("Parents trouvés :")
                    for p in parents:
                        indent = "  " * p['niveau']
                        logger.info(f"{indent}└─ {p['code']} - {p['libelle']} (qté: {p['quantite']})")
                else:
                    logger.info("Aucun parent trouvé")
            else:
                logger.error(f"Article {code} non trouvé!")

if __name__ == "__main__":
    test_hierarchy()
