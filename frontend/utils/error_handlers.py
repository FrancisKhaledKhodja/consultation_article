from PyQt6.QtWidgets import QMessageBox

def show_error_dialog(title, message, details=None):
    try:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText(message)
        if details:
            error_dialog.setDetailedText(details)
        error_dialog.setWindowTitle(title)
        error_dialog.exec()
    except Exception as e:
        print(f"Erreur lors de l'affichage de la boîte de dialogue : {e}")
