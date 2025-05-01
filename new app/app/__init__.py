from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config=None):
    app = Flask(__name__)
    
    # Load default configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_for_dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bulletin_de_paie.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Override default configuration if provided
    if config:
        app.config.from_object(config)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Set login view for login_required decorator
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    
    # Set up user loader function
    from app.models import User
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.profiles import bp as profiles_bp
    app.register_blueprint(profiles_bp, url_prefix='/profiles')
    
    from app.calculator import bp as calculator_bp
    app.register_blueprint(calculator_bp, url_prefix='/calculator')
    
    from app.history import bp as history_bp
    app.register_blueprint(history_bp, url_prefix='/history')
    
    # Register custom template filters
    from app.utils import parse_json
    app.jinja_env.filters['fromjson'] = parse_json
    
    # Add current year to all templates
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Initialize database within the app context
    with app.app_context():
        if not os.path.exists(os.path.join(app.instance_path)):
            os.makedirs(os.path.join(app.instance_path))
        
        # Import models to ensure they're registered with SQLAlchemy
        from app import models
    
    return app 