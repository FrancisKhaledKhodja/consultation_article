from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from sqlmodel import Session
from frontend.utils.database import get_engine
from frontend.utils.logging_config import logger

class ImagePanel(QWidget):
    """Panel affichant les images d'un article"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Scroll area pour les images
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Widget contenant les images
        content = QWidget()
        self.image_layout = QVBoxLayout()
        content.setLayout(self.image_layout)
        scroll.setWidget(content)
        
        # Label par défaut
        self.no_image_label = QLabel("Aucune image disponible")
        self.no_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_layout.addWidget(self.no_image_label)
        
    def clear_images(self):
        """Nettoie toutes les images"""
        while self.image_layout.count():
            child = self.image_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def update_images(self, image_data_list):
        """Met à jour les images affichées depuis la base de données
        
        Args:
            image_data_list: Liste des données binaires des images
        """
        # Nettoyer les images existantes
        self.clear_images()
                
        if not image_data_list:
            # Afficher le message par défaut
            self.no_image_label = QLabel("Aucune image disponible")
            self.no_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.image_layout.addWidget(self.no_image_label)
            return
            
        # Ajouter les nouvelles images
        for image_data in image_data_list:
            try:
                # Vérifier que les données ne sont pas vides
                if not image_data:
                    logger.warning(f"Données d'image vides")
                    continue
                    
                # Créer un label pour l'image
                image_label = QLabel()
                pixmap = QPixmap()
                
                # Charger les données binaires dans le QPixmap
                success = pixmap.loadFromData(image_data)
                if not success:
                    logger.error(f"Impossible de charger l'image")
                    continue
                    
                # Redimensionner l'image si elle est trop grande
                if pixmap.width() > 800:
                    pixmap = pixmap.scaledToWidth(800, Qt.TransformationMode.SmoothTransformation)
                    
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                self.image_layout.addWidget(image_label)
                self.image_layout.addSpacing(10)  # Espace entre les images
                
            except Exception as e:
                logger.error(f"Erreur lors de l'affichage de l'image : {str(e)}")
                continue
                
        # Ajouter un espaceur à la fin
        self.image_layout.addStretch()
