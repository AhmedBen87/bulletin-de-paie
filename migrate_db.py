import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/salary_calculator.db')
cursor = conn.cursor()

# Add the new column to the table
try:
    cursor.execute('ALTER TABLE user_profile ADD COLUMN seniority_rate_percent FLOAT DEFAULT 0')
    print("Successfully added seniority_rate_percent column")
    conn.commit()
except sqlite3.OperationalError as e:
    print(f"Error: {e}")
    # If column already exists, this will fail, but that's fine

# Close the connection
conn.close()

print("Migration completed") 