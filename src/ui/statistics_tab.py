from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGridLayout, QDateEdit, QPushButton, QGroupBox,
    QTableWidget, QTableWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import numpy as np

class StatisticsTab(QWidget):
    def __init__(self, db_manager, trade_data_tab):
        super().__init__()
        self.db_manager = db_manager
        self.trade_data_tab = trade_data_tab
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Date range selector (top row)
        date_layout = QHBoxLayout()
        
        # Start date section
        start_date_group = QGroupBox("Start Date")
        start_date_layout = QHBoxLayout(start_date_group)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        start_date_layout.addWidget(self.start_date_edit)
        
        # End date section
        end_date_group = QGroupBox("End Date")
        end_date_layout = QHBoxLayout(end_date_group)
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        end_date_layout.addWidget(self.end_date_edit)
        
        date_layout.addWidget(start_date_group)
        date_layout.addWidget(end_date_group)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_statistics)
        date_layout.addWidget(refresh_button)
        
        date_layout.addStretch()
        
        main_layout.addLayout(date_layout)
        
        # Main content area (middle section with 2 rows)
        content_layout = QHBoxLayout()
        
        # Stats section (left column)
        self.stats_group = QGroupBox("Stats")
        stats_layout = QGridLayout(self.stats_group)
        
        # Create statistics labels
        # Row 1
        stats_layout.addWidget(QLabel("Net Gain/Loss:"), 0, 0)
        self.net_profit_label = QLabel("$0.00")
        stats_layout.addWidget(self.net_profit_label, 0, 1)
        
        # Row 2
        stats_layout.addWidget(QLabel("Total Commissions:"), 1, 0)
        self.total_commission_label = QLabel("$0.00")
        stats_layout.addWidget(self.total_commission_label, 1, 1)
        
        # Row 3
        stats_layout.addWidget(QLabel("% Win:"), 2, 0)
        self.win_rate_label = QLabel("0%")
        stats_layout.addWidget(self.win_rate_label, 2, 1)
        
        # Row 4
        stats_layout.addWidget(QLabel("% Loss:"), 3, 0)
        self.loss_rate_label = QLabel("0%")
        stats_layout.addWidget(self.loss_rate_label, 3, 1)
        
        # Row 5
        stats_layout.addWidget(QLabel("% Break Even:"), 4, 0)
        self.break_even_rate_label = QLabel("0%")
        stats_layout.addWidget(self.break_even_rate_label, 4, 1)
        
        # Row 6
        stats_layout.addWidget(QLabel("Average daily gain/loss:"), 5, 0)
        self.avg_daily_pnl_label = QLabel("$0.00")
        stats_layout.addWidget(self.avg_daily_pnl_label, 5, 1)
        
        # Row 7
        stats_layout.addWidget(QLabel("Average winning trade:"), 6, 0)
        self.avg_winner_label = QLabel("$0.00")
        stats_layout.addWidget(self.avg_winner_label, 6, 1)
        
        # Row 8
        stats_layout.addWidget(QLabel("Average losing trade:"), 7, 0)
        self.avg_loser_label = QLabel("$0.00")
        stats_layout.addWidget(self.avg_loser_label, 7, 1)
        
        # Row 9
        stats_layout.addWidget(QLabel("Total number of trades:"), 8, 0)
        self.total_trades_label = QLabel("0")
        stats_layout.addWidget(self.total_trades_label, 8, 1)
        
        # Row 10
        stats_layout.addWidget(QLabel("Number of winning trades:"), 9, 0)
        self.winning_trades_label = QLabel("0")
        stats_layout.addWidget(self.winning_trades_label, 9, 1)
        
        # Row 11
        stats_layout.addWidget(QLabel("Number of losing trades:"), 10, 0)
        self.losing_trades_label = QLabel("0")
        stats_layout.addWidget(self.losing_trades_label, 10, 1)
        
        # Row 12
        stats_layout.addWidget(QLabel("Number of break even trades:"), 11, 0)
        self.break_even_trades_label = QLabel("0")
        stats_layout.addWidget(self.break_even_trades_label, 11, 1)
        
        # Row 13
        stats_layout.addWidget(QLabel("Max consecutive wins:"), 12, 0)
        self.max_cons_wins_label = QLabel("0")
        stats_layout.addWidget(self.max_cons_wins_label, 12, 1)
        
        # Row 14
        stats_layout.addWidget(QLabel("Max consecutive losses:"), 13, 0)
        self.max_cons_losses_label = QLabel("0")
        stats_layout.addWidget(self.max_cons_losses_label, 13, 1)
        
        # Row 15
        stats_layout.addWidget(QLabel("Largest gain:"), 14, 0)
        self.largest_winner_label = QLabel("$0.00")
        stats_layout.addWidget(self.largest_winner_label, 14, 1)
        
        # Row 16
        stats_layout.addWidget(QLabel("Largest loss:"), 15, 0)
        self.largest_loser_label = QLabel("$0.00")
        stats_layout.addWidget(self.largest_loser_label, 15, 1)
        
        # Row 17
        stats_layout.addWidget(QLabel("Average trade gain/loss:"), 16, 0)
        self.avg_trade_pnl_label = QLabel("$0.00")
        stats_layout.addWidget(self.avg_trade_pnl_label, 16, 1)
        
        # Row 18
        stats_layout.addWidget(QLabel("Average hold time (winning trades):"), 17, 0)
        self.avg_hold_win_label = QLabel("0")
        stats_layout.addWidget(self.avg_hold_win_label, 17, 1)
        
        # Row 19
        stats_layout.addWidget(QLabel("Average hold time (losing trades):"), 18, 0)
        self.avg_hold_loss_label = QLabel("0")
        stats_layout.addWidget(self.avg_hold_loss_label, 18, 1)
        
        # Row 20
        stats_layout.addWidget(QLabel("Max drawdown:"), 19, 0)
        self.max_drawdown_label = QLabel("$0.00")
        stats_layout.addWidget(self.max_drawdown_label, 19, 1)
        
        # Row 21
        stats_layout.addWidget(QLabel("Average position MFE:"), 20, 0)
        self.avg_mfe_label = QLabel("$0.00")
        stats_layout.addWidget(self.avg_mfe_label, 20, 1)
        
        # Row 22
        stats_layout.addWidget(QLabel("Average position MAE:"), 21, 0)
        self.avg_mae_label = QLabel("$0.00")
        stats_layout.addWidget(self.avg_mae_label, 21, 1)
        
        content_layout.addWidget(self.stats_group, 1)
        
        # Right side charts (2x2 grid)
        charts_layout = QVBoxLayout()
        
        # Top row charts
        top_charts_layout = QHBoxLayout()
        
        # Profit & Loss chart
        self.pnl_group = QGroupBox("Profit & Loss")
        pnl_layout = QVBoxLayout(self.pnl_group)
        self.pnl_figure = Figure(figsize=(4, 3), dpi=100)
        self.pnl_canvas = FigureCanvas(self.pnl_figure)
        pnl_layout.addWidget(self.pnl_canvas)
        top_charts_layout.addWidget(self.pnl_group)
        
        # Scatter Plot chart
        self.scatter_group = QGroupBox("Scatter Plot")
        scatter_layout = QVBoxLayout(self.scatter_group)
        self.scatter_figure = Figure(figsize=(4, 3), dpi=100)
        self.scatter_canvas = FigureCanvas(self.scatter_figure)
        scatter_layout.addWidget(self.scatter_canvas)
        top_charts_layout.addWidget(self.scatter_group)
        
        charts_layout.addLayout(top_charts_layout)
        
        # Bottom row charts
        bottom_charts_layout = QHBoxLayout()
        
        # MFE chart
        self.mfe_group = QGroupBox("MFE")
        mfe_layout = QVBoxLayout(self.mfe_group)
        self.mfe_figure = Figure(figsize=(4, 3), dpi=100)
        self.mfe_canvas = FigureCanvas(self.mfe_figure)
        mfe_layout.addWidget(self.mfe_canvas)
        bottom_charts_layout.addWidget(self.mfe_group)
        
        # MAE chart
        self.mae_group = QGroupBox("MAE")
        mae_layout = QVBoxLayout(self.mae_group)
        self.mae_figure = Figure(figsize=(4, 3), dpi=100)
        self.mae_canvas = FigureCanvas(self.mae_figure)
        mae_layout.addWidget(self.mae_canvas)
        bottom_charts_layout.addWidget(self.mae_group)
        
        charts_layout.addLayout(bottom_charts_layout)
        
        content_layout.addLayout(charts_layout, 2)
        
        main_layout.addLayout(content_layout)
        
        # Daily statistics table (bottom section)
        self.daily_stats_group = QGroupBox("Daily Statistics")
        daily_stats_layout = QVBoxLayout(self.daily_stats_group)
        
        self.daily_stats_table = QTableWidget()
        self.daily_stats_table.setColumnCount(4)
        self.daily_stats_table.setHorizontalHeaderLabels(["% Win", "Average P&L", "Total P&L (net)", ""])
        self.daily_stats_table.setRowCount(5)
        self.daily_stats_table.setVerticalHeaderLabels(["Mon", "Tue", "Wed", "Thu", "Fri"])
        daily_stats_layout.addWidget(self.daily_stats_table)
        
        main_layout.addWidget(self.daily_stats_group)
        
        # Initialize with empty data
        self.refresh_statistics()
    
    def prepare_filters_from_data_tab(self):
        """Prepare filters based on the trade data tab's current filters"""
        data_tab_filters = self.trade_data_tab.get_current_filters()
        
        if 'start_date' in data_tab_filters and data_tab_filters['start_date']:
            self.start_date_edit.setDate(QDate.fromString(data_tab_filters['start_date'], "yyyy-MM-dd"))
            
        if 'end_date' in data_tab_filters and data_tab_filters['end_date']:
            self.end_date_edit.setDate(QDate.fromString(data_tab_filters['end_date'], "yyyy-MM-dd"))
            
        self.refresh_statistics()
    
    def refresh_statistics(self):
        """Calculate and display statistics"""
        filters = {
            'start_date': self.start_date_edit.date().toString("yyyy-MM-dd"),
            'end_date': self.end_date_edit.date().toString("yyyy-MM-dd")
        }
        
        # Merge with data tab filters (except dates which we control here)
        data_tab_filters = self.trade_data_tab.get_current_filters()
        for key, value in data_tab_filters.items():
            if key not in ['start_date', 'end_date'] and value is not None:
                filters[key] = value
        
        # Get trades for the selected period
        trades = self.db_manager.get_trades(filters)
        
        # Calculate statistics for these trades
        stats = self.calculate_extended_statistics(trades)
        
        # Update statistics labels
        self.update_stats_display(stats)
        
        # Generate and display graphs
        self.update_charts(trades, stats)
        
        # Update daily statistics
        self.update_daily_statistics(trades)
    
    def calculate_extended_statistics(self, trades):
        """Calculate detailed statistics for the trades"""
        if not trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "break_even_trades": 0,
                "win_rate": 0,
                "loss_rate": 0,
                "break_even_rate": 0,
                "net_profit": 0,
                "total_commission": 0,
                "avg_daily_pnl": 0,
                "avg_winner": 0,
                "avg_loser": 0,
                "largest_winner": 0,
                "largest_loser": 0,
                "avg_trade_pnl": 0,
                "max_consecutive_wins": 0,
                "max_consecutive_losses": 0,
                "avg_hold_time_winners": 0,
                "avg_hold_time_losers": 0,
                "max_drawdown": 0,
                "avg_mfe": 0,
                "avg_mae": 0
            }
        
        # Calculate P&L for each trade
        for trade in trades:
            # For demo - in real app you'd match buys with sells
            quantity = trade.get('quantity', 0)
            price = trade.get('price', 0)
            commission = float(trade.get('commission', 0))
            multiplier = trade.get('multiplier', 1)
            action = trade.get('action', '').lower()
            
            # Simple P&L calculation (for demo purposes)
            pnl = (quantity * price * multiplier) * (1 if 'buy' in action else -1) - commission
            trade['pnl'] = pnl
        
        # Initialize statistics
        stats = {
            "total_trades": len(trades),
            "winning_trades": sum(1 for t in trades if t['pnl'] > 0),
            "losing_trades": sum(1 for t in trades if t['pnl'] < 0),
            "break_even_trades": sum(1 for t in trades if t['pnl'] == 0),
            "total_commission": sum(float(t.get('commission', 0)) for t in trades),
            "net_profit": sum(t['pnl'] for t in trades),
            "total_profit": sum(t['pnl'] for t in trades if t['pnl'] > 0),
            "total_loss": sum(abs(t['pnl']) for t in trades if t['pnl'] < 0),
            "largest_winner": max((t['pnl'] for t in trades if t['pnl'] > 0), default=0),
            "largest_loser": max((abs(t['pnl']) for t in trades if t['pnl'] < 0), default=0),
            "avg_mfe": sum(float(t.get('mfe', 0)) for t in trades) / len(trades) if trades else 0,
            "avg_mae": sum(float(t.get('mae', 0)) for t in trades) / len(trades) if trades else 0
        }
        
        # Calculate percentages
        stats["win_rate"] = (stats["winning_trades"] / stats["total_trades"]) * 100 if stats["total_trades"] > 0 else 0
        stats["loss_rate"] = (stats["losing_trades"] / stats["total_trades"]) * 100 if stats["total_trades"] > 0 else 0
        stats["break_even_rate"] = (stats["break_even_trades"] / stats["total_trades"]) * 100 if stats["total_trades"] > 0 else 0
        
        # Calculate average values
        stats["avg_winner"] = stats["total_profit"] / stats["winning_trades"] if stats["winning_trades"] > 0 else 0
        stats["avg_loser"] = stats["total_loss"] / stats["losing_trades"] if stats["losing_trades"] > 0 else 0
        stats["avg_trade_pnl"] = stats["net_profit"] / stats["total_trades"] if stats["total_trades"] > 0 else 0
        
        # Calculate consecutive wins/losses
        if trades:
            current_streak = 1
            max_win_streak = 0
            max_loss_streak = 0
            
            sorted_trades = sorted(trades, key=lambda x: (x['date'], x['time']))
            
            for i in range(1, len(sorted_trades)):
                if (sorted_trades[i]['pnl'] > 0 and sorted_trades[i-1]['pnl'] > 0) or \
                   (sorted_trades[i]['pnl'] < 0 and sorted_trades[i-1]['pnl'] < 0):
                    current_streak += 1
                else:
                    current_streak = 1
                
                if sorted_trades[i]['pnl'] > 0:
                    max_win_streak = max(max_win_streak, current_streak)
                elif sorted_trades[i]['pnl'] < 0:
                    max_loss_streak = max(max_loss_streak, current_streak)
            
            stats["max_consecutive_wins"] = max_win_streak
            stats["max_consecutive_losses"] = max_loss_streak
        else:
            stats["max_consecutive_wins"] = 0
            stats["max_consecutive_losses"] = 0
        
        # Calculate daily P&L average
        if trades:
            # Group trades by date
            trades_by_date = {}
            for trade in trades:
                date = trade['date']
                if date not in trades_by_date:
                    trades_by_date[date] = []
                trades_by_date[date].append(trade)
            
            # Calculate daily P&L
            daily_pnl = [sum(t['pnl'] for t in day_trades) for day_trades in trades_by_date.values()]
            stats["avg_daily_pnl"] = sum(daily_pnl) / len(daily_pnl) if daily_pnl else 0
        else:
            stats["avg_daily_pnl"] = 0
        
        # Calculate max drawdown (simplified)
        if trades:
            sorted_trades = sorted(trades, key=lambda x: (x['date'], x['time']))
            cumulative_pnl = [0]
            
            for trade in sorted_trades:
                cumulative_pnl.append(cumulative_pnl[-1] + trade['pnl'])
            
            peak = max(cumulative_pnl)
            drawdowns = [peak - val for val in cumulative_pnl]
            stats["max_drawdown"] = max(drawdowns)
        else:
            stats["max_drawdown"] = 0
        
        # Calculate average hold times (using bars as a proxy for now)
        # In a real app you'd calculate this from entry/exit times
        stats["avg_hold_time_winners"] = sum(int(t.get('bars', 0)) for t in trades if t['pnl'] > 0) / max(stats["winning_trades"], 1)
        stats["avg_hold_time_losers"] = sum(int(t.get('bars', 0)) for t in trades if t['pnl'] < 0) / max(stats["losing_trades"], 1)
        
        return stats
    
    def update_stats_display(self, stats):
        """Update the statistics display labels"""
        self.total_trades_label.setText(str(stats["total_trades"]))
        self.winning_trades_label.setText(str(stats["winning_trades"]))
        self.losing_trades_label.setText(str(stats["losing_trades"]))
        self.break_even_trades_label.setText(str(stats["break_even_trades"]))
        
        self.win_rate_label.setText(f"{stats['win_rate']:.2f}%")
        self.loss_rate_label.setText(f"{stats['loss_rate']:.2f}%")
        self.break_even_rate_label.setText(f"{stats['break_even_rate']:.2f}%")
        
        self.net_profit_label.setText(f"${stats['net_profit']:.2f}")
        self.total_commission_label.setText(f"${stats['total_commission']:.2f}")
        self.avg_daily_pnl_label.setText(f"${stats['avg_daily_pnl']:.2f}")
        
        self.avg_winner_label.setText(f"${stats['avg_winner']:.2f}")
        self.avg_loser_label.setText(f"${stats['avg_loser']:.2f}")
        self.avg_trade_pnl_label.setText(f"${stats['avg_trade_pnl']:.2f}")
        
        self.largest_winner_label.setText(f"${stats['largest_winner']:.2f}")
        self.largest_loser_label.setText(f"${stats['largest_loser']:.2f}")
        
        self.max_cons_wins_label.setText(str(stats["max_consecutive_wins"]))
        self.max_cons_losses_label.setText(str(stats["max_consecutive_losses"]))
        
        self.avg_hold_win_label.setText(f"{stats['avg_hold_time_winners']:.2f}")
        self.avg_hold_loss_label.setText(f"{stats['avg_hold_time_losers']:.2f}")
        
        self.max_drawdown_label.setText(f"${stats['max_drawdown']:.2f}")
        self.avg_mfe_label.setText(f"${stats['avg_mfe']:.2f}")
        self.avg_mae_label.setText(f"${stats['avg_mae']:.2f}")
    
    def update_charts(self, trades, stats):
        """Update all charts based on trade data"""
        # Clear all figures
        self.pnl_figure.clear()
        self.scatter_figure.clear()
        self.mfe_figure.clear()
        self.mae_figure.clear()
        
        if not trades:
            # No trades to display
            for fig in [self.pnl_figure, self.scatter_figure, self.mfe_figure, self.mae_figure]:
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, "No trades in the selected date range", 
                       ha='center', va='center', fontsize=9)
                ax.axis('off')
        else:
            # Sort trades by date/time for proper ordering
            sorted_trades = sorted(trades, key=lambda x: (x['date'], x['time']))
            
            # Prepare data for charts
            trade_numbers = list(range(1, len(sorted_trades) + 1))
            pnl_values = [t['pnl'] for t in sorted_trades]
            cumulative_pnl = np.cumsum(pnl_values)
            
            mfe_values = [float(t.get('mfe', 0)) for t in sorted_trades]
            mae_values = [float(t.get('mae', 0)) for t in sorted_trades]
            
            # 1. P&L Chart (Equity Curve)
            ax1 = self.pnl_figure.add_subplot(111)
            ax1.plot(trade_numbers, cumulative_pnl, marker='o', markersize=3, color='blue')
            ax1.set_xlabel('Trade Number')
            ax1.set_ylabel('P&L')
            ax1.grid(True, linestyle='--', alpha=0.6)
            
            # 2. Scatter Plot
            ax2 = self.scatter_figure.add_subplot(111)
            colors = ['green' if pnl > 0 else 'red' for pnl in pnl_values]
            ax2.scatter(trade_numbers, pnl_values, c=colors, s=25)
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax2.set_xlabel('Trade Number')
            ax2.set_ylabel('P&L')
            ax2.grid(True, linestyle='--', alpha=0.6)
            
            # 3. MFE Chart
            ax3 = self.mfe_figure.add_subplot(111)
            ax3.plot(trade_numbers, mfe_values, marker='o', markersize=3, color='green')
            ax3.set_xlabel('Trade Number')
            ax3.set_ylabel('MFE')
            ax3.grid(True, linestyle='--', alpha=0.6)
            
            # 4. MAE Chart
            ax4 = self.mae_figure.add_subplot(111)
            ax4.plot(trade_numbers, mae_values, marker='o', markersize=3, color='red')
            ax4.set_xlabel('Trade Number')
            ax4.set_ylabel('MAE')
            ax4.grid(True, linestyle='--', alpha=0.6)
        
        # Redraw all canvases
        self.pnl_canvas.draw()
        self.scatter_canvas.draw()
        self.mfe_canvas.draw()
        self.mae_canvas.draw()
    
    def update_daily_statistics(self, trades):
        """Update the daily statistics table"""
        # Clear the table first
        for row in range(5):  # Monday to Friday
            for col in range(4):
                self.daily_stats_table.setItem(row, col, QTableWidgetItem(""))
        
        if not trades:
            return
        
        # Group trades by day of week
        days_of_week = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri"}
        trades_by_day = {day: [] for day in range(5)}  # 0-4 = Mon-Fri
        
        for trade in trades:
            try:
                date = datetime.strptime(trade['date'], '%Y-%m-%d')
                day_of_week = date.weekday()
                if day_of_week < 5:  # Only Monday to Friday
                    trades_by_day[day_of_week].append(trade)
            except (ValueError, TypeError):
                # Skip trades with invalid dates
                continue
        
        # Calculate statistics for each day
        for day_idx, day_trades in trades_by_day.items():
            if not day_trades:
                continue
                
            # Calculate win rate
            wins = sum(1 for t in day_trades if t['pnl'] > 0)
            win_rate = (wins / len(day_trades)) * 100 if day_trades else 0
            
            # Calculate average P&L
            avg_pnl = sum(t['pnl'] for t in day_trades) / len(day_trades) if day_trades else 0
            
            # Calculate total P&L
            total_pnl = sum(t['pnl'] for t in day_trades)
            
            # Add to table
            self.daily_stats_table.setItem(day_idx, 0, QTableWidgetItem(f"{win_rate:.1f}%"))
            self.daily_stats_table.setItem(day_idx, 1, QTableWidgetItem(f"${avg_pnl:.2f}"))
            self.daily_stats_table.setItem(day_idx, 2, QTableWidgetItem(f"${total_pnl:.2f}"))
            
            # Color code based on P&L
            text_color = QColor(0, 150, 0) if total_pnl > 0 else QColor(200, 0, 0) if total_pnl < 0 else QColor(0, 0, 0)
            for col in range(3):
                item = self.daily_stats_table.item(day_idx, col)
                if item:
                    item.setForeground(text_color) 