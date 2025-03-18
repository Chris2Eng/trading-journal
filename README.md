# Trading Journal

A comprehensive application for tracking and analyzing trading activities. This tool helps traders monitor their performance, identify patterns, and improve their trading strategies.

## Features

- Daily Debrief: Track your daily trading thoughts and patterns
- Trade Data Management: Import and filter your trades
- Statistics: Analyze your trading performance with visual charts
- Trade Images: Attach screenshots or images to your trades
- CSV Import: Import trade data from .csv files

## Requirements

- Python 3.7+
- PyQt6
- Pandas
- Matplotlib
- SQLite3
- Pillow

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/trading-journal.git
   cd trading-journal
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Import trade data from CSV files using the "Import CSV" button in the top-right corner.

3. Use the Daily Debrief tab to record your daily trading thoughts and insights.

4. Use the Fields & Data tab to view and filter your trades.

5. Use the Statistics tab to analyze your trading performance.

## CSV Format

The application expects CSV files with the following columns:
- Date/Time
- Instrument
- Action
- Quantity 
- Price
- Commission (optional)
- MAE (optional)
- MFE (optional)
- Bars (optional)
- Entry Strategy (optional)
- Notes (optional)

## Features by Tab

### Daily Debrief Tab
- Record intraday summaries and feelings
- Document recurring patterns and when they best play out
- Track leverage information
- Auto-resets for new trading days (3pm cutoff)

### Fields & Data Tab
- View all trade information in a tabular format
- Filter trades by date, time, instrument, action, entry strategy, and bars
- Attach and view photos/screenshots for each trade

### Statistics Tab
- View key performance metrics including win rate, profit factor, etc.
- Analyze performance with visual charts
- Filter statistics by date range or use the same filters as the data tab

## License

This project is licensed under the MIT License - see the LICENSE file for details. 