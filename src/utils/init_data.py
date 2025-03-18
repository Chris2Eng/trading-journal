def init_default_instruments(db_manager):
    """Initialize the database with default instruments and multipliers"""
    default_instruments = [
        ("ES", 50.0),  # E-mini S&P 500
        ("NQ", 20.0),  # E-mini NASDAQ-100
        ("YM", 5.0),   # E-mini Dow
        ("RTY", 5.0),  # E-mini Russell 2000
        ("CL", 1000.0), # Crude Oil
        ("GC", 100.0), # Gold
        ("SI", 5000.0), # Silver
        ("ZB", 1000.0), # 30-year Treasury Bonds
        ("ZN", 1000.0), # 10-year Treasury Notes
        ("6E", 125000.0), # Euro FX
        ("6J", 12500000.0), # Japanese Yen
        ("6B", 62500.0), # British Pound
        ("6C", 100000.0), # Canadian Dollar
        ("ZC", 50.0),  # Corn
        ("ZS", 50.0),  # Soybeans
        ("ZW", 50.0),  # Wheat
    ]
    
    for name, multiplier in default_instruments:
        db_manager.ensure_instrument_exists(name, multiplier)
        
    return True 