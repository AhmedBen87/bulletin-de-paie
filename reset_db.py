import os
import sqlite3
import shutil
from app import app, db

def reset_database():
    print("Starting database reset...")
    
    # Get the instance path
    instance_path = app.instance_path
    print(f"Instance path: {instance_path}")
    
    # Create instance directory if it doesn't exist
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        print(f"Created instance directory: {instance_path}")
    
    # Database file path
    db_file = os.path.join(instance_path, 'salary_calculator.db')
    print(f"Database file path: {db_file}")
    
    # Remove the database file if it exists
    if os.path.exists(db_file):
        try:
            # Try to delete the file directly
            os.remove(db_file)
            print(f"Successfully deleted {db_file}")
        except PermissionError:
            print(f"Permission error when trying to delete {db_file}")
            # If permission error (file in use), try renaming
            try:
                backup_file = db_file + ".bak"
                shutil.move(db_file, backup_file)
                print(f"Renamed {db_file} to {backup_file}")
            except Exception as e:
                print(f"Failed to rename file: {e}")
    else:
        print(f"Database file {db_file} not found")
    
    # Create database with all tables
    with app.app_context():
        print("Creating all tables...")
        db.create_all()
        print("Tables created successfully")
    
    # Verify database has been created with correct schema
    print("Verifying database schema...")
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in database: {tables}")
        
        # Check user_profile table schema
        cursor.execute("PRAGMA table_info(user_profile);")
        columns = cursor.fetchall()
        print("user_profile columns:")
        for col in columns:
            print(f"  {col}")
        
        conn.close()
        print("Database verification completed")
    except Exception as e:
        print(f"Error verifying database: {e}")

if __name__ == "__main__":
    reset_database()
    print("Database reset complete.") 