from flask import Flask
from flask_migrate import Migrate, MigrateCommand, init, migrate, upgrade
from app import create_app, db
import os

app = create_app()
migrate = Migrate(app, db)

def init_migrations():
    """Initialize migrations directory structure."""
    with app.app_context():
        init()

def create_migration(message="Migration"):
    """Create a new migration."""
    with app.app_context():
        migrate(message=message)

def apply_migrations():
    """Apply all pending migrations."""
    with app.app_context():
        upgrade()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migrations.py [init|migrate|upgrade]")
        print("  init    - Initialize migrations directory")
        print("  migrate - Create a new migration")
        print("  upgrade - Apply migrations")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'init':
        init_migrations()
        print("Migrations directory initialized.")
    elif command == 'migrate':
        message = sys.argv[2] if len(sys.argv) > 2 else "Migration"
        create_migration(message)
        print(f"Migration created with message: {message}")
    elif command == 'upgrade':
        apply_migrations()
        print("Migrations applied.")
    else:
        print(f"Unknown command: {command}")
        print("Available commands: init, migrate, upgrade")
        sys.exit(1) 