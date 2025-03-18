import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image
import shutil

def format_date(date_str):
    """Format date string to consistent format"""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        try:
            dt = datetime.strptime(date_str, '%m/%d/%Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return date_str

def is_trading_day(date):
    """Check if date is a trading day (Mon-Fri)"""
    dt = datetime.strptime(date, '%Y-%m-%d')
    # Monday is 0, Sunday is 6
    return dt.weekday() < 5  # 0-4 are weekdays

def get_new_trading_day_start():
    """Get the timestamp when a new trading day starts (3pm)"""
    now = datetime.now()
    # New trading day starts at 3pm (15:00)
    trading_day_start = now.replace(hour=15, minute=0, second=0, microsecond=0)
    return trading_day_start

def get_current_trading_date():
    """Get current trading date considering 3pm day change"""
    now = datetime.now()
    # If it's after 3pm, use today's date
    # If it's before 3pm, use previous day if it's a trading day
    if now.hour < 15:  # Before 3pm
        yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
        if is_trading_day(yesterday):
            return yesterday
    
    # Use today's date (after 3pm or no valid trading day yesterday)
    return now.strftime('%Y-%m-%d')

def save_image(source_path, trade_id, images_dir="static/images"):
    """Save image to application storage and return the path"""
    # Ensure directory exists
    os.makedirs(images_dir, exist_ok=True)
    
    # Create a unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"trade_{trade_id}_{timestamp}{os.path.splitext(source_path)[1]}"
    target_path = os.path.join(images_dir, filename)
    
    # Copy file to target location
    try:
        shutil.copy2(source_path, target_path)
        return target_path
    except Exception as e:
        print(f"Error saving image: {str(e)}")
        return None

def resize_image(image_path, max_width=800, max_height=600):
    """Resize image to fit within maximum dimensions"""
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        # Calculate new dimensions maintaining aspect ratio
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height), Image.LANCZOS)
            img.save(image_path)
        
        return True
    except Exception as e:
        print(f"Error resizing image: {str(e)}")
        return False

def show_message(parent, title, message, icon=QMessageBox.Icon.Information):
    """Show a message dialog"""
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(icon)
    msg_box.exec()

def load_image_as_pixmap(image_path, max_width=None, max_height=None):
    """Load image from path and return as QPixmap with optional resizing"""
    pixmap = QPixmap(image_path)
    
    if not pixmap.isNull() and (max_width or max_height):
        if max_width and max_height:
            pixmap = pixmap.scaled(max_width, max_height, aspectRatioMode=1)  # KeepAspectRatio
        elif max_width:
            pixmap = pixmap.scaledToWidth(max_width, mode=1)  # SmoothTransformation
        elif max_height:
            pixmap = pixmap.scaledToHeight(max_height, mode=1)  # SmoothTransformation
    
    return pixmap

def get_entry_strategy_options():
    """Get list of entry strategies"""
    return [
        "balance-VAH", 
        "balance-VAL", 
        "p-POC", 
        "p-VWAP", 
        "b-POC", 
        "b-VWAP", 
        "PoorHigh", 
        "PoorLow"
    ]

def validate_trade_data(data):
    """Validate trade data"""
    errors = []
    
    # Required fields
    if not data.get('date'):
        errors.append("Date is required")
    
    if not data.get('time'):
        errors.append("Time is required")
    
    if not data.get('instrument'):
        errors.append("Instrument is required")
    
    if not data.get('action'):
        errors.append("Action is required")
    
    try:
        quantity = int(data.get('quantity', 0))
        if quantity <= 0:
            errors.append("Quantity must be a positive number")
    except ValueError:
        errors.append("Quantity must be a valid number")
    
    try:
        price = float(data.get('price', 0))
        if price <= 0:
            errors.append("Price must be a positive number")
    except ValueError:
        errors.append("Price must be a valid number")
    
    return errors 