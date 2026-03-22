from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    role = db.Column(db.String(20), default='customer')
    profile_image = db.Column(db.String(255)) # Cloudinary URL
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    contact = db.Column(db.String(20))
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(255)) # Cloudinary URL
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    owner = db.relationship('User', backref='restaurants')

class RestaurantMedia(db.Model):
    __tablename__ = 'restaurant_media'
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    media_type = db.Column(db.String(20), nullable=False) # 'menu', 'video'
    url = db.Column(db.String(255), nullable=False)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    restaurant = db.relationship('Restaurant', backref='media')

class Coupon(db.Model):
    __tablename__ = 'coupons'
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    discount_type = db.Column(db.String(20), nullable=False) # 'percent' or 'fixed'
    discount_value = db.Column(db.Numeric(10,2), nullable=False)
    valid_until = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    restaurant = db.relationship('Restaurant', backref='coupons')
    __table_args__ = (db.UniqueConstraint('restaurant_id', 'code', name='unique_coupon_code_per_restaurant'),)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class FoodType(db.Model):
    __tablename__ = 'food_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    is_approved = db.Column(db.Boolean, default=True)
    requested_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    requested_by = db.relationship('User', foreign_keys=[requested_by_id])

class Dish(db.Model):
    __tablename__ = 'dishes'
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    food_type_id = db.Column(db.Integer, db.ForeignKey('food_types.id'))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10,2), nullable=False)
    image_url = db.Column(db.String(255)) # Cloudinary URL
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    restaurant = db.relationship('Restaurant', backref='dishes')
    category = db.relationship('Category')
    food_type = db.relationship('FoodType')

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    total_amount = db.Column(db.Numeric(10,2), nullable=False)
    status = db.Column(db.String(20), default='pending')
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_time = db.Column(db.DateTime)
    payment_method = db.Column(db.String(20), default='cash')
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=True)
    discount_amount = db.Column(db.Numeric(10,2), default=0)
    customer = db.relationship('User', foreign_keys=[customer_id], backref='orders')
    restaurant = db.relationship('Restaurant', backref='orders')
    coupon = db.relationship('Coupon')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False) # price at order time
    order = db.relationship('Order', backref='items')
    dish = db.relationship('Dish')

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    rating = db.Column(db.Integer) # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    customer = db.relationship('User', foreign_keys=[customer_id], backref='reviews')
    __table_args__ = (db.UniqueConstraint('customer_id', 'restaurant_id', name='unique_customer_restaurant'),)
class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='wishlists')
    dish = db.relationship('Dish', backref='wishlisted_by')


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))