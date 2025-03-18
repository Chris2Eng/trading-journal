from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QDateEdit, QPushButton, QGroupBox, QMessageBox
)
from PyQt6.QtCore import QDate, Qt, QTimer
from datetime import datetime
from src.utils.helpers import get_current_trading_date, show_message
import time

class DailyDebriefTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
        # Set up timer to check for new trading day
        self.check_for_new_day_timer = QTimer()
        self.check_for_new_day_timer.timeout.connect(self.check_for_new_trading_day)
        self.check_for_new_day_timer.start(60000)  # Check every minute
        
        # Load current trading day data
        self.current_date = get_current_trading_date()
        self.date_edit.setDate(QDate.fromString(self.current_date, "yyyy-MM-dd"))
        self.load_debrief_data()
        
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        
        # Date selection
        date_layout = QHBoxLayout()
        date_label = QLabel("Trading Date:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.dateChanged.connect(self.date_changed)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        
        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_clicked)
        date_layout.addWidget(load_button)
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_clicked)
        date_layout.addWidget(save_button)
        
        layout.addLayout(date_layout)
        
        # Debrief section
        debrief_group = QGroupBox("1. Debrief")
        debrief_layout = QVBoxLayout(debrief_group)
        
        # Intraday summary
        intraday_label = QLabel("1.1 Intraday Summary:")
        self.intraday_text = QTextEdit()
        debrief_layout.addWidget(intraday_label)
        debrief_layout.addWidget(self.intraday_text)
        
        # Feelings/self-talk
        feelings_label = QLabel("1.2 Feelings/Self-talk:")
        self.feelings_text = QTextEdit()
        debrief_layout.addWidget(feelings_label)
        debrief_layout.addWidget(self.feelings_text)
        
        layout.addWidget(debrief_group)
        
        # Recurring patterns section
        patterns_group = QGroupBox("2. Recurring Patterns")
        patterns_layout = QVBoxLayout(patterns_group)
        
        patterns_label = QLabel("2.1 Recurring Patterns:")
        self.patterns_text = QTextEdit()
        patterns_layout.addWidget(patterns_label)
        patterns_layout.addWidget(self.patterns_text)
        
        play_out_label = QLabel("2.2 When They Best Play Out:")
        self.play_out_text = QTextEdit()
        patterns_layout.addWidget(play_out_label)
        patterns_layout.addWidget(self.play_out_text)
        
        layout.addWidget(patterns_group)
        
        # Leverage section
        leverage_group = QGroupBox("3. Using Information to Leverage Up/Down")
        leverage_layout = QVBoxLayout(leverage_group)
        
        self.leverage_text = QTextEdit()
        leverage_layout.addWidget(self.leverage_text)
        
        layout.addWidget(leverage_group)
    
    def date_changed(self, date):
        """Handle date change event"""
        self.current_date = date.toString("yyyy-MM-dd")
    
    def load_clicked(self):
        """Load debrief data for the selected date"""
        self.load_debrief_data()
    
    def save_clicked(self):
        """Save debrief data for the current date"""
        success, message = self.db_manager.save_daily_debrief(
            self.current_date,
            self.intraday_text.toPlainText(),
            self.feelings_text.toPlainText(),
            self.patterns_text.toPlainText(),
            self.play_out_text.toPlainText(),
            self.leverage_text.toPlainText()
        )
        
        if success:
            show_message(self, "Save Successful", f"Daily debrief for {self.current_date} saved successfully.")
        else:
            show_message(self, "Save Error", message, QMessageBox.Icon.Critical)
    
    def load_debrief_data(self):
        """Load debrief data for the current date"""
        debrief_data = self.db_manager.get_daily_debrief(self.current_date)
        
        if debrief_data:
            self.intraday_text.setText(debrief_data.get('intraday_summary', ''))
            self.feelings_text.setText(debrief_data.get('feelings', ''))
            self.patterns_text.setText(debrief_data.get('recurring_patterns', ''))
            self.play_out_text.setText(debrief_data.get('best_play_out', ''))
            self.leverage_text.setText(debrief_data.get('leverage_info', ''))
        else:
            # Clear all fields for a new date
            self.intraday_text.clear()
            self.feelings_text.clear()
            self.patterns_text.clear()
            self.play_out_text.clear()
            self.leverage_text.clear()
    
    def check_for_new_trading_day(self):
        """Check if a new trading day has started and reset fields if needed"""
        new_trading_date = get_current_trading_date()
        
        # If the trading date has changed, update the date and clear fields
        if new_trading_date != self.current_date:
            self.current_date = new_trading_date
            self.date_edit.setDate(QDate.fromString(self.current_date, "yyyy-MM-dd"))
            self.load_debrief_data()  # This will clear fields if no data for the new date 