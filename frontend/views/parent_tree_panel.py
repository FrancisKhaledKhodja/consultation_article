from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem, QMessageBox)
from PyQt6.QtCore import pyqtSignal
from backend.api import get_session
from sqlmodel import select
from creation_base_donnees.models import Article, Nomenclature
from frontend.utils.logging_config import logger

class ParentTreePanel(QWidget):
    article_selected = pyqtSignal(str)  # Signal émis quand un article est sélectionné

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self._current_article = None

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Articles parents :"))
        
        # Arbre des articles parents
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels([
            "Code Article | Libellé | Type | Quantité"
        ])
        self.tree_widget.setColumnWidth(0, 800)
        layout.addWidget(self.tree_widget)

        # Connecter les signaux
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)

    def show_article_parents(self, code_article):
        """Affiche l'arborescence des parents pour l'article donné"""
        if not code_article:
            return
            
        self._current_article = code_article
        try:
            with get_session() as session:
                # Récupérer l'article
                article = session.exec(
                    select(Article).where(Article.code_article == code_article)
                ).first()
                
                if not article:
                    logger.warning(f"Article {code_article} non trouvé dans la base de données.")
                    return
                    
                # Construire l'arborescence des parents
                tree_data = self._build_parent_tree_data(session, article)
                self.update_tree(tree_data)
                
        except Exception as e:
            logger.error(f"Erreur lors de la construction de l'arborescence des parents : {str(e)}")
            QMessageBox.critical(self, "Erreur", "Une erreur est survenue lors de la construction de l'arborescence des parents.")

    def _build_parent_tree_data(self, session, article, child_code=None, depth=0):
        """Construit récursivement l'arborescence des parents d'un article avec leurs propres fils"""
        if depth > 10:  # Limite de profondeur pour éviter les boucles infinies
            return None
            
        # Données de base de l'article
        tree_data = {
            'code': article.code_article,
            'libelle': article.libelle_court_article or '',
            'type': article.type_article or '',
            'quantite': ''
        }
        
        # Si ce n'est pas l'article initial, chercher sa quantité par rapport à son fils
        if child_code:
            nomenclature = session.exec(
                select(Nomenclature)
                .where(Nomenclature.code_article_parent == article.code_article)
                .where(Nomenclature.code_article_fils == child_code)
            ).first()
            if nomenclature:
                tree_data['quantite'] = f"{nomenclature.quantite:.1f}"
        
        # Chercher tous les articles fils de cet article (sauf l'article initial)
        fils_nomenclatures = session.exec(
            select(Nomenclature, Article)
            .join(Article, Article.code_article == Nomenclature.code_article_fils)
            .where(Nomenclature.code_article_parent == article.code_article)
        ).all()
        
        if fils_nomenclatures:
            tree_data['children'] = []
            for n, fils in fils_nomenclatures:
                # Ne pas inclure l'article initial dans l'arborescence pour éviter les cycles
                if fils.code_article != self._current_article:
                    child_data = {
                        'code': fils.code_article,
                        'libelle': fils.libelle_court_article or '',
                        'type': fils.type_article or '',
                        'quantite': f"{n.quantite:.1f}",
                        'depth': depth + 1
                    }
                    
                    # Récursivement chercher les fils de ce fils
                    fils_of_fils = session.exec(
                        select(Nomenclature, Article)
                        .join(Article, Article.code_article == Nomenclature.code_article_fils)
                        .where(Nomenclature.code_article_parent == fils.code_article)
                    ).all()
                    
                    if fils_of_fils:
                        child_data['children'] = []
                        for n2, fils2 in fils_of_fils:
                            if fils2.code_article != self._current_article:
                                child_data['children'].append({
                                    'code': fils2.code_article,
                                    'libelle': fils2.libelle_court_article or '',
                                    'type': fils2.type_article or '',
                                    'quantite': f"{n2.quantite:.1f}",
                                    'depth': depth + 2
                                })
                    
                    tree_data['children'].append(child_data)
        
        # Chercher les articles parents
        parent_nomenclatures = session.exec(
            select(Nomenclature, Article)
            .join(Article, Article.code_article == Nomenclature.code_article_parent)
            .where(Nomenclature.code_article_fils == article.code_article)
        ).all()
        
        if parent_nomenclatures:
            tree_data['parents'] = []
            for n, parent in parent_nomenclatures:
                parent_data = self._build_parent_tree_data(session, parent, article.code_article, depth + 1)
                if parent_data:
                    tree_data['parents'].append(parent_data)
                    
        return tree_data

    def on_tree_item_clicked(self, item, column):
        # Extraire le code article de l'item sélectionné
        item_text = item.text(0)
        code_article = item_text.split("|")[0].strip()
        if code_article != self._current_article:  # Éviter la récursion infinie
            self.article_selected.emit(code_article)

    def update_tree(self, tree_data):
        self.tree_widget.clear()
        if not tree_data:
            return
            
        def add_tree_items(parent, items, is_child=False):
            if not isinstance(items, list):
                items = [items]
                
            for item in items:
                tree_item = QTreeWidgetItem(parent)
                tree_item.setText(0, f"{item['code']} | {item['libelle']} | {item['type']} | {item['quantite']}")
                
                # Ajouter les enfants avec indentation
                if 'children' in item:
                    child_parent = QTreeWidgetItem(tree_item)
                    child_parent.setText(0, "Articles fils :")
                    
                    for child in item['children']:
                        child_item = QTreeWidgetItem(child_parent)
                        prefix = "  " * (child.get('depth', 1))
                        child_item.setText(0, f"{prefix}└─ {child['code']} | {child['libelle']} | {child['type']} | {child['quantite']}")
                        
                        # Ajouter les fils des fils
                        if 'children' in child:
                            child_fils_parent = QTreeWidgetItem(child_item)
                            child_fils_parent.setText(0, f"{prefix}  Articles fils :")
                            for fils in child['children']:
                                fils_item = QTreeWidgetItem(child_fils_parent)
                                prefix2 = "  " * (fils.get('depth', 2))
                                fils_item.setText(0, f"{prefix2}└─ {fils['code']} | {fils['libelle']} | {fils['type']} | {fils['quantite']}")
                
                # Ajouter les parents
                if 'parents' in item:
                    add_tree_items(tree_item, item['parents'])
                    
        # Créer l'item racine
        root_item = QTreeWidgetItem(self.tree_widget)
        root_item.setText(0, f"{tree_data['code']} | {tree_data['libelle']} | {tree_data['type']} | {tree_data['quantite']}")
        
        # Ajouter les parents et leurs fils
        if 'parents' in tree_data:
            add_tree_items(root_item, tree_data['parents'])
            
        # Développer l'arbre
        self.tree_widget.expandAll()
