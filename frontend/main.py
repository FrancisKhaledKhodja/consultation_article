import sys
import os
import logging
from PyQt6.QtWidgets import QApplication

# Ajout du chemin racine au PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from frontend.utils.logging_config import setup_logging
from frontend.views.main_window import MainWindow

def main():
    try:
        # Initialiser l'application Qt
        app = QApplication(sys.argv)
        
        # Configurer le logging
        log_file = setup_logging()
        if not log_file:
            print("Attention: La configuration du logging a échoué")
        
        # Créer et afficher la fenêtre principale
        window = MainWindow()
        window.show()
        
        # Démarrer la boucle d'événements
        return app.exec()
        
    except Exception as e:
        logging.error(f"Erreur fatale lors du démarrage de l'application: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
