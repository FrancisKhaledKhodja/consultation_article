import os
import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QSplitter, QMessageBox
from PyQt6.QtCore import Qt

# Ajout du chemin racine au PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from sqlmodel import select
from backend.api import *
from creation_base_donnees.models import Article, ArticleManufacturer, Nomenclature, Image
from frontend.utils.logging_config import logger, setup_logging
from frontend.utils.error_handlers import show_error_dialog
from frontend.views.search_panel import SearchPanel
from frontend.views.tree_panel import TreePanel
from frontend.views.parent_tree_panel import ParentTreePanel
from frontend.views.details_panel import DetailsPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_database()
        
        self.setup_ui()
        
    def setup_database(self):
        try:
            # Vérification de la base de données en essayant de récupérer un article
            with get_session() as session:
                # Test des nomenclatures
                nomenclatures = session.exec(select(Nomenclature)).all()
                logger.info(f"Nombre total de nomenclatures dans la base : {len(nomenclatures)}")
                if nomenclatures:
                    for n in nomenclatures[:5]:
                        logger.info(f"Exemple de nomenclature : parent={n.code_article_parent}, fils={n.code_article_fils}, qté={n.quantite}")
                else:
                    logger.warning("Aucune nomenclature trouvée dans la base de données !")
                
                # Test des nomenclatures pour TDF160417
                test_code = "TDF160417"
                logger.info(f"Test des nomenclatures pour l'article {test_code}")
                
                # Vérifier si l'article existe
                article = session.exec(
                    select(Article).where(Article.code_article == test_code)
                ).first()
                if article:
                    logger.info(f"Article trouvé : {article.code_article} - {article.libelle_court_article}")
                    
                    # Vérifier ses nomenclatures
                    nomenclatures = session.exec(
                        select(Nomenclature, Article)
                        .join(Article, Article.code_article == Nomenclature.code_article_fils)
                        .where(Nomenclature.code_article_parent == test_code)
                    ).all()
                    
                    if nomenclatures:
                        logger.info(f"Nombre de nomenclatures pour {test_code}: {len(nomenclatures)}")
                        for n, a in nomenclatures:
                            logger.info(f"Article fils: {a.code_article} - {a.libelle_court_article} (qté: {n.quantite})")
                    else:
                        logger.warning(f"Aucune nomenclature trouvée pour {test_code}")
                else:
                    logger.warning(f"Article {test_code} non trouvé dans la base")
                
                # Si on peut créer une session, c'est que la base de données est accessible
                logger.info("Connexion à la base de données réussie")
        except Exception as e:
            logger.error(f"Erreur lors de la connexion à la base de données : {str(e)}")
            show_error_dialog("Erreur de connexion à la base de données", str(e))
            sys.exit(1)

    def setup_ui(self):
        self.setWindowTitle("Consultation des articles")
        self.setGeometry(100, 100, 1200, 800)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Splitter horizontal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Panneau de gauche (recherche)
        self.search_panel = SearchPanel()
        splitter.addWidget(self.search_panel)

        # Panneau de droite (onglets)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.tab_widget = QTabWidget()
        right_layout.addWidget(self.tab_widget)
        splitter.addWidget(right_panel)

        # Onglets
        self.details_panel = DetailsPanel()
        self.tree_panel = TreePanel()
        
        self.tab_widget.addTab(self.details_panel, "Détails")
        self.tab_widget.addTab(self.tree_panel, "Arborescence")

        # Ajuster les proportions du splitter
        splitter.setSizes([300, 900])

        # Connecter les signaux
        self.search_panel.article_selected.connect(self.on_article_selected)
        self.tree_panel.article_selected.connect(self.on_article_selected)

    def on_article_selected(self, code_article):
        """Gère la sélection d'un article"""
        if not code_article:
            return
            
        logger.info(f"Article sélectionné : {code_article}")
        
        with get_session() as session:
            # Récupérer l'article
            article = session.exec(select(Article).where(Article.code_article == code_article)).first()
            
            if article:
                logger.info(f"Article trouvé : {article.code_article} - {article.libelle_court_article}")
                
                # Récupérer les fabricants
                fabricants = session.exec(select(ArticleManufacturer).where(ArticleManufacturer.code_article == code_article)).all()
                logger.info(f"Nombre de fabricants trouvés : {len(fabricants)}")
                
                # Récupérer les nomenclatures où l'article est parent ou fils
                nomenclatures_parent = session.exec(
                    select(Nomenclature)
                    .where(Nomenclature.code_article_parent == code_article)
                ).all()
                
                nomenclatures_fils = session.exec(
                    select(Nomenclature)
                    .where(Nomenclature.code_article_fils == code_article)
                ).all()
                
                nomenclatures = nomenclatures_parent + nomenclatures_fils
                logger.info(f"Nombre de nomenclatures trouvées (parent: {len(nomenclatures_parent)}, fils: {len(nomenclatures_fils)})")
                
                # Récupérer les images
                images = session.exec(select(Image).where(Image.code_article == code_article)).all()
                logger.info(f"Nombre d'images trouvées : {len(images)}")
                
                # Mettre à jour les détails
                logger.info("Mise à jour des détails...")
                self.details_panel.update_article(article)
                self.details_panel.update_manufacturers(fabricants)
                self.details_panel.update_nomenclatures(nomenclatures)
                self.details_panel.update_images(images)
                logger.info("Détails mis à jour avec succès")
                
                # Mettre à jour l'arborescence
                logger.info("Mise à jour de l'arborescence...")
                self.tree_panel.show_article_tree(code_article)
                logger.info("Arborescence mise à jour avec succès")
