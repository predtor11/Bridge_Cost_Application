import sqlite3

# Connect to SQLite database (creates file if it doesn't exist)
conn = sqlite3.connect("bridge_costs.db")
cursor = conn.cursor()

# Create table for bridge cost data
cursor.execute("""
CREATE TABLE IF NOT EXISTS bridge_costs (
    `Material` TEXT PRIMARY KEY,
    `Base Rate (₹/m²)` REAL,
    `Maintenance Rate (₹/m²/year)` REAL,
    `Repair Rate (₹/m²)` REAL,
    `Demolition Rate (₹/m²)` REAL,
    `Environmental Factor (₹/m²)` REAL,
    `Social Factor (₹/vehicle/year)` REAL,
    `Delay Factor (₹/vehicle/year)` REAL
)
""")

# Insert sample data for Steel and Concrete
cursor.executemany("""
INSERT OR REPLACE INTO bridge_costs (`Material`, `Base Rate (₹/m²)`, `Maintenance Rate (₹/m²/year)`, `Repair Rate (₹/m²)`, 
                                     `Demolition Rate (₹/m²)`, `Environmental Factor (₹/m²)`, `Social Factor (₹/vehicle/year)`, `Delay Factor (₹/vehicle/year)`)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", [
    ('Steel', 3000, 50, 200, 100, 10, 0.5, 0.3),
    ('Concrete', 2500, 75, 150, 80, 8, 0.6, 0.2)
])

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database created and populated successfully!")
