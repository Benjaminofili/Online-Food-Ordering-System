from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
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
    
    # Configure Cloudinary
    if app.config.get('CLOUDINARY_URL'):
        cloudinary.config(
            cloudinary_url=app.config.get('CLOUDINARY_URL')
        )
    else:
        app.logger.warning("CLOUDINARY_URL not set in environment!")

    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    # Register blueprints
    from app.routes import auth, customer, owner, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(customer.bp)
    app.register_blueprint(owner.bp)
    app.register_blueprint(admin.bp)

    # --- HOME ROUTE ---
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')

    # Create tables (for development)
    with app.app_context():
        db.create_all()

    return app