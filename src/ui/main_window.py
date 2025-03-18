import sys
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, 
    QWidget, QPushButton, QLabel, QFileDialog,
    QMessageBox
)
from PyQt6.QtCore import Qt

from src.ui.daily_debrief_tab import DailyDebriefTab
from src.ui.trade_data_tab import TradeDataTab
from src.ui.statistics_tab import StatisticsTab
from src.utils.helpers import show_message
from src.utils.csv_importer import CSVImporter

class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        
        self.db_manager = db_manager
        self.setWindowTitle("Trading Journal")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Create header with import button
        header_layout = QHBoxLayout()
        header_label = QLabel("Trading Journal")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        import_button = QPushButton("Import CSV")
        import_button.clicked.connect(self.import_csv)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(import_button)
        
        main_layout.addLayout(header_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.daily_debrief_tab = DailyDebriefTab(self.db_manager)
        self.trade_data_tab = TradeDataTab(self.db_manager)
        self.statistics_tab = StatisticsTab(self.db_manager, self.trade_data_tab)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.daily_debrief_tab, "Daily Debrief")
        self.tab_widget.addTab(self.trade_data_tab, "Fields & Data")
        self.tab_widget.addTab(self.statistics_tab, "Statistics")
        
        main_layout.addWidget(self.tab_widget)
        
        # Connect signals
        self.tab_widget.currentChanged.connect(self.tab_changed)
        
    def tab_changed(self, index):
        """Handle tab change event"""
        # If statistics tab is selected, refresh statistics based on current filters
        if index == 2:  # Statistics tab
            self.statistics_tab.prepare_filters_from_data_tab()
    
    def import_csv(self):
        """Import trade data from CSV file"""
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
            
        # Validate and import CSV
        importer = CSVImporter(file_path)
        valid, message = importer.validate_csv()
        
        if not valid:
            show_message(self, "Import Error", message, QMessageBox.Icon.Critical)
            return
            
        # Read CSV data
        success, data = importer.read_csv()
        
        if not success:
            show_message(self, "Import Error", data, QMessageBox.Icon.Critical)
            return
            
        # Import data to database
        success, message = self.db_manager.import_trades(file_path)
        
        if success:
            show_message(self, "Import Successful", message)
            # Refresh trade data tab
            self.trade_data_tab.load_trades()
        else:
            show_message(self, "Import Error", message, QMessageBox.Icon.Critical) 