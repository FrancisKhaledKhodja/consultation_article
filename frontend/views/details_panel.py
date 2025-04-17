from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QTabWidget, QTextBrowser, QGroupBox, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import io
from sqlmodel import Session, select
from frontend.views.image_panel import ImagePanel
from creation_base_donnees.models import Article, Image
from frontend.utils.database import get_engine
import logging

logger = logging.getLogger(__name__)

class ImagePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_image_index = 0
        self.images = []
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Zone d'affichage de l'image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)
        
        # Boutons de navigation
        nav_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("< Précédent")
        self.prev_button.clicked.connect(self.show_previous_image)
        self.prev_button.setEnabled(False)
        
        self.next_button = QPushButton("Suivant >")
        self.next_button.clicked.connect(self.show_next_image)
        self.next_button.setEnabled(False)
        
        self.image_counter_label = QLabel()
        self.image_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.image_counter_label)
        nav_layout.addWidget(self.next_button)
        
        layout.addLayout(nav_layout)
        
    def show_previous_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_current_image()
            
    def show_next_image(self):
        if self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
            self.display_current_image()
            
    def display_current_image(self):
        if not self.images:
            self.image_label.setText("Aucune image disponible")
            self.image_label.setPixmap(QPixmap())
            self.image_counter_label.setText("")
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            return
            
        # Mettre à jour le compteur
        self.image_counter_label.setText(f"Image {self.current_image_index + 1}/{len(self.images)}")
        
        # Mettre à jour les boutons
        self.prev_button.setEnabled(self.current_image_index > 0)
        self.next_button.setEnabled(self.current_image_index < len(self.images) - 1)
        
        # Afficher l'image courante
        image_data = self.images[self.current_image_index]
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        
        # Redimensionner l'image si elle est trop grande
        if pixmap.width() > 800 or pixmap.height() > 600:
            pixmap = pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio)
            
        self.image_label.setPixmap(pixmap)
        
    def update_images(self, image_data_list):
        self.images = image_data_list or []
        self.current_image_index = 0 if self.images else -1
        self.display_current_image()

class DetailsPanel(QWidget):
    """Panel affichant les détails d'un article"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_article_code = None
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Onglets
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Onglet Informations générales
        info_tab = QWidget()
        info_layout = QVBoxLayout()
        info_tab.setLayout(info_layout)
        
        # Informations générales
        general_group = QGroupBox("Informations générales")
        general_layout = QVBoxLayout()
        general_group.setLayout(general_layout)
        
        self.code_label = QLabel()
        self.libelle_court_label = QLabel()
        self.libelle_long_label = QLabel()
        self.type_label = QLabel()
        self.statut_label = QLabel()
        self.consommable_label = QLabel()
        self.suivi_num_serie_label = QLabel()
        self.feuille_catalogue_label = QLabel()
        self.description_feuille_catalogue_label = QLabel()
        self.stock_secu_label = QLabel()
        self.cycle_achat_label = QLabel()
        self.lieu_reparation_label = QLabel()
        self.description_lieu_reparation_label = QLabel()
        self.cycle_vie_production_label = QLabel()

        
        general_layout.addWidget(self.code_label)
        general_layout.addWidget(self.libelle_court_label)
        general_layout.addWidget(self.libelle_long_label)
        general_layout.addWidget(self.type_label)
        general_layout.addWidget(self.statut_label)
        general_layout.addWidget(self.consommable_label)
        general_layout.addWidget(self.suivi_num_serie_label)
        general_layout.addWidget(self.feuille_catalogue_label)
        general_layout.addWidget(self.description_feuille_catalogue_label)
        general_layout.addWidget(self.stock_secu_label)
        general_layout.addWidget(self.cycle_achat_label)
        general_layout.addWidget(self.lieu_reparation_label)
        general_layout.addWidget(self.description_lieu_reparation_label)
        general_layout.addWidget(self.cycle_vie_production_label)
        
        info_layout.addWidget(general_group)
        
        # Commentaires
        comments_group = QGroupBox("Commentaires")
        comments_layout = QVBoxLayout()
        comments_group.setLayout(comments_layout)
        
        self.commentaire_technique = QTextBrowser()
        self.commentaire_logistique = QTextBrowser()
        
        technique_label = QLabel("Commentaire technique:")
        logistique_label = QLabel("Commentaire logistique:")
        
        comments_layout.addWidget(technique_label)
        comments_layout.addWidget(self.commentaire_technique)
        comments_layout.addWidget(logistique_label)
        comments_layout.addWidget(self.commentaire_logistique)
        
        info_layout.addWidget(comments_group)
        
        # Ajouter l'onglet Informations
        tabs.addTab(info_tab, "Informations générales")
        
        # Onglet Logistique
        logistic_tab = QWidget()
        logistic_layout = QVBoxLayout()
        logistic_tab.setLayout(logistic_layout)
        
        # Informations de base
        basic_group = QGroupBox("Informations de base")
        basic_layout = QVBoxLayout()
        basic_group.setLayout(basic_layout)
        
        self.affretement_label = QLabel()
        self.hors_normes_label = QLabel()
        self.fragile_label = QLabel()
        
        basic_layout.addWidget(self.affretement_label)
        basic_layout.addWidget(self.hors_normes_label)
        basic_layout.addWidget(self.fragile_label)
        
        logistic_layout.addWidget(basic_group)
        
        # Dimensions
        dimensions_group = QGroupBox("Dimensions et poids")
        dimensions_layout = QVBoxLayout()
        dimensions_group.setLayout(dimensions_layout)
        
        self.poids_label = QLabel()
        self.volume_label = QLabel()
        self.hauteur_label = QLabel()
        self.longueur_label = QLabel()
        self.largeur_label = QLabel()
        
        dimensions_layout.addWidget(self.poids_label)
        dimensions_layout.addWidget(self.volume_label)
        dimensions_layout.addWidget(self.hauteur_label)
        dimensions_layout.addWidget(self.longueur_label)
        dimensions_layout.addWidget(self.largeur_label)
        
        logistic_layout.addWidget(dimensions_group)
        
        # Matière dangereuse
        md_group = QGroupBox("Matière dangereuse")
        md_layout = QVBoxLayout()
        md_group.setLayout(md_layout)
        
        self.md_label = QLabel()
        self.md_code_onu_label = QLabel()
        self.md_groupe_emballage_label = QLabel()
        self.md_type_colis_label = QLabel()
        
        md_layout.addWidget(self.md_label)
        md_layout.addWidget(self.md_code_onu_label)
        md_layout.addWidget(self.md_groupe_emballage_label)
        md_layout.addWidget(self.md_type_colis_label)
        
        logistic_layout.addWidget(md_group)
        
        # Ajouter l'onglet Logistique
        tabs.addTab(logistic_tab, "Logistique")
        
        # Onglet Fabricants
        manufacturers_tab = QWidget()
        manufacturers_layout = QVBoxLayout()
        manufacturers_tab.setLayout(manufacturers_layout)
        
        self.manufacturers_table = QTableWidget()
        self.manufacturers_table.setColumnCount(2)
        self.manufacturers_table.setHorizontalHeaderLabels(["Fabricant", "Référence"])
        self.manufacturers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        manufacturers_layout.addWidget(self.manufacturers_table)
        tabs.addTab(manufacturers_tab, "Fabricants")
        
        # Onglet Nomenclatures
        nomenclatures_tab = QWidget()
        nomenclatures_layout = QVBoxLayout()
        nomenclatures_tab.setLayout(nomenclatures_layout)
        
        self.nomenclatures_table = QTableWidget()
        self.nomenclatures_table.setColumnCount(5)
        self.nomenclatures_table.setHorizontalHeaderLabels(["Relation", "Code Article", "Libellé", "Type", "Quantité"])
        self.nomenclatures_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        nomenclatures_layout.addWidget(self.nomenclatures_table)
        tabs.addTab(nomenclatures_tab, "Nomenclatures")
        
        # Onglet Images
        images_tab = QWidget()
        images_layout = QVBoxLayout()
        images_tab.setLayout(images_layout)
        
        self.image_panel = ImagePanel()
        images_layout.addWidget(self.image_panel)
        
        tabs.addTab(images_tab, "Images")
        
    def update_article(self, article):
        """Met à jour les informations de l'article"""
        if not article:
            return
            
        self.current_article_code = article.code_article
        
        # Informations générales
        self.code_label.setText(f"Code article : {article.code_article}")
        self.libelle_court_label.setText(f"Libellé court : {article.libelle_court_article}")
        self.libelle_long_label.setText(f"Libellé long : {article.libelle_long_article or ''}")
        self.type_label.setText(f"Type : {article.type_article or ''}")
        self.statut_label.setText(f"Statut: {article.statut_abrege_article or ''}")
        self.consommable_label.setText(f"Consommable: {article.catalogue_consommable or ''}")
        self.suivi_num_serie_label.setText(f"Suivie par num serie: {article.suivi_par_num_serie_oui_non or ''}")
        self.feuille_catalogue_label.setText(f"Feuiile catalogue: {article.feuille_du_catalogue or ''}")
        self.description_feuille_catalogue_label.setText(f"Descrip. feuille: {article.description_de_la_feuille_du_catalogue or ''}")
        self.stock_secu_label.setText(f"Stock secu: {article.stocksecu_inv_oui_non or ''}")
        self.cycle_achat_label.setText(f"Cycle achat: {article.cycle_de_vie_achat or ''}")
        self.lieu_reparation_label.setText(f"Code réparateur: {article.lieu_de_reparation_pim or ''}")
        self.description_lieu_reparation_label.setText(f"Libellé réparateur: {article.description_lieu_de_reparation or ''}")
        self.cycle_vie_production_label.setText(f"Cycle production: {article.cycle_de_vie_de_production_pim or ''}")

      
        # Commentaires
        self.commentaire_technique.setText(article.commentaire_technique or '')
        self.commentaire_logistique.setText(article.commentaire_logistique or '')
        
        # Informations logistiques de base
        self.affretement_label.setText(f"Affrètement : {'Oui' if article.affretement else 'Non'}")
        self.hors_normes_label.setText(f"Article hors normes : {'Oui' if article.article_hors_normes else 'Non'}")
        self.fragile_label.setText(f"Fragile : {'Oui' if article.fragile else 'Non'}")
        
        # Dimensions et poids
        self.poids_label.setText(f"Poids : {article.poids_article or 'Non spécifié'}")
        self.volume_label.setText(f"Volume : {article.volume_article or 'Non spécifié'}")
        self.hauteur_label.setText(f"Hauteur : {article.hauteur_article or 'Non spécifié'}")
        self.longueur_label.setText(f"Longueur : {article.longueur_article or 'Non spécifié'}")
        self.largeur_label.setText(f"Largeur : {article.largeur_article or 'Non spécifié'}")
        
        # Matière dangereuse
        self.md_label.setText(f"Matière dangereuse : {'Oui' if article.matiere_dangereuse else 'Non'}")
        self.md_code_onu_label.setText(f"Code ONU : {article.md_code_onu or 'Non spécifié'}")
        self.md_groupe_emballage_label.setText(f"Groupe d'emballage : {article.md_groupe_emballage or 'Non spécifié'}")
        self.md_type_colis_label.setText(f"Type de colis : {article.md_type_colis or 'Non spécifié'}")
            
    def update_manufacturers(self, manufacturers):
        """Met à jour la table des fabricants"""
        self.manufacturers_table.setRowCount(0)
        
        if not manufacturers:
            return
            
        self.manufacturers_table.setRowCount(len(manufacturers))
        for row, manufacturer in enumerate(manufacturers):
            self.manufacturers_table.setItem(row, 0, QTableWidgetItem(manufacturer.nom_fabricant or ''))
            self.manufacturers_table.setItem(row, 1, QTableWidgetItem(manufacturer.reference_article_fabricant or ''))
            
    def update_nomenclatures(self, nomenclatures):
        """Met à jour le tableau des nomenclatures"""
        # Effacer le contenu actuel
        self.nomenclatures_table.setRowCount(0)
        
        if not nomenclatures:
            return
            
        # Configurer le tableau
        self.nomenclatures_table.setRowCount(len(nomenclatures))
        
        try:
            with Session(get_engine()) as session:
                # Récupérer tous les codes articles (parents et fils)
                article_codes = []
                for n in nomenclatures:
                    if n.code_article_parent not in article_codes:
                        article_codes.append(n.code_article_parent)
                    if n.code_article_fils not in article_codes:
                        article_codes.append(n.code_article_fils)
                
                # Récupérer tous les articles en une seule requête
                articles = {
                    article.code_article: article 
                    for article in session.exec(
                        select(Article).where(Article.code_article.in_(article_codes))
                    ).all()
                }
                
                # Remplir le tableau avec les données
                for row, nomenclature in enumerate(nomenclatures):
                    # Si l'article est parent, on affiche le fils
                    # Si l'article est fils, on affiche le parent
                    article_code = nomenclature.code_article_fils
                    is_parent = True
                    
                    if article_code == self.current_article_code:
                        article_code = nomenclature.code_article_parent
                        is_parent = False
                    
                    article = articles.get(article_code)
                    if not article:
                        continue
                    

                    # Ajouter une indication du type de relation
                    relation = "Est composé de" if is_parent else "Entre dans la composition de"
                    self.nomenclatures_table.setItem(row, 0, QTableWidgetItem(relation))
                    # Remplir la ligne
                    self.nomenclatures_table.setItem(row, 1, QTableWidgetItem(article.code_article))
                    self.nomenclatures_table.setItem(row, 2, QTableWidgetItem(article.libelle_court_article))
                    self.nomenclatures_table.setItem(row, 3, QTableWidgetItem(article.type_article or ''))
                    self.nomenclatures_table.setItem(row, 4, QTableWidgetItem(f"{nomenclature.quantite:.1f}"))
                    
                    
                    
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des nomenclatures : {str(e)}")
            
    def update_images(self, images):
        """Met à jour les images dans le panneau d'images"""
        if not images:
            self.image_panel.update_images([])
            return
            
        # Extraire les données binaires des images
        image_data_list = []
        for image in images:
            if hasattr(image, 'image') and image.image:
                image_data_list.append(image.image)
                
        # Mettre à jour le panneau d'images avec les données binaires
        self.image_panel.update_images(image_data_list)
