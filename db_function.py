
import sqlite3

def user():
    conn = sqlite3.connect('milk_collection_system.db')
    cur = conn.cursor()
    
    # Create the User table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS USER (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userName TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()  
    conn.close() 
    return "success"


def farmer():
    conn = sqlite3.connect('milk_collection_system.db')
    cur = conn.cursor()
    
    # Create the Farmer table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS FARMER (
            farmer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmerName TEXT NOT NULL,
            contactInfo TEXT NOT NULL
        )
    ''')

    conn.commit()  
    conn.close() 
    return "success"


def milk_collection():
    conn = sqlite3.connect('milk_collection_system.db')
    cur = conn.cursor()
    
    # Create the Milk Collection table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS MILKCOLLECTION (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmerId INTEGER NOT NULL,
            quantity REAL NOT NULL,          
            reading REAL NOT NULL,           
            pricePerLiter REAL NOT NULL,     
            totalAmount REAL NOT NULL,       
            date DATE DEFAULT CURRENT_DATE,  
            FOREIGN KEY (farmerId) REFERENCES FARMER(farmer_id)
        )
    ''')

    conn.commit()  
    conn.close() 
    return "success"
