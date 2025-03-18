from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton, 
    QComboBox, QDateEdit, QTimeEdit, QGroupBox,
    QFileDialog, QHeaderView, QSpinBox, QMessageBox,
    QStyledItemDelegate
)
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QColor

from datetime import datetime
from src.utils.helpers import (
    get_entry_strategy_options, format_date, 
    show_message, save_image, load_image_as_pixmap
)

class EntryStrategyDelegate(QStyledItemDelegate):
    """Custom delegate for Entry Strategy dropdown in table cells"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.strategies = get_entry_strategy_options()
    
    def createEditor(self, parent, option, index):
        """Create the dropdown editor"""
        combo = QComboBox(parent)
        combo.addItems(self.strategies)
        return combo
    
    def setEditorData(self, editor, index):
        """Set the current value in the editor"""
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole) or ""
        if value in self.strategies:
            editor.setCurrentText(value)
        else:
            editor.setCurrentIndex(0)
    
    def setModelData(self, editor, model, index):
        """Set the data when editing is finished"""
        model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update the editor's geometry"""
        editor.setGeometry(option.rect)


class TradeDataTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_filters = {}
        self.init_ui()
        self.load_trades()
        
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        
        # Filters section
        filters_group = QGroupBox("Filters")
        filters_layout = QVBoxLayout(filters_group)
        
        # Date filters
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date Range:"))
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        
        date_layout.addWidget(self.start_date_edit)
        date_layout.addWidget(QLabel("to"))
        date_layout.addWidget(self.end_date_edit)
        
        date_layout.addWidget(QLabel("Time Range:"))
        
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setTime(QTime(0, 0, 0))
        
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setTime(QTime(23, 59, 59))
        
        date_layout.addWidget(self.start_time_edit)
        date_layout.addWidget(QLabel("to"))
        date_layout.addWidget(self.end_time_edit)
        
        filters_layout.addLayout(date_layout)
        
        # Other filters
        other_filters_layout = QHBoxLayout()
        
        other_filters_layout.addWidget(QLabel("Instrument:"))
        self.instrument_combo = QComboBox()
        self.instrument_combo.addItem("All", None)
        self.load_instruments()
        other_filters_layout.addWidget(self.instrument_combo)
        
        other_filters_layout.addWidget(QLabel("Action:"))
        self.action_combo = QComboBox()
        self.action_combo.addItem("All", None)
        self.action_combo.addItem("Buy", "Buy")
        self.action_combo.addItem("Sell", "Sell")
        other_filters_layout.addWidget(self.action_combo)
        
        other_filters_layout.addWidget(QLabel("Entry Strategy:"))
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItem("All", None)
        for strategy in get_entry_strategy_options():
            self.strategy_combo.addItem(strategy, strategy)
        other_filters_layout.addWidget(self.strategy_combo)
        
        other_filters_layout.addWidget(QLabel("Bars:"))
        self.min_bars_spin = QSpinBox()
        self.min_bars_spin.setMinimum(0)
        self.min_bars_spin.setMaximum(9999)
        
        self.max_bars_spin = QSpinBox()
        self.max_bars_spin.setMinimum(0)
        self.max_bars_spin.setMaximum(9999)
        self.max_bars_spin.setValue(9999)
        
        other_filters_layout.addWidget(self.min_bars_spin)
        other_filters_layout.addWidget(QLabel("to"))
        other_filters_layout.addWidget(self.max_bars_spin)
        
        filters_layout.addLayout(other_filters_layout)
        
        # Filter buttons
        buttons_layout = QHBoxLayout()
        
        apply_button = QPushButton("Apply Filters")
        apply_button.clicked.connect(self.apply_filters)
        
        clear_button = QPushButton("Clear Filters")
        clear_button.clicked.connect(self.clear_filters)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(apply_button)
        buttons_layout.addWidget(clear_button)
        
        filters_layout.addLayout(buttons_layout)
        
        layout.addWidget(filters_group)
        
        # Trades table
        self.trades_table = QTableWidget()
        self.trades_table.setColumnCount(12)  # Adjusted column count per requirements
        self.trades_table.setHorizontalHeaderLabels([
            "Date", "Time", "Instrument", "Action", "Quantity", 
            "Price", "Commission", "MAE", "MFE", "Bars", 
            "Entry Strategy", "Photo"
        ])
        
        # Set column resize modes
        header = self.trades_table.horizontalHeader()
        for i in range(self.trades_table.columnCount()):
            if i == 10:  # Entry Strategy column
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        # Set the custom delegate for Entry Strategy column
        self.trades_table.setItemDelegateForColumn(10, EntryStrategyDelegate(self.trades_table))
        
        layout.addWidget(self.trades_table)
        
        # Connect signals
        self.trades_table.cellDoubleClicked.connect(self.cell_double_clicked)
        self.trades_table.cellChanged.connect(self.cell_changed)
    
    def cell_changed(self, row, column):
        """Handle cell value changes"""
        if column == 10:  # Entry Strategy column
            # Get the trade ID and new value
            trade_id = self.trades_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            new_value = self.trades_table.item(row, column).text()
            
            if trade_id and new_value:
                # Update the database
                self.db_manager.update_trade_entry_strategy(trade_id, new_value)
    
    def load_instruments(self):
        """Load instruments into combo box"""
        instruments = self.db_manager.get_instruments()
        for name, _ in instruments:
            self.instrument_combo.addItem(name, name)
    
    def apply_filters(self):
        """Apply filters to trades display"""
        self.current_filters = {
            'start_date': self.start_date_edit.date().toString("yyyy-MM-dd"),
            'end_date': self.end_date_edit.date().toString("yyyy-MM-dd"),
            'start_time': self.start_time_edit.time().toString("HH:mm:ss"),
            'end_time': self.end_time_edit.time().toString("HH:mm:ss"),
            'instrument': self.instrument_combo.currentData(),
            'action': self.action_combo.currentData(),
            'entry_strategy': self.strategy_combo.currentData(),
            'min_bars': self.min_bars_spin.value() if self.min_bars_spin.value() > 0 else None,
            'max_bars': self.max_bars_spin.value() if self.max_bars_spin.value() < 9999 else None
        }
        
        self.load_trades()
    
    def clear_filters(self):
        """Clear all filters"""
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.end_date_edit.setDate(QDate.currentDate())
        self.start_time_edit.setTime(QTime(0, 0, 0))
        self.end_time_edit.setTime(QTime(23, 59, 59))
        self.instrument_combo.setCurrentIndex(0)
        self.action_combo.setCurrentIndex(0)
        self.strategy_combo.setCurrentIndex(0)
        self.min_bars_spin.setValue(0)
        self.max_bars_spin.setValue(9999)
        
        self.current_filters = {}
        self.load_trades()
    
    def load_trades(self):
        """Load trades from database with current filters"""
        trades = self.db_manager.get_trades(self.current_filters)
        
        self.trades_table.setRowCount(0)  # Clear table
        
        for row_idx, trade in enumerate(trades):
            self.trades_table.insertRow(row_idx)
            
            # Date
            date_item = QTableWidgetItem(trade.get('date', ''))
            date_item.setData(Qt.ItemDataRole.UserRole, trade.get('id'))
            self.trades_table.setItem(row_idx, 0, date_item)
            
            # Time
            self.trades_table.setItem(row_idx, 1, QTableWidgetItem(trade.get('time', '')))
            
            # Instrument
            self.trades_table.setItem(row_idx, 2, QTableWidgetItem(trade.get('instrument', '')))
            
            # Action
            action_item = QTableWidgetItem(trade.get('action', ''))
            # Set background color based on action
            if 'buy' in trade.get('action', '').lower():
                action_item.setBackground(QColor(200, 255, 200))  # Light green
            elif 'sell' in trade.get('action', '').lower():
                action_item.setBackground(QColor(255, 200, 200))  # Light red
            self.trades_table.setItem(row_idx, 3, action_item)
            
            # Quantity
            self.trades_table.setItem(row_idx, 4, QTableWidgetItem(str(trade.get('quantity', ''))))
            
            # Price
            self.trades_table.setItem(row_idx, 5, QTableWidgetItem(str(trade.get('price', ''))))
            
            # Commission
            self.trades_table.setItem(row_idx, 6, QTableWidgetItem(str(trade.get('commission', ''))))
            
            # MAE
            self.trades_table.setItem(row_idx, 7, QTableWidgetItem(str(trade.get('mae', ''))))
            
            # MFE
            self.trades_table.setItem(row_idx, 8, QTableWidgetItem(str(trade.get('mfe', ''))))
            
            # Bars
            self.trades_table.setItem(row_idx, 9, QTableWidgetItem(str(trade.get('bars', ''))))
            
            # Entry Strategy
            entry_strategy_item = QTableWidgetItem(trade.get('entry_strategy', ''))
            entry_strategy_item.setFlags(entry_strategy_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.trades_table.setItem(row_idx, 10, entry_strategy_item)
            
            # Photo - Add a button or indicator if photos exist
            images = self.db_manager.get_trade_images(trade.get('id'))
            photo_text = f"{len(images)} image(s)" if images else "Add Photo"
            photo_item = QTableWidgetItem(photo_text)
            photo_item.setData(Qt.ItemDataRole.UserRole, trade.get('id'))
            self.trades_table.setItem(row_idx, 11, photo_item)
    
    def cell_double_clicked(self, row, column):
        """Handle double click on table cell"""
        if column == 11:  # Photo column
            trade_id = self.trades_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self.handle_photo_click(trade_id)
    
    def handle_photo_click(self, trade_id):
        """Handle click on photo cell"""
        # Check if trade already has photos
        existing_images = self.db_manager.get_trade_images(trade_id)
        
        if existing_images:
            # Show existing images
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Trade Images")
            dialog.resize(800, 600)
            
            layout = QVBoxLayout(dialog)
            
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            
            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            
            for img_path in existing_images:
                img_label = QLabel()
                pixmap = load_image_as_pixmap(img_path, 750)
                if not pixmap.isNull():
                    img_label.setPixmap(pixmap)
                    scroll_layout.addWidget(img_label)
                else:
                    scroll_layout.addWidget(QLabel(f"Unable to load image: {img_path}"))
            
            # Add an "Add More" button
            add_button = QPushButton("Add More Images")
            add_button.clicked.connect(lambda: self.add_new_photos(trade_id, dialog))
            scroll_layout.addWidget(add_button)
            
            scroll_area.setWidget(scroll_content)
            layout.addWidget(scroll_area)
            
            dialog.exec()
        else:
            # Add new photos
            self.add_new_photos(trade_id)
    
    def add_new_photos(self, trade_id, parent_dialog=None):
        """Add new photos to a trade"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if not file_paths:
            return
            
        # Save images and paths to database
        saved_paths = []
        for path in file_paths:
            saved_path = save_image(path, trade_id)
            if saved_path:
                saved_paths.append(saved_path)
        
        if saved_paths:
            success, message = self.db_manager.save_trade_images(trade_id, saved_paths)
            
            if success:
                show_message(self, "Images Saved", f"{len(saved_paths)} images saved successfully.")
                
                # Refresh trade list to update photo count
                self.load_trades()
                
                # Close parent dialog if it exists (to refresh)
                if parent_dialog:
                    parent_dialog.accept()
            else:
                show_message(self, "Error", message, QMessageBox.Icon.Critical)
    
    def get_current_filters(self):
        """Get current filters for use by other tabs"""
        return self.current_filters 