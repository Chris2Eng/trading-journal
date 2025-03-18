import pandas as pd
import os
from datetime import datetime

class CSVImporter:
    """Class for importing CSV trade data"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        
    def validate_csv(self):
        """Validate CSV file format"""
        if not os.path.exists(self.file_path):
            return False, "File does not exist"
            
        if not self.file_path.lower().endswith('.csv'):
            return False, "File is not a CSV file"
            
        try:
            # Try to read CSV file
            df = pd.read_csv(self.file_path)
            
            # Check for required columns based on NinjaTrader format
            # We're flexible with the exact format to support different CSV layouts
            required_columns = ['Instrument']
            
            # Check if we have either Entry time or Date/Time
            time_columns = ['Entry time', 'Date/Time']
            has_time_column = any(col in df.columns for col in time_columns)
            
            # Check if we have market position or action
            action_columns = ['Market pos.', 'Action']
            has_action_column = any(col in df.columns for col in action_columns)
            
            # Check if we have quantity
            qty_columns = ['Qty', 'Quantity']
            has_qty_column = any(col in df.columns for col in qty_columns)
            
            # Check if we have price
            price_columns = ['Entry price', 'Price']
            has_price_column = any(col in df.columns for col in price_columns)
            
            # Combine all required checks
            if 'Instrument' not in df.columns:
                return False, "Missing required column: Instrument"
                
            if not has_time_column:
                return False, "Missing required column: Entry time or Date/Time"
                
            if not has_action_column:
                return False, "Missing required column: Market pos. or Action"
                
            if not has_qty_column:
                return False, "Missing required column: Qty or Quantity"
                
            if not has_price_column:
                return False, "Missing required column: Entry price or Price"
                
            return True, "CSV file is valid"
        except Exception as e:
            return False, f"Error reading CSV file: {str(e)}"
            
    def read_csv(self):
        """Read CSV file and return DataFrame"""
        try:
            df = pd.read_csv(self.file_path)
            return True, df
        except Exception as e:
            return False, f"Error reading CSV file: {str(e)}"
            
    def map_columns(self, df):
        """Map NinjaTrader CSV columns to database fields"""
        # Create a new DataFrame with the mapped columns
        mapped_df = pd.DataFrame()
        
        # Map Instrument
        if 'Instrument' in df.columns:
            mapped_df['instrument'] = df['Instrument']
        
        # Map Date and Time
        if 'Entry time' in df.columns:
            # Split Entry time into date and time parts
            entry_times = pd.to_datetime(df['Entry time'], errors='coerce')
            mapped_df['date'] = entry_times.dt.strftime('%Y-%m-%d')
            mapped_df['time'] = entry_times.dt.strftime('%H:%M:%S')
        elif 'Date/Time' in df.columns:
            # Split Date/Time into date and time parts
            date_times = pd.to_datetime(df['Date/Time'], errors='coerce')
            mapped_df['date'] = date_times.dt.strftime('%Y-%m-%d')
            mapped_df['time'] = date_times.dt.strftime('%H:%M:%S')
        
        # Map Action
        if 'Market pos.' in df.columns:
            # Convert Market pos. to Action (Long -> Buy, Short -> Sell)
            mapped_df['action'] = df['Market pos.'].apply(lambda x: 'Buy' if x == 'Long' else 'Sell' if x == 'Short' else x)
        elif 'Action' in df.columns:
            mapped_df['action'] = df['Action']
        
        # Map Quantity
        if 'Qty' in df.columns:
            mapped_df['quantity'] = df['Qty']
        elif 'Quantity' in df.columns:
            mapped_df['quantity'] = df['Quantity']
        
        # Map Price
        if 'Entry price' in df.columns:
            mapped_df['price'] = df['Entry price']
        elif 'Price' in df.columns:
            mapped_df['price'] = df['Price']
        
        # Map Commission
        if 'Commission' in df.columns:
            # Remove any $ signs and convert to float
            mapped_df['commission'] = df['Commission'].apply(lambda x: str(x).replace('$', '').replace(',', '') if isinstance(x, str) else x)
        else:
            mapped_df['commission'] = 0.0
        
        # Map MAE
        if 'MAE' in df.columns:
            # Remove any $ signs and convert to float
            mapped_df['mae'] = df['MAE'].apply(lambda x: str(x).replace('$', '').replace(',', '') if isinstance(x, str) else x)
        else:
            mapped_df['mae'] = 0.0
        
        # Map MFE
        if 'MFE' in df.columns:
            # Remove any $ signs and convert to float
            mapped_df['mfe'] = df['MFE'].apply(lambda x: str(x).replace('$', '').replace(',', '') if isinstance(x, str) else x)
        else:
            mapped_df['mfe'] = 0.0
        
        # Map Bars
        if 'Bars' in df.columns:
            mapped_df['bars'] = df['Bars']
        else:
            mapped_df['bars'] = 0
        
        # Entry Strategy and Notes (empty by default, user will fill in)
        mapped_df['entry_strategy'] = ''
        
        if 'Strategy' in df.columns:
            mapped_df['entry_strategy'] = df['Strategy']
            
        mapped_df['notes'] = ''
        
        return mapped_df 