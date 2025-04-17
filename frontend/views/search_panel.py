from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                            QHeaderView, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal
from backend.api import get_session
from sqlmodel import select, or_
from creation_base_donnees.models import Article, ArticleManufacturer

class SearchPanel(QWidget):
    article_selected = pyqtSignal(str)  # Signal émis quand un article est sélectionné
    
    # Liste des champs texte à rechercher dans Article
    ARTICLE_SEARCHABLE_FIELDS = [
        'code_article',
        'proprietaire_article',
        'type_article',
        'libelle_court_article',
        'libelle_long_article',
        'description_famille_d_achat',
        'commentaire_technique',
        'commentaire_logistique',
        'statut_abrege_article',
        'cycle_de_vie_achat',
        'cycle_de_vie_de_production_pim',
        'feuille_du_catalogue',
        'description_de_la_feuille_du_catalogue',
        'famille_d_achat_feuille_du_catalogue',
        'catalogue_consommable',
        'criticite_pim'
    ]
    
    # Liste des champs booléens à rechercher dans Article
    ARTICLE_BOOLEAN_FIELDS = [
        'suivi_par_num_serie_oui_non',
        'stocksecu_inv_oui_non',
        'article_hors_normes',
        'peremption',
        'retour_production',
        'is_oc',
        'is_ol',
        'affretement',
        'fragile',
        'matiere_dangereuse'
    ]
    
    # Liste des champs à rechercher dans ArticleManufacturer
    MANUFACTURER_SEARCHABLE_FIELDS = [
        'nom_fabricant',
        'reference_article_fabricant'
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Créer un splitter vertical pour la zone de recherche
        search_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Widget du haut pour la zone de recherche
        search_top = QWidget()
        search_top_layout = QVBoxLayout(search_top)
        
        # Zone de recherche
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher dans tous les champs...")
        search_button = QPushButton("Rechercher")
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        search_top_layout.addLayout(search_layout)
        search_top_layout.addWidget(QLabel("Résultats de recherche :"))
        
        # Widget du bas pour la table des résultats
        search_bottom = QWidget()
        search_bottom_layout = QVBoxLayout(search_bottom)
        
        # Table des résultats de recherche
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Code Article",
            "Libellé",
            "Statut",
            "Type",
            "Criticité"
        ])
        self.results_table.setSortingEnabled(True)
        
        # Ajuster les colonnes
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        search_bottom_layout.addWidget(self.results_table)
        
        # Ajouter les widgets au splitter
        search_splitter.addWidget(search_top)
        search_splitter.addWidget(search_bottom)
        
        # Définir les tailles initiales
        search_splitter.setStretchFactor(0, 1)
        search_splitter.setStretchFactor(1, 2)
        
        layout.addWidget(search_splitter)

        # Connecter les signaux
        self.search_input.returnPressed.connect(self.search_articles)
        search_button.clicked.connect(self.search_articles)
        self.results_table.itemClicked.connect(self.on_result_selected)

    def search_articles(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            return
            
        try:
            with get_session() as session:
                # Construire les conditions de recherche pour Article (champs texte)
                article_conditions = []
                for field in self.ARTICLE_SEARCHABLE_FIELDS:
                    attr = getattr(Article, field)
                    article_conditions.append(attr.ilike(f"%{keyword}%"))
                
                # Ajouter les conditions pour les champs booléens
                if keyword.lower() in ('oui', 'non'):
                    for field in self.ARTICLE_BOOLEAN_FIELDS:
                        attr = getattr(Article, field)
                        article_conditions.append(attr == (keyword.lower() == 'oui'))

                # Requête avec jointure et conditions
                query = (
                    select(Article)
                    .outerjoin(ArticleManufacturer)
                    .where(or_(*article_conditions))
                )
                
                results = session.exec(query).all()
                self.update_results(results)
        except Exception as e:
            import traceback
            print(f"Erreur complète : {traceback.format_exc()}")
            from frontend.utils.error_handlers import show_error_dialog
            show_error_dialog(
                "Erreur de recherche",
                "Impossible d'effectuer la recherche",
                str(e)
            )

    def on_result_selected(self, item):
        row = item.row()
        code_article = self.results_table.item(row, 0).text()
        self.article_selected.emit(code_article)

    def update_results(self, results):
        """Met à jour la table des résultats"""
        self.results_table.setRowCount(0)
        if not results:
            return
            
        # Afficher les résultats
        for article in results:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            # Informations de l'article
            self.results_table.setItem(row, 0, QTableWidgetItem(article.code_article))
            self.results_table.setItem(row, 1, QTableWidgetItem(article.libelle_court_article or ""))
            self.results_table.setItem(row, 2, QTableWidgetItem(article.statut_abrege_article or ""))
            self.results_table.setItem(row, 3, QTableWidgetItem(article.type_article or ""))
            self.results_table.setItem(row, 4, QTableWidgetItem(article.criticite_pim or ""))
