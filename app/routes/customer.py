from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from flask_login import login_required, current_user
from app import db
from app import db
from app.models import Restaurant, Dish, Order, OrderItem, Review, Coupon
from datetime import datetime

bp = Blueprint('customer', __name__, url_prefix='/customer')

def customer_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'customer':
            flash('Access denied. Customer only.', 'danger')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return login_required(wrapper)

@bp.route('/dashboard')
@customer_required
def dashboard():
    query = request.args.get('q')
    if query:
        restaurants = Restaurant.query.filter(Restaurant.name.ilike(f'%{query}%') | Restaurant.address.ilike(f'%{query}%')).all()
    else:
        restaurants = Restaurant.query.all()
    return render_template('customer/dashboard.html', restaurants=restaurants, query=query)

@bp.route('/restaurant/<int:id>')
@customer_required
def restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    dishes = Dish.query.filter_by(restaurant_id=restaurant.id, is_available=True).all()
    reviews = Review.query.filter_by(restaurant_id=restaurant.id).order_by(Review.created_at.desc()).all()
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
    return render_template('customer/restaurant.html', restaurant=restaurant, dishes=dishes, reviews=reviews, avg_rating=avg_rating)

@bp.route('/cart')
@customer_required
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for dish_id_str, qty in cart.items():
        dish = Dish.query.get(int(dish_id_str))
        if dish:
            subtotal = float(dish.price) * qty
            total += subtotal
            cart_items.append({'dish': dish, 'quantity': qty, 'subtotal': subtotal})
    return render_template('customer/cart.html', cart_items=cart_items, total=total)

@bp.route('/cart/add/<int:dish_id>', methods=['POST'])
@customer_required
def add_to_cart(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    cart = session.get('cart', {})
    
    # Store restaurant_id to prevent ordering from multiple restaurants
    current_rest_id = session.get('cart_restaurant_id')
    if current_rest_id and current_rest_id != dish.restaurant_id and len(cart) > 0:
        flash('You can only order from one restaurant at a time. Please clear your cart first.', 'danger')
        return redirect(url_for('customer.restaurant', id=dish.restaurant_id))
        
    session['cart_restaurant_id'] = dish.restaurant_id
    
    dish_id_str = str(dish_id)
    if dish_id_str in cart:
        cart[dish_id_str] += 1
    else:
        cart[dish_id_str] = 1
        
    session['cart'] = cart
    flash(f'{dish.name} added to cart.', 'success')
    return redirect(url_for('customer.restaurant', id=dish.restaurant_id))

@bp.route('/cart/clear', methods=['POST'])
@customer_required
def clear_cart():
    session.pop('cart', None)
    session.pop('cart_restaurant_id', None)
    flash('Cart cleared.', 'success')
    return redirect(url_for('customer.view_cart'))

@bp.route('/cart/update/<int:dish_id>/<action>', methods=['POST'])
@customer_required
def update_cart(dish_id, action):
    cart = session.get('cart', {})
    dish_id_str = str(dish_id)
    if dish_id_str in cart:
        if action == 'increase':
            cart[dish_id_str] += 1
        elif action == 'decrease':
            if cart[dish_id_str] > 1:
                cart[dish_id_str] -= 1
            else:
                del cart[dish_id_str]
        session['cart'] = cart
        if not cart:
            session.pop('cart_restaurant_id', None)
            
    if request.headers.get('Accept') == 'application/json':
        # Return updated JSON
        total = 0.0
        item_qty = 0
        item_subtotal = 0.0
        for did_str, qty in cart.items():
            dish = Dish.query.get(int(did_str))
            if dish:
                total += float(dish.price) * qty
                if str(did_str) == dish_id_str:
                    item_qty = qty
                    item_subtotal = float(dish.price) * qty
        return {'success': True, 'new_qty': item_qty, 'new_subtotal': item_subtotal, 'new_total': total}
        
    return redirect(url_for('customer.view_cart'))

@bp.route('/cart/apply_coupon', methods=['POST'])
@customer_required
def apply_coupon():
    code = request.form.get('code')
    restaurant_id = session.get('cart_restaurant_id')
    
    if not restaurant_id:
        flash('Add items to your cart first.', 'warning')
        return redirect(url_for('customer.view_cart'))
        
    coupon = Coupon.query.filter_by(restaurant_id=restaurant_id, code=code, is_active=True).first()
    
    if not coupon:
        flash('Invalid or inactive promo code.', 'danger')
        return redirect(url_for('customer.view_cart'))
        
    if coupon.valid_until and coupon.valid_until < datetime.now():
        flash('This promo code has expired.', 'danger')
        return redirect(url_for('customer.view_cart'))
        
    session['applied_coupon_id'] = coupon.id
    flash(f'Promo code {code} applied successfully!', 'success')
    return redirect(url_for('customer.view_cart'))

@bp.route('/checkout', methods=['GET', 'POST'])
@customer_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('customer.dashboard'))
        
    restaurant_id = session.get('cart_restaurant_id')
    restaurant = Restaurant.query.get(restaurant_id)
    
    # Calculate total
    total = 0.0
    dishes_in_cart = []
    for dish_id_str, qty in cart.items():
        dish = Dish.query.get(int(dish_id_str))
        if dish:
            total += float(dish.price) * qty
            dishes_in_cart.append((dish, qty))
            
    if request.method == 'POST':
        address = request.form.get('address') or current_user.address
        payment_method = request.form.get('payment_method')
        
        coupon_id = session.get('applied_coupon_id')
        discount_amount = 0.0
        
        if coupon_id:
            coupon = Coupon.query.get(coupon_id)
            if coupon and coupon.is_active and (not coupon.valid_until or coupon.valid_until >= datetime.now()):
                if coupon.discount_type == 'percent':
                    discount_amount = total * (float(coupon.discount_value) / 100.0)
                else:
                    discount_amount = float(coupon.discount_value)
                total = max(0.0, total - discount_amount)
            else:
                coupon_id = None # Coupon invalid

        order = Order(
            customer_id=current_user.id,
            restaurant_id=restaurant_id,
            total_amount=total,
            discount_amount=discount_amount,
            coupon_id=coupon_id,
            status='pending',
            delivery_address=address,
            payment_method=payment_method
        )
        db.session.add(order)
        db.session.flush() # get order.id
        
        for dish, qty in dishes_in_cart:
            item = OrderItem(
                order_id=order.id,
                dish_id=dish.id,
                quantity=qty,
                price=dish.price
            )
            db.session.add(item)
            
        db.session.commit()
        session.pop('cart', None)
        session.pop('cart_restaurant_id', None)
        session.pop('applied_coupon_id', None)
        flash('Order placed successfully!', 'success')
        return redirect(url_for('customer.my_orders'))
        
    # GET Request Logic
    coupon_id = session.get('applied_coupon_id')
    discount_amount = 0.0
    applied_coupon = None
    original_total = total
    
    if coupon_id:
        coupon = Coupon.query.get(coupon_id)
        if coupon and coupon.is_active and (not coupon.valid_until or coupon.valid_until >= datetime.now()):
            applied_coupon = coupon
            if coupon.discount_type == 'percent':
                discount_amount = total * (float(coupon.discount_value) / 100.0)
            else:
                discount_amount = float(coupon.discount_value)
            total = max(0.0, total - discount_amount)
            
    return render_template('customer/checkout.html', total=total, original_total=original_total, discount_amount=discount_amount, applied_coupon=applied_coupon, restaurant=restaurant)

@bp.route('/my-orders')
@customer_required
def my_orders():
    orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('customer/orders.html', orders=orders)

@bp.route('/restaurant/<int:id>/review', methods=['GET', 'POST'])
@customer_required
def leave_review(id):
    restaurant = Restaurant.query.get_or_404(id)
    # Check if they have a delivered order from this restaurant
    has_ordered = Order.query.filter_by(customer_id=current_user.id, restaurant_id=id, status='delivered').first()
    if not has_ordered:
        flash('You can only review restaurants you have received a delivered order from.', 'danger')
        return redirect(url_for('customer.restaurant', id=id))
        
    review = Review.query.filter_by(customer_id=current_user.id, restaurant_id=id).first()
    
    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment')
        
        if review:
            review.rating = rating
            review.comment = comment
            flash('Review updated.', 'success')
        else:
            review = Review(customer_id=current_user.id, restaurant_id=id, rating=rating, comment=comment)
            db.session.add(review)
            flash('Review submitted.', 'success')
            
        db.session.commit()
        return redirect(url_for('customer.restaurant', id=id))
        
    return render_template('customer/review.html', restaurant=restaurant, review=review)

@bp.route('/api/my-active-orders')
@customer_required
def api_active_orders():
    orders = Order.query.filter(
        Order.customer_id == current_user.id,
        Order.status.in_(['pending', 'accepted', 'preparing', 'out for delivery'])
    ).all()
    
    return {'orders': [{
        'id': o.id, 
        'status': o.status,
        'delivery_time': o.delivery_time.strftime('%I:%M %p') if o.delivery_time else None
    } for o in orders]}