import sqlite3

conn = sqlite3.connect('subway_store.db')
cursor = conn.cursor()

sql_query = """

CREATE TABLE IF NOT EXISTS subway (
    outlet_name VARCHAR(60),
    address VARCHAR(100),
    opening_hours VARCHAR(60),
    waze_link VARCHAR(200),
    gmaps_link VARCHAR(200),
    latitude REAL,
    longitude REAL
)
"""

cursor.execute(sql_query)
conn.commit()
conn.close()
