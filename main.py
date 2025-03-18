import sys
from src.ui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication
from src.database.db_manager import DatabaseManager
from src.utils.init_data import init_default_instruments

def main():
    # Initialize database
    db_manager = DatabaseManager()
    db_manager.setup_database()
    
    # Initialize default data
    init_default_instruments(db_manager)
    
    # Initialize application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow(db_manager)
    window.show()
    
    # Run application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 