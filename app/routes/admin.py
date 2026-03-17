from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Restaurant, Order, Category, FoodType

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin only.', 'danger')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return login_required(wrapper)

@bp.route('/dashboard')
@admin_required
def dashboard():
    users_count = User.query.filter_by(role='customer').count()
    restaurants_count = Restaurant.query.count()
    orders_count = Order.query.count()
    return render_template('admin/dashboard.html', 
                           users_count=users_count, 
                           restaurants_count=restaurants_count, 
                           orders_count=orders_count)

@bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            new_cat = Category(name=name)
            db.session.add(new_cat)
            db.session.commit()
            flash('Category added.', 'success')
        return redirect(url_for('admin.categories'))
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@bp.route('/categories/delete/<int:id>', methods=['POST'])
@admin_required
def delete_category(id):
    cat = Category.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    flash('Category deleted.', 'success')
    return redirect(url_for('admin.categories'))

@bp.route('/food-types', methods=['GET', 'POST'])
@admin_required
def food_types():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            new_ft = FoodType(name=name)
            db.session.add(new_ft)
            db.session.commit()
            flash('Food Type added.', 'success')
        return redirect(url_for('admin.food_types'))
    food_types = FoodType.query.all()
    return render_template('admin/food_types.html', food_types=food_types)

@bp.route('/food-types/delete/<int:id>', methods=['POST'])
@admin_required
def delete_food_type(id):
    ft = FoodType.query.get_or_404(id)
    db.session.delete(ft)
    db.session.commit()
    flash('Food Type deleted.', 'success')
    return redirect(url_for('admin.food_types'))

@bp.route('/reports/customers')
@admin_required
def customers_report():
    customers = User.query.filter_by(role='customer').all()
    return render_template('admin/customers.html', customers=customers)

@bp.route('/reports/restaurants')
@admin_required
def restaurants_report():
    restaurants = Restaurant.query.all()
    return render_template('admin/restaurants.html', restaurants=restaurants)

@bp.route('/orders')
@admin_required
def all_orders():
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('admin/orders.html', orders=orders)