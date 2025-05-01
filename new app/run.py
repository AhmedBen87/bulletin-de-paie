import os
import click
from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User, UserProfile, CalculationHistory

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Add database models to Flask shell context."""
    return {
        'db': db,
        'User': User,
        'UserProfile': UserProfile,
        'CalculationHistory': CalculationHistory
    }

@app.cli.command("create-admin")
@click.argument("username")
@click.argument("email")
@click.argument("password")
def create_admin(username, email, password):
    """Create an admin user."""
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f"Admin user {username} created!")

@app.cli.command("init-db")
def init_db():
    """Initialize the database with tables."""
    db.create_all()
    click.echo("Database tables created!")

@app.cli.command("reset-db")
@click.confirmation_option(prompt="Are you sure you want to reset the database?")
def reset_db():
    """Reset the database by dropping and recreating all tables."""
    db.drop_all()
    db.create_all()
    click.echo("Database has been reset!")

if __name__ == '__main__':
    app.run(debug=True) 