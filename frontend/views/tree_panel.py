from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTreeWidget, QTreeWidgetItem, QMessageBox, QLabel
)
from PyQt6.QtCore import pyqtSignal
from sqlmodel import select
from backend.api import get_session
from creation_base_donnees.models import Article, Nomenclature
from frontend.utils.logging_config import logger

class TreePanel(QWidget):
    """Panel affichant l'arborescence des articles"""
    
    article_selected = pyqtSignal(str)  # Signal émis quand un article est sélectionné
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Zone de recherche pour l'arborescence
        search_layout = QHBoxLayout()
        self.tree_code_input = QLineEdit()
        self.tree_code_input.setPlaceholderText("Code article...")
        search_layout.addWidget(self.tree_code_input)
        
        tree_search_button = QPushButton("Rechercher")
        search_layout.addWidget(tree_search_button)
        layout.addLayout(search_layout)
        
        # Arbre des articles
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Article"])
        self.tree_widget.setColumnWidth(0, 800)
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.tree_widget)
        
        # Connecter les signaux
        tree_search_button.clicked.connect(lambda: self.show_article_tree(self.tree_code_input.text().strip()))
        
    def on_item_double_clicked(self, item, column):
        """Quand un article est double-cliqué dans l'arbre"""
        text = item.text(0)
        if text:
            # Extraire le code article (première partie avant le |)
            code = text.split('|')[0].strip()
            if code:
                self.article_selected.emit(code)
                
    def show_article_tree(self, code_article=None):
        """Affiche l'arborescence d'un article"""
        if not code_article:
            return
            
        self.tree_widget.clear()
        
        try:
            with get_session() as session:
                article = session.exec(
                    select(Article).where(Article.code_article == code_article)
                ).first()
                
                if not article:
                    return
                    
                # Créer l'item racine
                root = QTreeWidgetItem(self.tree_widget)
                root.setText(0, f"{article.code_article} | {article.libelle_court_article}")
                
                # Construire l'arbre récursivement
                self._build_tree(session, root, article.code_article)
                
                # Développer l'arbre
                self.tree_widget.expandAll()
                
        except Exception as e:
            logger.error(f"Erreur lors de la construction de l'arbre : {str(e)}")
            QMessageBox.critical(self, "Erreur", "Une erreur est survenue lors de la construction de l'arborescence.")
            
    def _build_tree(self, session, parent_item, code_article_parent, depth=0):
        """Construit récursivement l'arbre des articles"""
        if depth > 10:  # Limite de profondeur pour éviter les boucles infinies
            return
            
        try:
            # Récupérer les nomenclatures
            nomenclatures = session.exec(
                select(Nomenclature, Article)
                .join(Article, Article.code_article == Nomenclature.code_article_fils)
                .where(Nomenclature.code_article_parent == code_article_parent)
            ).all()
            
            for nomenclature, article in nomenclatures:
                # Créer un item pour l'article fils
                item = QTreeWidgetItem(parent_item)
                item.setText(0, f"{article.code_article} | {article.libelle_court_article} | {article.type_article or ''} | {nomenclature.quantite:.1f}")
                
                # Récursivement construire l'arbre pour cet article
                self._build_tree(session, item, article.code_article, depth + 1)
                
        except Exception as e:
            logger.error(f"Erreur lors de la construction d'une branche : {str(e)}")
            raise
