from flask import Flask, render_template  # <-- add render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    # Register blueprints
    from app.routes import auth, customer, owner, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(customer.bp)
    app.register_blueprint(owner.bp)
    app.register_blueprint(admin.bp)

    # --- ADD THIS HOME ROUTE ---
    @app.route('/')
    def index():
        return render_template('index.html')  # or just return a string for now
    # ---------------------------

    # Create tables (for development)
    with app.app_context():
        db.create_all()

    return app