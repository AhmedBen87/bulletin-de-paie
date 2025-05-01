import sqlite3
import os

def create_direct_db():
    print("Creating database directly with SQLite...")
    
    # Path to the instance directory
    instance_dir = "instance"
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
        print(f"Created instance directory: {instance_dir}")
    
    # Database file path
    db_file = os.path.join(instance_dir, "salary_calculator.db")
    
    # Delete database if it exists
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"Deleted existing database file: {db_file}")
        except Exception as e:
            print(f"Failed to delete database: {e}")
            return
    
    # Create database and required tables
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create user_profile table
    cursor.execute('''
    CREATE TABLE user_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        hourly_rate FLOAT NOT NULL,
        function_bonus_base_amount FLOAT DEFAULT 0,
        performance_bonus_amount FLOAT DEFAULT 0,
        prime_de_niveau_amount FLOAT DEFAULT 0,
        seniority_rate_percent FLOAT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create calculation_history table
    cursor.execute('''
    CREATE TABLE calculation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id INTEGER NOT NULL,
        calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        input_data TEXT,
        result_data TEXT,
        gross_salary FLOAT,
        net_salary FLOAT,
        FOREIGN KEY (profile_id) REFERENCES user_profile (id)
    )
    ''')
    
    conn.commit()
    
    # Verify tables were created correctly
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables created: {tables}")
    
    # Verify user_profile columns
    cursor.execute("PRAGMA table_info(user_profile);")
    columns = cursor.fetchall()
    print("user_profile columns:")
    for col in columns:
        print(f"  {col}")
    
    conn.close()
    print("Database creation completed successfully")

if __name__ == "__main__":
    create_direct_db()
    print("Script execution completed. Database should now be created.") 