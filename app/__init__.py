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
        from app.models import Category, Dish, Review
        categories = Category.query.all()
        popular_dishes = Dish.query.limit(8).all()
        active_reviews = Review.query.order_by(Review.id.desc()).limit(5).all()
        return render_template('index.html', 
                             categories=categories, 
                             popular_dishes=popular_dishes,
                             active_reviews=active_reviews)

    # Render Uptime Cron Route
    @app.route('/ping')
    def ping():
        return "pong", 200

    # Create tables and auto-seed on first boot
    with app.app_context():
        db.create_all()
        _auto_seed()

    return app


def _auto_seed():
    """Seed the database with initial data only if it is empty (first deployment)."""
    from app.models import User, Category, FoodType, Restaurant, Dish
    from werkzeug.security import generate_password_hash
    import logging
    log = logging.getLogger(__name__)

    # Only run if there are no categories (fresh database)
    if Category.query.first():
        return

    log.info("Empty database detected – running auto-seed...")

    # --- Categories ---
    for name in ["Biryani", "Burger", "Chicken", "Pizza", "Kebab",
                 "Chinese", "Desserts", "Drinks", "Salads", "Sandwiches",
                 "Sushi", "Seafood", "Pasta", "Breakfast", "Vegan"]:
        db.session.add(Category(name=name))

    # --- Food Types ---
    for name in ["Veg", "Non-Veg", "Vegan", "Gluten-Free", "Halal", "Kosher"]:
        db.session.add(FoodType(name=name, is_approved=True))

    # --- Admin User ---
    if not User.query.filter_by(email="admin@regfood.com").first():
        db.session.add(User(
            name="RegFood Admin", email="admin@regfood.com",
            password_hash=generate_password_hash("Admin@12345"),
            role='admin', phone='+1000000000', address='RegFood HQ'
        ))

    # --- Demo Owner ---
    owner = User(
        name="RegFood Kitchen", email="owner@regfood.com",
        password_hash=generate_password_hash("Owner@12345"),
        role='owner', phone='+1000000001', address='123 Food Street'
    )
    db.session.add(owner)
    db.session.flush()  # get the owner.id

    # --- Demo Restaurant ---
    restaurant = Restaurant(
        owner_id=owner.id, name="RegFood Kitchen",
        address="123 Food Street, City Centre", contact="+1000000001",
        description="The flagship RegFood restaurant serving delicious meals.",
        logo_url="/static/regfood/images/breadcrumb_bg.jpg"
    )
    db.session.add(restaurant)
    db.session.flush()  # get the restaurant.id

    # --- Demo Customer ---
    db.session.add(User(
        name="RegFood Customer", email="customer@regfood.com",
        password_hash=generate_password_hash("Customer@12345"),
        role='customer', phone='+1000000002', address='456 Maple Avenue'
    ))

    db.session.flush()

    # --- Demo Dishes ---
    biryani = Category.query.filter_by(name="Biryani").first()
    burger  = Category.query.filter_by(name="Burger").first()
    chicken = Category.query.filter_by(name="Chicken").first()
    nonveg  = FoodType.query.filter_by(name="Non-Veg").first()
    veg     = FoodType.query.filter_by(name="Veg").first()

    for name, price, cat, ftype, desc in [
        ("Hyderabadi Biryani", 12.99, biryani, nonveg,
         "Authentic slow-cooked biryani with tender lamb and aromatic spices."),
        ("Chicken Nuggets", 8.99, chicken, nonveg,
         "Crispy golden chicken nuggets served with dipping sauce."),
        ("Spicy Burger", 9.99, burger, nonveg,
         "A juicy double-stacked spicy beef burger with jalapeños."),
        ("Fried Chicken", 10.99, chicken, nonveg,
         "Southern-style crispy fried chicken, golden perfection."),
        ("Mozzarella Sticks", 6.99, chicken, veg,
         "Gooey mozzarella wrapped in a crispy golden crust."),
        ("Popcorn Chicken", 7.99, chicken, nonveg,
         "Bite-sized popcorn chicken, perfectly seasoned."),
    ]:
        db.session.add(Dish(
            restaurant_id=restaurant.id, name=name, price=price,
            description=desc, category=cat, food_type=ftype,
            image_url="/static/regfood/images/menu2_img_1.jpg",
            is_available=True
        ))

    db.session.commit()
    log.info("Auto-seed complete. Admin: admin@regfood.com / Admin@12345")