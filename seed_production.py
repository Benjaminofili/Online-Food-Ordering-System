"""
RegFood Production Seed Script
================================
Run this once via Render Shell to initialize the live production database.

Usage (in Render Shell):
    python seed_production.py
"""

from app import create_app, db
from app.models import User, Category, FoodType, Restaurant, Dish
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():

    # ─── 1. ADMIN USER ────────────────────────────────────────────────────────
    ADMIN_EMAIL    = "admin@regfood.com"
    ADMIN_PASSWORD = "Admin@12345"   # ← CHANGE THIS after first login!
    ADMIN_NAME     = "RegFood Admin"

    if not User.query.filter_by(email=ADMIN_EMAIL).first():
        admin = User(
            name=ADMIN_NAME,
            email=ADMIN_EMAIL,
            password_hash=generate_password_hash(ADMIN_PASSWORD),
            role='admin',
            phone='+1000000000',
            address='RegFood HQ'
        )
        db.session.add(admin)
        print(f"✅ Admin created → {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    else:
        print(f"⚠️  Admin already exists: {ADMIN_EMAIL}")

    # ─── 2. CATEGORIES ────────────────────────────────────────────────────────
    categories = [
        "Biryani", "Burger", "Chicken", "Pizza",
        "Kebab", "Chinese", "Desserts", "Drinks",
        "Salads", "Sandwiches", "Sushi", "Seafood",
        "Pasta", "Breakfast", "Vegan"
    ]
    cat_count = 0
    for name in categories:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
            cat_count += 1
    print(f"✅ {cat_count} categories added.")

    # ─── 3. FOOD TYPES ────────────────────────────────────────────────────────
    food_types = ["Veg", "Non-Veg", "Vegan", "Gluten-Free", "Halal", "Kosher"]
    ft_count = 0
    for name in food_types:
        if not FoodType.query.filter_by(name=name).first():
            db.session.add(FoodType(name=name, is_approved=True))
            ft_count += 1
    print(f"✅ {ft_count} food types added.")

    # ─── 4. DEMO OWNER + RESTAURANT ───────────────────────────────────────────
    OWNER_EMAIL    = "owner@regfood.com"
    OWNER_PASSWORD = "Owner@12345"   # ← Change after testing!

    owner = User.query.filter_by(email=OWNER_EMAIL).first()
    if not owner:
        owner = User(
            name="RegFood Kitchen",
            email=OWNER_EMAIL,
            password_hash=generate_password_hash(OWNER_PASSWORD),
            role='owner',
            phone='+1000000001',
            address='123 Food Street'
        )
        db.session.add(owner)
        db.session.flush()  # get the ID before commit
        print(f"✅ Demo owner created → {OWNER_EMAIL} / {OWNER_PASSWORD}")
    else:
        print(f"⚠️  Demo owner already exists: {OWNER_EMAIL}")

    restaurant = Restaurant.query.filter_by(owner_id=owner.id).first()
    if not restaurant:
        restaurant = Restaurant(
            owner_id=owner.id,
            name="RegFood Kitchen",
            address="123 Food Street, City Centre",
            contact="+1000000001",
            description="The flagship RegFood restaurant serving delicious meals around the clock.",
            logo_url="/static/regfood/images/breadcrumb_bg.jpg"
        )
        db.session.add(restaurant)
        db.session.flush()
        print(f"✅ Demo restaurant created: RegFood Kitchen")
    else:
        print(f"⚠️  Demo restaurant already exists.")

    # ─── 5. DEMO DISHES ───────────────────────────────────────────────────────
    biryani_cat  = Category.query.filter_by(name="Biryani").first()
    burger_cat   = Category.query.filter_by(name="Burger").first()
    chicken_cat  = Category.query.filter_by(name="Chicken").first()
    dessert_cat  = Category.query.filter_by(name="Desserts").first()
    nonveg_type  = FoodType.query.filter_by(name="Non-Veg").first()
    veg_type     = FoodType.query.filter_by(name="Veg").first()

    sample_dishes = [
        dict(name="Hyderabadi Biryani",  price=12.99, category=biryani_cat,  food_type=nonveg_type,
             description="Authentic slow-cooked biryani with tender lamb and aromatic spices.",
             image_url="/static/regfood/images/menu2_img_1.jpg"),
        dict(name="Chicken Nuggets",     price=8.99,  category=chicken_cat, food_type=nonveg_type,
             description="Crispy golden chicken nuggets served with dipping sauce.",
             image_url="/static/regfood/images/menu2_img_1.jpg"),
        dict(name="Spicy Burger",        price=9.99,  category=burger_cat,  food_type=nonveg_type,
             description="A juicy double-stacked spicy beef burger with jalapeños.",
             image_url="/static/regfood/images/menu2_img_1.jpg"),
        dict(name="Fried Chicken",       price=10.99, category=chicken_cat, food_type=nonveg_type,
             description="Southern-style crispy fried chicken, golden perfection.",
             image_url="/static/regfood/images/menu2_img_1.jpg"),
        dict(name="Mozzarella Sticks",   price=6.99,  category=dessert_cat, food_type=veg_type,
             description="Gooey mozzarella wrapped in a crispy golden crust.",
             image_url="/static/regfood/images/menu2_img_1.jpg"),
        dict(name="Popcorn Chicken",     price=7.99,  category=chicken_cat, food_type=nonveg_type,
             description="Bite-sized popcorn chicken, perfectly seasoned.",
             image_url="/static/regfood/images/menu2_img_1.jpg"),
    ]

    dish_count = 0
    for d in sample_dishes:
        if not Dish.query.filter_by(name=d["name"], restaurant_id=restaurant.id).first():
            db.session.add(Dish(
                restaurant_id=restaurant.id,
                name=d["name"],
                price=d["price"],
                description=d["description"],
                image_url=d["image_url"],
                category=d["category"],
                food_type=d["food_type"],
                is_available=True
            ))
            dish_count += 1
    print(f"✅ {dish_count} demo dishes added.")

    # ─── 6. DEMO CUSTOMER ─────────────────────────────────────────────────────
    CUST_EMAIL    = "customer@regfood.com"
    CUST_PASSWORD = "Customer@12345"
    if not User.query.filter_by(email=CUST_EMAIL).first():
        db.session.add(User(
            name="RegFood Customer",
            email=CUST_EMAIL,
            password_hash=generate_password_hash(CUST_PASSWORD),
            role='customer',
            phone='+1000000002',
            address='456 Maple Avenue'
        ))
        print(f"✅ Demo customer created → {CUST_EMAIL} / {CUST_PASSWORD}")
    else:
        print(f"⚠️  Demo customer already exists: {CUST_EMAIL}")

    # ─── COMMIT ───────────────────────────────────────────────────────────────
    db.session.commit()
    print("\n🎉 Database seeded successfully! RegFood is ready.")
    print("\n📋 Login Credentials:")
    print(f"   Admin    → {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print(f"   Owner    → {OWNER_EMAIL} / {OWNER_PASSWORD}")
    print(f"   Customer → {CUST_EMAIL} / {CUST_PASSWORD}")
    print("\n⚠️  IMPORTANT: Change these passwords immediately after first login!")
