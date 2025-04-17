import sys
import logging
from PyQt6.QtWidgets import QApplication
from frontend.views.main_window import MainWindow

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)

def main():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        return app.exec()
    except Exception as e:
        logging.error(f"Erreur lors du démarrage de l'application: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
