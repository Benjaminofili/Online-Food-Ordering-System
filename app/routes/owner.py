from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models import Restaurant, Dish, Order, Category, FoodType
from app.utils import upload_image_to_cloudinary

bp = Blueprint('owner', __name__, url_prefix='/owner')

def owner_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'owner':
            flash('Access denied. Restaurant Owner only.', 'danger')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return login_required(wrapper)

def get_restaurant():
    # Helper to get the current owner's restaurant
    return Restaurant.query.filter_by(owner_id=current_user.id).first()

@bp.route('/dashboard')
@owner_required
def dashboard():
    restaurant = get_restaurant()
    if not restaurant:
        flash('Please set up your restaurant profile first.', 'warning')
        return redirect(url_for('owner.profile'))
    
    dishes_count = Dish.query.filter_by(restaurant_id=restaurant.id).count()
    recent_orders = Order.query.filter_by(restaurant_id=restaurant.id).order_by(Order.order_date.desc()).limit(5).all()
    
    return render_template('owner/dashboard.html', restaurant=restaurant, dishes_count=dishes_count, recent_orders=recent_orders)

@bp.route('/profile', methods=['GET', 'POST'])
@owner_required
def profile():
    restaurant = get_restaurant()
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        contact = request.form.get('contact')
        description = request.form.get('description')
        
        # Handle file upload for logo
        logo_file = request.files.get('logo')
        logo_url = None
        if logo_file and logo_file.filename != '':
            logo_url = upload_image_to_cloudinary(logo_file)
        
        if not restaurant:
            restaurant = Restaurant(owner_id=current_user.id)
            db.session.add(restaurant)
            
        restaurant.name = name
        restaurant.address = address
        restaurant.contact = contact
        restaurant.description = description
        if logo_url:
            restaurant.logo_url = logo_url
        
        db.session.commit()
        flash('Restaurant profile updated.', 'success')
        return redirect(url_for('owner.dashboard'))
        
    return render_template('owner/profile.html', restaurant=restaurant)

@bp.route('/dishes')
@owner_required
def dishes():
    restaurant = get_restaurant()
    if not restaurant:
        return redirect(url_for('owner.profile'))
    dishes = Dish.query.filter_by(restaurant_id=restaurant.id).all()
    return render_template('owner/dishes.html', dishes=dishes)

@bp.route('/dishes/add', methods=['GET', 'POST'])
@owner_required
def add_dish():
    restaurant = get_restaurant()
    if not restaurant:
        return redirect(url_for('owner.profile'))
        
    categories = Category.query.all()
    food_types = FoodType.query.all()
    
    if request.method == 'POST':
        image_file = request.files.get('image')
        image_url = None
        if image_file and image_file.filename != '':
            image_url = upload_image_to_cloudinary(image_file)
            
        dish = Dish(
            restaurant_id=restaurant.id,
            category_id=request.form.get('category_id'),
            food_type_id=request.form.get('food_type_id'),
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=request.form.get('price'),
            image_url=image_url,
            is_available=request.form.get('is_available') == 'on'
        )
        db.session.add(dish)
        db.session.commit()
        flash('Dish added.', 'success')
        return redirect(url_for('owner.dishes'))
        
    return render_template('owner/dish_form.html', categories=categories, food_types=food_types, dish=None)

@bp.route('/dishes/edit/<int:id>', methods=['GET', 'POST'])
@owner_required
def edit_dish(id):
    restaurant = get_restaurant()
    dish = Dish.query.get_or_404(id)
    if dish.restaurant_id != restaurant.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('owner.dishes'))
        
    categories = Category.query.all()
    food_types = FoodType.query.all()
    
    if request.method == 'POST':
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            image_url = upload_image_to_cloudinary(image_file)
            if image_url:
                dish.image_url = image_url
                
        dish.category_id = request.form.get('category_id')
        dish.food_type_id = request.form.get('food_type_id')
        dish.name = request.form.get('name')
        dish.description = request.form.get('description')
        dish.price = request.form.get('price')
        dish.is_available = request.form.get('is_available') == 'on'
        
        db.session.commit()
        flash('Dish updated.', 'success')
        return redirect(url_for('owner.dishes'))
        
    return render_template('owner/dish_form.html', categories=categories, food_types=food_types, dish=dish)

@bp.route('/dishes/delete/<int:id>', methods=['POST'])
@owner_required
def delete_dish(id):
    restaurant = get_restaurant()
    dish = Dish.query.get_or_404(id)
    if dish.restaurant_id == restaurant.id:
        db.session.delete(dish)
        db.session.commit()
        flash('Dish deleted.', 'success')
    return redirect(url_for('owner.dishes'))

@bp.route('/orders')
@owner_required
def orders():
    restaurant = get_restaurant()
    if not restaurant:
        return redirect(url_for('owner.profile'))
    orders = Order.query.filter_by(restaurant_id=restaurant.id).order_by(Order.order_date.desc()).all()
    return render_template('owner/orders.html', orders=orders)

@bp.route('/orders/update/<int:id>', methods=['POST'])
@owner_required
def update_order(id):
    restaurant = get_restaurant()
    order = Order.query.get_or_404(id)
    if order.restaurant_id == restaurant.id:
        order.status = request.form.get('status')
        db.session.commit()
        flash('Order status updated.', 'success')
    return redirect(url_for('owner.orders'))