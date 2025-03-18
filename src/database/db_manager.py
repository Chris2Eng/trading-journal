import sqlite3
import os
import pandas as pd
from datetime import datetime
from src.utils.csv_importer import CSVImporter

class DatabaseManager:
    def __init__(self, db_path="trading_journal.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        
    def connect(self):
        """Establish connection to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            
    def setup_database(self):
        """Create necessary tables if they don't exist"""
        # Create Instruments table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS instruments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            multiplier REAL NOT NULL
        )
        ''')
        
        # Create Trades table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            instrument TEXT NOT NULL,
            action TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            commission REAL,
            mae REAL,
            mfe REAL,
            bars INTEGER,
            entry_strategy TEXT,
            notes TEXT,
            FOREIGN KEY (instrument) REFERENCES instruments(name)
        )
        ''')
        
        # Create Images table for storing photos related to trades
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            FOREIGN KEY (trade_id) REFERENCES trades(id)
        )
        ''')
        
        # Create Daily Debrief table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_debrief (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            intraday_summary TEXT,
            feelings TEXT,
            recurring_patterns TEXT,
            best_play_out TEXT,
            leverage_info TEXT
        )
        ''')
        
        # Save changes
        self.conn.commit()
        
    def import_trades(self, csv_path):
        """Import trades from CSV file"""
        try:
            # Use the CSVImporter to read and map the file
            importer = CSVImporter(csv_path)
            valid, message = importer.validate_csv()
            
            if not valid:
                return False, message
                
            success, df = importer.read_csv()
            
            if not success:
                return False, df  # df contains error message in this case
                
            # Map CSV columns to our database structure
            mapped_df = importer.map_columns(df)
            
            # Process data and insert into database
            for _, row in mapped_df.iterrows():
                # Extract instrument name and ensure it exists
                instrument = row.get('instrument', '')
                self.ensure_instrument_exists(instrument)
                
                # Insert trade data
                self.cursor.execute('''
                INSERT INTO trades (
                    date, time, instrument, action, quantity, price,
                    commission, mae, mfe, bars, entry_strategy, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('date', ''),
                    row.get('time', ''),
                    instrument,
                    row.get('action', ''),
                    row.get('quantity', 0),
                    row.get('price', 0.0),
                    row.get('commission', 0.0),
                    row.get('mae', 0.0),
                    row.get('mfe', 0.0),
                    row.get('bars', 0),
                    row.get('entry_strategy', ''),
                    row.get('notes', '')
                ))
            
            # Commit changes
            self.conn.commit()
            return True, f"Successfully imported {len(mapped_df)} trades from {os.path.basename(csv_path)}"
        except Exception as e:
            self.conn.rollback()
            return False, f"Error importing trades: {str(e)}"
    
    def ensure_instrument_exists(self, instrument_name, default_multiplier=1.0):
        """Make sure the instrument exists in the database"""
        if not instrument_name:
            return
        
        self.cursor.execute("SELECT name FROM instruments WHERE name = ?", (instrument_name,))
        result = self.cursor.fetchone()
        
        if not result:
            self.cursor.execute(
                "INSERT INTO instruments (name, multiplier) VALUES (?, ?)",
                (instrument_name, default_multiplier)
            )
            self.conn.commit()
    
    def get_trades(self, filters=None):
        """Get trades with optional filters"""
        query = """
        SELECT t.*, i.multiplier 
        FROM trades t
        JOIN instruments i ON t.instrument = i.name
        """
        
        parameters = []
        
        if filters:
            conditions = []
            
            if 'start_date' in filters and filters['start_date']:
                conditions.append("t.date >= ?")
                parameters.append(filters['start_date'])
                
            if 'end_date' in filters and filters['end_date']:
                conditions.append("t.date <= ?")
                parameters.append(filters['end_date'])
                
            if 'instrument' in filters and filters['instrument']:
                conditions.append("t.instrument = ?")
                parameters.append(filters['instrument'])
                
            if 'action' in filters and filters['action']:
                conditions.append("t.action = ?")
                parameters.append(filters['action'])
                
            if 'entry_strategy' in filters and filters['entry_strategy']:
                conditions.append("t.entry_strategy = ?")
                parameters.append(filters['entry_strategy'])
                
            if 'min_bars' in filters and filters['min_bars'] is not None:
                conditions.append("t.bars >= ?")
                parameters.append(filters['min_bars'])
                
            if 'max_bars' in filters and filters['max_bars'] is not None:
                conditions.append("t.bars <= ?")
                parameters.append(filters['max_bars'])
                
            if 'start_time' in filters and filters['start_time']:
                conditions.append("t.time >= ?")
                parameters.append(filters['start_time'])
                
            if 'end_time' in filters and filters['end_time']:
                conditions.append("t.time <= ?")
                parameters.append(filters['end_time'])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY t.date DESC, t.time DESC"
        
        try:
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
                
            columns = [col[0] for col in self.cursor.description]
            trades = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            return trades
        except Exception as e:
            print(f"Error getting trades: {str(e)}")
            return []
    
    def get_daily_debrief(self, date):
        """Get daily debrief for a specific date"""
        self.cursor.execute(
            "SELECT * FROM daily_debrief WHERE date = ?",
            (date,)
        )
        result = self.cursor.fetchone()
        
        if result:
            columns = [col[0] for col in self.cursor.description]
            return dict(zip(columns, result))
        else:
            return None
    
    def save_daily_debrief(self, date, intraday_summary, feelings, recurring_patterns, best_play_out, leverage_info):
        """Save or update daily debrief"""
        self.cursor.execute(
            "SELECT id FROM daily_debrief WHERE date = ?",
            (date,)
        )
        result = self.cursor.fetchone()
        
        try:
            if result:
                # Update existing record
                self.cursor.execute('''
                UPDATE daily_debrief SET
                    intraday_summary = ?,
                    feelings = ?,
                    recurring_patterns = ?,
                    best_play_out = ?,
                    leverage_info = ?
                WHERE date = ?
                ''', (
                    intraday_summary,
                    feelings,
                    recurring_patterns,
                    best_play_out,
                    leverage_info,
                    date
                ))
            else:
                # Insert new record
                self.cursor.execute('''
                INSERT INTO daily_debrief (
                    date,
                    intraday_summary,
                    feelings,
                    recurring_patterns,
                    best_play_out,
                    leverage_info
                ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    date,
                    intraday_summary,
                    feelings,
                    recurring_patterns,
                    best_play_out,
                    leverage_info
                ))
            
            self.conn.commit()
            return True, "Daily debrief saved successfully"
        except Exception as e:
            self.conn.rollback()
            return False, f"Error saving daily debrief: {str(e)}"
            
    def save_trade_images(self, trade_id, image_paths):
        """Save image paths associated with a trade"""
        try:
            for path in image_paths:
                self.cursor.execute(
                    "INSERT INTO trade_images (trade_id, image_path) VALUES (?, ?)",
                    (trade_id, path)
                )
            
            self.conn.commit()
            return True, "Images saved successfully"
        except Exception as e:
            self.conn.rollback()
            return False, f"Error saving images: {str(e)}"
            
    def get_trade_images(self, trade_id):
        """Get images associated with a trade"""
        self.cursor.execute(
            "SELECT image_path FROM trade_images WHERE trade_id = ?",
            (trade_id,)
        )
        return [row[0] for row in self.cursor.fetchall()]
        
    def get_instruments(self):
        """Get list of all instruments"""
        self.cursor.execute("SELECT name, multiplier FROM instruments ORDER BY name")
        return self.cursor.fetchall()
        
    def update_instrument_multiplier(self, instrument_name, multiplier):
        """Update multiplier for an instrument"""
        try:
            self.cursor.execute(
                "UPDATE instruments SET multiplier = ? WHERE name = ?",
                (multiplier, instrument_name)
            )
            self.conn.commit()
            return True, "Multiplier updated successfully"
        except Exception as e:
            self.conn.rollback()
            return False, f"Error updating multiplier: {str(e)}"
            
    def calculate_statistics(self, filters=None):
        """Calculate trading statistics based on filtered trades"""
        trades = self.get_trades(filters)
        
        if not trades:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "average_winner": 0,
                "average_loser": 0,
                "profit_factor": 0,
                "net_profit": 0,
                "largest_winner": 0,
                "largest_loser": 0,
                "average_mae": 0,
                "average_mfe": 0
            }
        
        # Initialize statistics
        stats = {
            "total_trades": len(trades),
            "winning_trades": 0,
            "losing_trades": 0,
            "break_even_trades": 0,
            "total_profit": 0,
            "total_loss": 0,
            "largest_winner": 0,
            "largest_loser": 0,
            "total_mae": 0,
            "total_mfe": 0
        }
        
        # Calculate statistics
        for trade in trades:
            # Calculate P&L (simplified calculation, adjust based on your actual data format)
            quantity = trade.get('quantity', 0)
            price = trade.get('price', 0)
            commission = trade.get('commission', 0)
            multiplier = trade.get('multiplier', 1)
            action = trade.get('action', '').lower()
            
            # This is a simplification - you'd need to match buys with sells
            # For demonstration, we're just using a random P&L
            # In a real app, you'd need to track opening and closing positions
            
            # Assume P&L is stored or calculated somehow
            # This is just placeholder logic
            pnl = (quantity * price * multiplier) * (1 if 'buy' in action else -1) - commission
            
            if pnl > 0:
                stats["winning_trades"] += 1
                stats["total_profit"] += pnl
                stats["largest_winner"] = max(stats["largest_winner"], pnl)
            elif pnl < 0:
                stats["losing_trades"] += 1
                stats["total_loss"] += abs(pnl)
                stats["largest_loser"] = max(stats["largest_loser"], abs(pnl))
            else:
                stats["break_even_trades"] += 1
            
            stats["total_mae"] += trade.get('mae', 0)
            stats["total_mfe"] += trade.get('mfe', 0)
        
        # Calculate derived statistics
        win_rate = (stats["winning_trades"] / stats["total_trades"]) * 100 if stats["total_trades"] > 0 else 0
        average_winner = stats["total_profit"] / stats["winning_trades"] if stats["winning_trades"] > 0 else 0
        average_loser = stats["total_loss"] / stats["losing_trades"] if stats["losing_trades"] > 0 else 0
        profit_factor = stats["total_profit"] / stats["total_loss"] if stats["total_loss"] > 0 else float('inf')
        net_profit = stats["total_profit"] - stats["total_loss"]
        average_mae = stats["total_mae"] / stats["total_trades"] if stats["total_trades"] > 0 else 0
        average_mfe = stats["total_mfe"] / stats["total_trades"] if stats["total_trades"] > 0 else 0
        
        return {
            "total_trades": stats["total_trades"],
            "win_rate": round(win_rate, 2),
            "average_winner": round(average_winner, 2),
            "average_loser": round(average_loser, 2),
            "profit_factor": round(profit_factor, 2),
            "net_profit": round(net_profit, 2),
            "largest_winner": round(stats["largest_winner"], 2),
            "largest_loser": round(stats["largest_loser"], 2),
            "average_mae": round(average_mae, 2),
            "average_mfe": round(average_mfe, 2)
        }

    def update_trade_entry_strategy(self, trade_id, entry_strategy):
        """Update the entry strategy for a trade"""
        try:
            self.cursor.execute(
                "UPDATE trades SET entry_strategy = ? WHERE id = ?",
                (entry_strategy, trade_id)
            )
            self.conn.commit()
            return True, "Entry strategy updated successfully"
        except Exception as e:
            self.conn.rollback()
            return False, f"Error updating entry strategy: {str(e)}" 