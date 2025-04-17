import os
import logging

logger = logging.getLogger('ConsultationArticle')
logger.setLevel(logging.DEBUG)
logger.handlers = []

def setup_logging():
    try:
        # Créer le dossier de logs s'il n'existe pas
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Configurer le logging dans un fichier
        log_file = os.path.join(log_dir, "app.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        
        # Ajouter aussi un handler pour la console en mode debug
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(console_handler)
        
        return log_file
    except Exception as e:
        print(f"Erreur lors de la configuration du logging : {e}")
        return None
