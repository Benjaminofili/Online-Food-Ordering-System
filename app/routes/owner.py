from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models import Restaurant, Dish, Order, Category, FoodType, Coupon, OrderItem, RestaurantMedia
from app.utils import upload_file_to_cloudinary
from datetime import datetime, timedelta
from sqlalchemy import func
from spellchecker import SpellChecker

bp = Blueprint('owner', __name__, url_prefix='/owner')

spell = SpellChecker()

def check_dish_spelling(name):
    if not name: return None
    words = [w.strip('.,!?"\'') for w in name.split()]
    misspelled = spell.unknown(words)
    if not misspelled:
        return None
        
    suggestions = []
    for word in misspelled:
        if word and not word.isdigit():
            correction = spell.correction(word)
            if correction and correction != word:
                suggestions.append(f"'{word}' -> '{correction}'")
                
    if suggestions:
        return f"Typo warning: Did you mean {', '.join(suggestions)}?"
    return None

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
    
    # Analytics Metrics
    completed_orders = Order.query.filter(
        Order.restaurant_id == restaurant.id,
        Order.status != 'cancelled'
    ).all()
    total_revenue = sum(float(o.total_amount) for o in completed_orders)
    
    # 7-Day Revenue Trend
    today = datetime.now().date()
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    revenue_by_date = {d: 0.0 for d in dates}
    
    for o in completed_orders:
        if o.order_date:
            o_date = o.order_date.strftime('%Y-%m-%d')
            if o_date in revenue_by_date:
                revenue_by_date[o_date] += float(o.total_amount)
                
    weekly_revenue_labels = list(revenue_by_date.keys())
    weekly_revenue_data = list(revenue_by_date.values())
    
    # Top 5 Dishes
    top_dishes_query = db.session.query(
        Dish.name, func.sum(OrderItem.quantity).label('total_sold')
    ).join(OrderItem).join(Order).filter(
        Order.restaurant_id == restaurant.id,
        Order.status != 'cancelled'
    ).group_by(Dish.id).order_by(func.sum(OrderItem.quantity).desc()).limit(5).all()
    
    top_dishes_labels = [d[0] for d in top_dishes_query]
    top_dishes_data = [d[1] for d in top_dishes_query]
    
    return render_template('owner_dashboard.html', 
        restaurant=restaurant, 
        dishes_count=dishes_count, 
        recent_orders=recent_orders,
        total_revenue=total_revenue,
        weekly_revenue_labels=weekly_revenue_labels,
        weekly_revenue_data=weekly_revenue_data,
        top_dishes_labels=top_dishes_labels,
        top_dishes_data=top_dishes_data
    )

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
            logo_url = upload_file_to_cloudinary(logo_file)
        
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
        
    return render_template('dashboard_info_edit.html', restaurant=restaurant)

@bp.route('/dishes')
@owner_required
def dishes():
    restaurant = get_restaurant()
    if not restaurant:
        return redirect(url_for('owner.profile'))
    dishes = Dish.query.filter_by(restaurant_id=restaurant.id).all()
    return render_template('owner_dishes.html', dishes=dishes)

@bp.route('/dishes/add', methods=['GET', 'POST'])
@owner_required
def add_dish():
    restaurant = get_restaurant()
    if not restaurant:
        return redirect(url_for('owner.profile'))
        
    categories = Category.query.all()
    food_types = FoodType.query.filter(
        db.or_(FoodType.is_approved == True, FoodType.requested_by_id == current_user.id)
    ).all()
    
    if request.method == 'POST':
        image_file = request.files.get('image')
        image_url = None
        if image_file and image_file.filename != '':
            image_url = upload_file_to_cloudinary(image_file)
            
        food_type_id = request.form.get('food_type_id')
        new_food_type_name = request.form.get('new_food_type')
        if new_food_type_name:
            existing = FoodType.query.filter(func.lower(FoodType.name) == new_food_type_name.lower()).first()
            if existing:
                food_type_id = existing.id
            else:
                new_ft = FoodType(name=new_food_type_name, is_approved=False, requested_by_id=current_user.id)
                db.session.add(new_ft)
                db.session.flush()
                food_type_id = new_ft.id
            
        dish = Dish(
            restaurant_id=restaurant.id,
            category_id=request.form.get('category_id'),
            food_type_id=food_type_id,
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=request.form.get('price'),
            image_url=image_url,
            is_available=request.form.get('is_available') == 'on'
        )
        db.session.add(dish)
        db.session.commit()
        
        warning = check_dish_spelling(dish.name)
        if warning:
            flash(warning, 'warning')
            flash('Dish added successfully, but with possible typos.', 'success')
        else:
            flash('Dish added successfully.', 'success')
            
        return redirect(url_for('owner.dishes'))
        
    return render_template('owner_add_edit_dish.html', categories=categories, food_types=food_types, dish=None)

@bp.route('/dishes/edit/<int:id>', methods=['GET', 'POST'])
@owner_required
def edit_dish(id):
    restaurant = get_restaurant()
    dish = db.get_or_404(Dish, id)
    if dish.restaurant_id != restaurant.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('owner.dishes'))
        
    categories = Category.query.all()
    food_types = FoodType.query.filter(
        db.or_(FoodType.is_approved == True, FoodType.requested_by_id == current_user.id)
    ).all()
    
    if request.method == 'POST':
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            image_url = upload_file_to_cloudinary(image_file)
            if image_url:
                dish.image_url = image_url
                
        food_type_id = request.form.get('food_type_id')
        new_food_type_name = request.form.get('new_food_type')
        if new_food_type_name:
            existing = FoodType.query.filter(func.lower(FoodType.name) == new_food_type_name.lower()).first()
            if existing:
                food_type_id = existing.id
            else:
                new_ft = FoodType(name=new_food_type_name, is_approved=False, requested_by_id=current_user.id)
                db.session.add(new_ft)
                db.session.flush()
                food_type_id = new_ft.id

        dish.category_id = request.form.get('category_id')
        dish.food_type_id = food_type_id
        dish.name = request.form.get('name')
        dish.description = request.form.get('description')
        dish.price = request.form.get('price')
        dish.is_available = request.form.get('is_available') == 'on'
        
        db.session.commit()
        
        warning = check_dish_spelling(dish.name)
        if warning:
            flash(warning, 'warning')
            flash('Dish updated successfully, but with possible typos.', 'success')
        else:
            flash('Dish updated successfully.', 'success')
            
        return redirect(url_for('owner.dishes'))
        
    return render_template('owner_add_edit_dish.html', categories=categories, food_types=food_types, dish=dish)

@bp.route('/dishes/delete/<int:id>', methods=['POST'])
@owner_required
def delete_dish(id):
    restaurant = get_restaurant()
    dish = db.get_or_404(Dish, id)
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
    
    status_filter = request.args.get('status')
    query = Order.query.filter_by(restaurant_id=restaurant.id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    restaurant_orders = query.order_by(Order.order_date.desc()).all()
    return render_template('owner_orders.html', orders=restaurant_orders)

@bp.route('/orders/update/<int:id>', methods=['POST'])
@owner_required
def update_order(id):
    restaurant = get_restaurant()
    order = db.get_or_404(Order, id)
    if order.restaurant_id == restaurant.id:
        status = request.form.get('status')
        order.status = status
        
        if status in ['accepted', 'preparing']:
            estimated_time = request.form.get('estimated_time')
            if estimated_time and estimated_time.isdigit():
                from datetime import timedelta
                order.delivery_time = datetime.now() + timedelta(minutes=int(estimated_time))
                
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': True}
            
        flash('Order status updated.', 'success')
    return redirect(url_for('owner.orders'))

@bp.route('/coupons')
@owner_required
def coupons():
    restaurant = get_restaurant()
    if not restaurant:
        flash('Please set up your restaurant profile first.', 'warning')
        return redirect(url_for('owner.profile'))
    coupons = Coupon.query.filter_by(restaurant_id=restaurant.id).all()
    return render_template('owner_coupons.html', coupons=coupons)

@bp.route('/coupons/add', methods=['POST'])
@owner_required
def add_coupon():
    restaurant = get_restaurant()
    code = request.form.get('code')
    discount_type = request.form.get('discount_type')
    discount_value = request.form.get('discount_value')
    valid_until_str = request.form.get('valid_until')
    is_active = request.form.get('is_active') == 'on'

    if Coupon.query.filter_by(restaurant_id=restaurant.id, code=code).first():
        flash('A coupon with this code already exists for your restaurant.', 'danger')
        return redirect(url_for('owner.coupons'))

    valid_until = None
    if valid_until_str:
        valid_until = datetime.fromisoformat(valid_until_str)
        
    coupon = Coupon(
        restaurant_id=restaurant.id,
        code=code,
        discount_type=discount_type,
        discount_value=discount_value,
        valid_until=valid_until,
        is_active=is_active
    )
    db.session.add(coupon)
    db.session.commit()
    flash('Coupon created successfully.', 'success')
    return redirect(url_for('owner.coupons'))

@bp.route('/coupons/delete/<int:id>', methods=['POST'])
@owner_required
def delete_coupon(id):
    restaurant = get_restaurant()
    coupon = db.get_or_404(Coupon, id)
    if coupon.restaurant_id == restaurant.id:
        db.session.delete(coupon)
        db.session.commit()
        flash('Coupon deleted.', 'success')
    return redirect(url_for('owner.coupons'))

@bp.route('/media', methods=['GET', 'POST'])
@owner_required
def media():
    restaurant = get_restaurant()
    if not restaurant:
        flash('Please set up your restaurant profile first.', 'warning')
        return redirect(url_for('owner.profile'))
        
    if request.method == 'POST':
        media_type = request.form.get('media_type') # 'menu_image' or 'video'
        
        url = None
        if media_type == 'menu_image':
            image_file = request.files.get('image')
            if image_file and image_file.filename != '':
                url = upload_file_to_cloudinary(image_file)
        elif media_type == 'video':
            video_file = request.files.get('video_file')
            if video_file and video_file.filename != '':
                # Cloudinary auto-detects video files via resource_type='auto'
                url = upload_file_to_cloudinary(video_file, resource_type="auto")
            else:
                url = request.form.get('video_url')
            
        if url:
            display_order = request.form.get('display_order', 0, type=int)
            new_media = RestaurantMedia(
                restaurant_id=restaurant.id,
                media_type=media_type,
                url=url,
                display_order=display_order
            )
            db.session.add(new_media)
            db.session.commit()
            flash('Media added successfully.', 'success')
        else:
            flash('Failed to add media. Please provide a valid file or URL.', 'danger')
            
        return redirect(url_for('owner.media'))

    menus = RestaurantMedia.query.filter_by(restaurant_id=restaurant.id, media_type='menu_image').order_by(RestaurantMedia.display_order).all()
    videos = RestaurantMedia.query.filter_by(restaurant_id=restaurant.id, media_type='video').order_by(RestaurantMedia.display_order).all()
    
    return render_template('owner_media.html', menus=menus, videos=videos)

@bp.route('/media/delete/<int:id>', methods=['POST'])
@owner_required
def delete_media(id):
    restaurant = get_restaurant()
    media_item = db.get_or_404(RestaurantMedia, id)
    if media_item.restaurant_id == restaurant.id:
        db.session.delete(media_item)
        db.session.commit()
        flash('Media deleted.', 'success')
    return redirect(url_for('owner.media'))

@bp.route('/media/reorder', methods=['POST'])
@owner_required
def reorder_media():
    restaurant = get_restaurant()
    data = request.get_json()
    if data and 'items' in data:
        for item in data['items']:
            media_item = db.session.get(RestaurantMedia, item['id'])
            if media_item and media_item.restaurant_id == restaurant.id:
                media_item.display_order = item['display_order']
        db.session.commit()
        return {'success': True}
    return {'success': False}, 400