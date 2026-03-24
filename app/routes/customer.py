from flask import Blueprint, render_template, flash, redirect, url_for, request, session, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Restaurant, Dish, Order, OrderItem, Review, Coupon, Category, FoodType, Wishlist, RestaurantMedia
from app.utils import upload_file_to_cloudinary
from datetime import datetime
from sqlalchemy import func, select

bp = Blueprint('customer', __name__, url_prefix='/customer')

def serialize_order_event(order):
    status = (order.status or '').strip().lower()
    status_map = {
        'pending': ('Pending', 'warning', 'placed'),
        'accepted': ('Accepted', 'info', 'accepted'),
        'preparing': ('Preparing', 'info', 'preparing'),
        'out for delivery': ('Out for Delivery', 'primary', 'en_route'),
        'delivered': ('Delivered', 'success', 'delivered'),
        'completed': ('Completed', 'success', 'completed'),
        'cancelled': ('Cancelled', 'danger', 'cancelled'),
    }
    label, tone, timeline_key = status_map.get(status, (status.title() if status else 'Unknown', 'secondary', 'unknown'))
    return {
        'id': order.id,
        'status': status,
        'status_label': label,
        'status_tone': tone,
        'timeline_key': timeline_key,
        'delivery_time': order.delivery_time.strftime('%I:%M %p') if order.delivery_time else None,
        'total_amount': float(order.total_amount),
        'order_date': order.order_date.isoformat() if order.order_date else None,
        'restaurant_name': order.restaurant.name if order.restaurant else None
    }

def _is_ajax():
    """Detect AJAX requests reliably."""
    return (request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.headers.get('Accept') == 'application/json' or
            (request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html))

# ── Public JSON API (no auth required) ──────────────────────────────────────

@bp.route('/api/restaurants/search')
def api_search_restaurants():
    """Public search API used by the React discovery page."""
    q            = request.args.get('q', '').strip()
    category_id  = request.args.get('category_id', type=int)
    food_type_id = request.args.get('food_type_id', type=int)
    page         = request.args.get('page', 1, type=int)
    per_page     = 12

    rest_query = Restaurant.query

    # Dish-level filters need a join
    if category_id or food_type_id or q:
        if category_id or food_type_id:
            rest_query = rest_query.join(Dish, Dish.restaurant_id == Restaurant.id)
            if category_id:
                rest_query = rest_query.filter(Dish.category_id == category_id)
            if food_type_id:
                rest_query = rest_query.filter(Dish.food_type_id == food_type_id)

        if q:
            dish_match = rest_query.filter(Dish.name.ilike(f'%{q}%'))
            name_match = Restaurant.query.filter(
                Restaurant.name.ilike(f'%{q}%') |
                Restaurant.address.ilike(f'%{q}%')
            )
            from sqlalchemy import union
            matched_ids = [r.id for r in dish_match.distinct().all()] + \
                          [r.id for r in name_match.all()]
            matched_ids = list(set(matched_ids))
            rest_query = Restaurant.query.filter(Restaurant.id.in_(matched_ids))

    rest_query = rest_query.distinct()
    paginated  = rest_query.paginate(page=page, per_page=per_page, error_out=False)

    results = []
    for r in paginated.items:
        reviews  = Review.query.filter_by(restaurant_id=r.id).all()
        avg      = round(sum(rv.rating for rv in reviews) / len(reviews), 1) if reviews else None
        num_dish = Dish.query.filter_by(restaurant_id=r.id, is_available=True).count()
        results.append({
            'id':          r.id,
            'name':        r.name,
            'address':     r.address,
            'description': r.description,
            'logo_url':    r.logo_url,
            'avg_rating':  avg,
            'review_count': len(reviews),
            'dish_count':  num_dish,
        })

    return jsonify({
        'restaurants': results,
        'total':       paginated.total,
        'pages':       paginated.pages,
        'page':        page,
        'has_next':    paginated.has_next,
    })


@bp.route('/api/restaurants/meta')
def api_restaurant_meta():
    """Return categories and food types for filter dropdowns."""
    categories  = [{'id': c.id, 'name': c.name} for c in Category.query.order_by(Category.name).all()]
    food_types  = [{'id': f.id, 'name': f.name} for f in FoodType.query.order_by(FoodType.name).all()]
    return jsonify({'categories': categories, 'food_types': food_types})

# ── End Public API ───────────────────────────────────────────────────────────

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
    category_id = request.args.get('category_id', type=int)
    food_type_id = request.args.get('food_type_id', type=int)
    min_rating = request.args.get('min_rating', type=int)

    rest_query = Restaurant.query

    if category_id or food_type_id:
        rest_query = rest_query.join(Dish)
        if category_id:
            rest_query = rest_query.filter(Dish.category_id == category_id)
        if food_type_id:
            rest_query = rest_query.filter(Dish.food_type_id == food_type_id)

    if query:
        rest_query = rest_query.filter(Restaurant.name.ilike(f'%{query}%') | Restaurant.address.ilike(f'%{query}%'))

    restaurants = rest_query.distinct().all()

    # Filter by average rating in Python to avoid complex group_by issues with distinct
    if min_rating:
        filtered_rests = []
        for r in restaurants:
            reviews = Review.query.filter_by(restaurant_id=r.id).all()
            avg_rating = sum(rv.rating for rv in reviews) / len(reviews) if reviews else 0
            if avg_rating >= min_rating:
                filtered_rests.append(r)
        restaurants = filtered_rests

    popular_dishes = Dish.query.filter_by(is_available=True).limit(8).all()
    categories = Category.query.all()
    food_types = FoodType.query.all()

    return render_template(
        'index.html', 
        restaurants=restaurants, 
        popular_dishes=popular_dishes,
        query=query,
        categories=categories,
        food_types=food_types,
        selected_category=category_id,
        selected_food_type=food_type_id,
        selected_rating=min_rating
    )

@bp.route('/menu')
@customer_required
def global_menu():
    query = request.args.get('q')
    category_id = request.args.get('category_id', type=int)
    food_type_id = request.args.get('food_type_id', type=int)
    page = request.args.get('page', 1, type=int)

    stmt = select(Dish).filter_by(is_available=True).join(Restaurant)
    if category_id:
        stmt = stmt.filter(Dish.category_id == category_id)
    if food_type_id:
        stmt = stmt.filter(Dish.food_type_id == food_type_id)
    if query:
        stmt = stmt.filter(Dish.name.ilike(f'%{query}%') | Dish.description.ilike(f'%{query}%'))
    
    stmt = stmt.order_by(Dish.id.desc())

    # Paginate dishes (12 per page)
    paginated_dishes = db.paginate(stmt, page=page, per_page=12, error_out=False)

    categories = Category.query.all()
    food_types = FoodType.query.all()

    return render_template(
        'menu.html', 
        dishes=paginated_dishes,
        query=query,
        categories=categories,
        food_types=food_types,
        selected_category=category_id,
        selected_food_type=food_type_id
    )

@bp.route('/restaurant/<int:id>')
@customer_required
def restaurant(id):
    restaurant = db.get_or_404(Restaurant, id)
    dishes = Dish.query.filter_by(restaurant_id=restaurant.id, is_available=True).all()
    reviews = Review.query.filter_by(restaurant_id=restaurant.id).order_by(Review.created_at.desc()).all()
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
    
    menus = RestaurantMedia.query.filter_by(restaurant_id=restaurant.id, media_type='menu_image').order_by(RestaurantMedia.display_order).all()
    videos = RestaurantMedia.query.filter_by(restaurant_id=restaurant.id, media_type='video').order_by(RestaurantMedia.display_order).all()
    promo_images = RestaurantMedia.query.filter_by(restaurant_id=restaurant.id, media_type='promo_image').order_by(RestaurantMedia.display_order).all()
    
    cart = session.get('cart', {})
    cart_items = []
    cart_total = 0.0
    for dish_id_str, qty in cart.items():
        cart_dish = db.session.get(Dish, int(dish_id_str))
        if cart_dish:
            sub = float(cart_dish.price) * qty
            cart_total += sub
            cart_items.append({'dish': cart_dish, 'quantity': qty, 'subtotal': sub})
            
    return render_template('menu_details.html', restaurant=restaurant, dishes=dishes, reviews=reviews, avg_rating=avg_rating, cart_items=cart_items, cart_total=cart_total, menus=menus, videos=videos, promo_images=promo_images)

@bp.route('/dish/<int:id>')
@customer_required
def dish_details(id):
    dish = db.get_or_404(Dish, id)
    restaurant = dish.restaurant
    # Fetch reviews for the restaurant
    reviews = Review.query.filter_by(restaurant_id=restaurant.id).order_by(Review.created_at.desc()).all()
    avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else None
    
    # Fetch related dishes (same category, excluding current dish)
    related_dishes = Dish.query.filter(Dish.category_id == dish.category_id, Dish.id != id, Dish.is_available == True).limit(4).all()
    if not related_dishes:
        # Fallback to other dishes from the same restaurant if no same-category dishes
        related_dishes = Dish.query.filter(Dish.restaurant_id == restaurant.id, Dish.id != id, Dish.is_available == True).limit(4).all()

    return render_template('menu_details.html', dish=dish, restaurant=restaurant, reviews=reviews, avg_rating=avg_rating, related_dishes=related_dishes)

@bp.route('/wishlist/add/<int:dish_id>', methods=['POST'])
@customer_required
def add_to_wishlist(dish_id):
    dish = db.get_or_404(Dish, dish_id)
    # Prevent duplicate entries
    existing = Wishlist.query.filter_by(user_id=current_user.id, dish_id=dish_id).first()
    # Detect AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
              (request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html)
    
    if existing:
        if is_ajax:
            return {'success': False, 'message': 'Already in wishlist'}, 200
        flash('Dish already in your wishlist.', 'info')
    else:
        entry = Wishlist(user_id=current_user.id, dish_id=dish_id)
        db.session.add(entry)
        db.session.commit()
        if is_ajax:
            return {'success': True, 'message': 'Added to wishlist'}, 200
        flash('Dish added to wishlist.', 'success')
    return redirect(request.referrer or url_for('customer.global_menu'))

@bp.route('/wishlist/remove/<int:dish_id>', methods=['POST'])
@customer_required
def remove_from_wishlist(dish_id):
    entry = Wishlist.query.filter_by(user_id=current_user.id, dish_id=dish_id).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
    
    # Detect AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
              (request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html)
              
    if is_ajax:
        return {'success': True, 'message': 'Removed from wishlist'}, 200
        
    flash('Removed from wishlist.', 'success')
    return redirect(url_for('customer.view_wishlist'))

@bp.route('/wishlist')
@customer_required
def view_wishlist():
    wish_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    # Load associated dishes for display
    dishes = [item.dish for item in wish_items]
    return render_template('dashboard_wishlist.html', dishes=dishes)

@bp.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0.0
    for dish_id_str, qty in cart.items():
        dish = db.session.get(Dish, int(dish_id_str))
        if dish:
            subtotal = float(dish.price) * qty
            total += subtotal
            cart_items.append({'dish': dish, 'quantity': qty, 'subtotal': subtotal})
    
    coupon_id = session.get('applied_coupon_id')
    applied_coupon = None
    discount_amount = 0.0
    
    if coupon_id:
        coupon = db.session.get(Coupon, coupon_id)
        if coupon and coupon.is_active:
            # Check if common rest_id matches
            rest_ids = {item['dish'].restaurant_id for item in cart_items}
            if coupon.restaurant_id in rest_ids:
                applied_coupon = coupon
                # Simple logic for cart view: apply to total if rest matches
                rest_total = sum(item['subtotal'] for item in cart_items if item['dish'].restaurant_id == coupon.restaurant_id)
                if coupon.discount_type in ['percent', 'percentage']:
                    discount_amount = rest_total * (float(coupon.discount_value) / 100.0)
                else:
                    discount_amount = float(coupon.discount_value)
                discount_amount = min(discount_amount, rest_total)

    final_total = max(0.0, total - discount_amount)
    return render_template('cart_view.html', cart_items=cart_items, total=total, discount_amount=discount_amount, applied_coupon=applied_coupon, final_total=final_total)

@bp.route('/cart/add/<int:dish_id>', methods=['POST'])
def add_to_cart(dish_id):
    dish = db.get_or_404(Dish, dish_id)
    cart = session.get('cart', {})
    
    qty = request.form.get('quantity', 1, type=int)
    dish_id_str = str(dish_id)
    if dish_id_str in cart:
        cart[dish_id_str] += qty
    else:
        cart[dish_id_str] = qty
        
    session['cart'] = cart
    session.modified = True
    
    if _is_ajax():
        return {'success': True, 'count': sum(cart.values()), 'message': f'{dish.name} added to cart.'}
        
    flash(f'{dish.name} added to cart.', 'success')
    return redirect(request.referrer or url_for('customer.global_menu'))

@bp.route('/cart/clear', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    session.pop('applied_coupon_id', None)
    
    if _is_ajax():
        return {'success': True, 'message': 'Cart cleared.'}
    
    flash('Cart cleared.', 'success')
    return redirect(url_for('customer.view_cart'))

@bp.route('/cart/update/<int:dish_id>/<action>', methods=['POST'])
def update_cart(dish_id, action):
    cart = session.get('cart', {})
    dish_id_str = str(dish_id)
    
    if dish_id_str in cart:
        if action == 'increment':
            cart[dish_id_str] += 1
        elif action == 'decrement':
            if cart[dish_id_str] > 1:
                cart[dish_id_str] -= 1
            else:
                del cart[dish_id_str]
        elif action == 'remove':
            del cart[dish_id_str]
            
        session['cart'] = cart
        session.modified = True
        if not cart:
            session.pop('applied_coupon_id', None)
            
    if _is_ajax():
        # Return updated JSON
        total = 0.0
        item_qty = 0
        item_subtotal = 0.0
        for did_str, qty in cart.items():
            dish = db.session.get(Dish, int(did_str))
            if dish:
                total += float(dish.price) * qty
                if str(did_str) == dish_id_str:
                    item_qty = qty
                    item_subtotal = float(dish.price) * qty
        return {'success': True, 'new_qty': item_qty, 'new_subtotal': item_subtotal, 'new_total': total, 'count': sum(cart.values()), 'action': action}
        
    return redirect(url_for('customer.view_cart'))

@bp.route('/cart/apply_coupon', methods=['POST'])
def apply_coupon():
    code = request.form.get('coupon_code')
    cart = session.get('cart', {})
    is_ajax = _is_ajax()
    
    if not cart:
        if is_ajax:
            return {'success': False, 'message': 'Add items to your cart first.'}, 200
        flash('Add items to your cart first.', 'warning')
        return redirect(url_for('customer.view_cart'))
        
    coupon = Coupon.query.filter_by(code=code, is_active=True).first()
    
    if not coupon:
        session.pop('applied_coupon_id', None)
        if is_ajax:
            return {'success': False, 'message': 'Invalid or inactive promo code.'}, 200
        flash('Invalid or inactive promo code.', 'danger')
        return redirect(url_for('customer.view_cart'))
        
    if coupon.valid_until and coupon.valid_until < datetime.now():
        session.pop('applied_coupon_id', None)
        if is_ajax:
            return {'success': False, 'message': 'This promo code has expired.'}, 200
        flash('This promo code has expired.', 'danger')
        return redirect(url_for('customer.view_cart'))

    # Check if coupon applies to any restaurant in the cart
    cart_items = [db.session.get(Dish, int(did)) for did in cart.keys() if db.session.get(Dish, int(did))]
    rest_ids = {dish.restaurant_id for dish in cart_items if dish}
    if coupon.restaurant_id not in rest_ids:
        session.pop('applied_coupon_id', None)
        if is_ajax:
            return {'success': False, 'message': f'Promo code {code} is only valid for a specific restaurant.'}, 200
        flash(f'Promo code {code} is only valid for a specific restaurant.', 'danger')
        return redirect(url_for('customer.view_cart'))
        
    session['applied_coupon_id'] = coupon.id
    
    # Calculate discount for AJAX response
    if is_ajax:
        total = 0.0
        for did_str, qty in cart.items():
            dish = db.session.get(Dish, int(did_str))
            if dish:
                total += float(dish.price) * qty
        rest_total = sum(
            float(db.session.get(Dish, int(did)).price) * qty
            for did, qty in cart.items()
            if db.session.get(Dish, int(did)) and db.session.get(Dish, int(did)).restaurant_id == coupon.restaurant_id
        )
        if coupon.discount_type in ['percent', 'percentage']:
            discount_amount = rest_total * (float(coupon.discount_value) / 100.0)
        else:
            discount_amount = float(coupon.discount_value)
        discount_amount = min(discount_amount, rest_total)
        final_total = max(0.0, total - discount_amount)
        return {'success': True, 'message': f'Promo code {code} applied!', 'discount_amount': round(discount_amount, 2), 'final_total': round(final_total, 2), 'total': round(total, 2)}
    
    flash(f'Promo code {code} applied successfully!', 'success')
    return redirect(url_for('customer.view_cart'))

@bp.route('/checkout', methods=['GET', 'POST'])
@customer_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('customer.dashboard'))

    # Ensure customer profile has mandatory delivery fields before checkout.
    if not (current_user.address or '').strip() or not (current_user.phone or '').strip():
        flash('Please ensure your phone number and delivery address are set in your profile before checking out.', 'warning')
        return redirect(url_for('customer.edit_profile'))
        
    total = 0.0
    orders_data = {} # { rest_id: {'total': 0.0, 'items': []} }
    
    for dish_id_str, qty in cart.items():
        dish = db.session.get(Dish, int(dish_id_str))
        if dish:
            item_subtotal = float(dish.price) * qty
            total += item_subtotal
            if dish.restaurant_id not in orders_data:
                orders_data[dish.restaurant_id] = {'total': 0.0, 'items': []}
            orders_data[dish.restaurant_id]['total'] += item_subtotal
            orders_data[dish.restaurant_id]['items'].append((dish, qty))
            
    coupon_id = session.get('applied_coupon_id')
    applied_coupon = None
    discount_amount = 0.0
    
    if coupon_id:
        coupon = db.session.get(Coupon, coupon_id)
        if coupon and coupon.is_active and (not coupon.valid_until or coupon.valid_until >= datetime.now()) and coupon.restaurant_id in orders_data:
            applied_coupon = coupon
            rest_total = orders_data[coupon.restaurant_id]['total']
            if coupon.discount_type in ['percent', 'percentage']:
                discount_amount = rest_total * (float(coupon.discount_value) / 100.0)
            else:
                discount_amount = float(coupon.discount_value)
            discount_amount = min(discount_amount, rest_total)
            
    final_total = max(0.0, total - discount_amount)
            
    if request.method == 'POST':
        address = request.form.get('address') or current_user.address
        payment_method = request.form.get('payment_method')
        
        for rest_id, data in orders_data.items():
            rest_discount = discount_amount if (applied_coupon and applied_coupon.restaurant_id == rest_id) else 0.0
            order_total = max(0.0, data['total'] - rest_discount)
            
            order = Order(
                customer_id=current_user.id,
                restaurant_id=rest_id,
                total_amount=order_total,
                discount_amount=rest_discount,
                coupon_id=coupon_id if (applied_coupon and applied_coupon.restaurant_id == rest_id) else None,
                status='pending',
                delivery_address=address,
                payment_method=payment_method
            )
            db.session.add(order)
            db.session.flush() # get order.id
            
            for dish, qty in data['items']:
                item = OrderItem(
                    order_id=order.id,
                    dish_id=dish.id,
                    quantity=qty,
                    price=dish.price
                )
                db.session.add(item)
                
        db.session.commit()
        session.pop('cart', None)
        session.pop('applied_coupon_id', None)
        session.modified = True
        flash('Order(s) placed successfully!', 'success')
        return redirect(url_for('customer.my_orders'))
        
    cart_restaurants = [db.session.get(Restaurant, rid) for rid in orders_data.keys()]
    return render_template('check_out.html', total=final_total, original_total=total, discount_amount=discount_amount, applied_coupon=applied_coupon, restaurants=cart_restaurants)

@bp.route('/my-orders')
@customer_required
def my_orders():
    orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('dashboard_order.html', orders=orders)

@bp.route('/order/<int:id>')
@customer_required
def order_invoice(id):
    order = db.get_or_404(Order, id)
    if order.customer_id != current_user.id:
        flash('Unauthorized access to order.', 'danger')
        return redirect(url_for('customer.my_orders'))
    return render_template('dashboard_order_invoice.html', order=order)

@bp.route('/restaurant/<int:id>/review', methods=['GET', 'POST'])
@customer_required
def leave_review(id):
    restaurant = db.get_or_404(Restaurant, id)
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
        
    return render_template('dashboard_review.html', restaurant=restaurant, review=review)

@bp.route('/api/my-active-orders')
@customer_required
def api_active_orders():
    orders = Order.query.filter(
        Order.customer_id == current_user.id,
        Order.status.in_(['pending', 'accepted', 'preparing', 'out for delivery'])
    ).all()
    
    return {'orders': [serialize_order_event(o) for o in orders]}

@bp.route('/api/my-orders/feed')
@customer_required
def api_orders_feed():
    """Return recent customer orders for lifecycle synchronization."""
    orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.order_date.desc()).limit(20).all()
    return {'orders': [serialize_order_event(o) for o in orders]}

@bp.route('/api/sync-state')
@customer_required
def api_sync_state():
    """Unified customer UI sync payload for cart, wishlist, and coupon panels."""
    cart = session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0

    wishlist_rows = Wishlist.query.filter_by(user_id=current_user.id).all()
    wishlist_ids = [w.dish_id for w in wishlist_rows]

    cart_items = []
    total = 0.0
    for dish_id_str, qty in cart.items():
        dish = db.session.get(Dish, int(dish_id_str))
        if dish:
            subtotal = float(dish.price) * qty
            total += subtotal
            cart_items.append({'dish': dish, 'quantity': qty, 'subtotal': subtotal})

    coupon_status = None
    discount_amount = 0.0
    coupon_id = session.get('applied_coupon_id')
    if coupon_id:
        coupon = db.session.get(Coupon, coupon_id)
        if not coupon:
            coupon_status = {'state': 'invalid', 'message': 'Coupon no longer exists.'}
        elif not coupon.is_active:
            coupon_status = {'state': 'invalid', 'message': 'Coupon is inactive.'}
        elif coupon.valid_until and coupon.valid_until < datetime.now():
            coupon_status = {'state': 'expired', 'message': 'Coupon has expired.'}
        else:
            rest_total = sum(item['subtotal'] for item in cart_items if item['dish'].restaurant_id == coupon.restaurant_id)
            if rest_total <= 0:
                coupon_status = {'state': 'invalid', 'message': 'Coupon does not match current cart restaurants.'}
            else:
                if coupon.discount_type in ['percent', 'percentage']:
                    discount_amount = rest_total * (float(coupon.discount_value) / 100.0)
                else:
                    discount_amount = float(coupon.discount_value)
                discount_amount = min(discount_amount, rest_total)
                coupon_status = {
                    'state': 'applied',
                    'message': f'Coupon {coupon.code} applied.',
                    'code': coupon.code
                }

    final_total = max(0.0, total - discount_amount)
    return {
        'cart_count': cart_count,
        'wishlist_count': len(wishlist_ids),
        'wishlist_ids': wishlist_ids,
        'coupon_status': coupon_status,
        'discount_amount': round(discount_amount, 2),
        'total': round(total, 2),
        'final_total': round(final_total, 2)
    }

# ── Static Pages ─────────────────────────────────────────────────────────────

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/contact')
def contact():
    return render_template('contact.html')

@bp.route('/faq')
def faq():
    return render_template('faq.html')

@bp.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@bp.route('/terms-condition')
def terms_condition():
    return render_template('terms_condition.html')

@bp.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')

@bp.route('/profile')
@customer_required
def profile():
    return render_template('dashboard.html')

@bp.route('/profile/edit', methods=['GET', 'POST'])
@customer_required
def edit_profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.phone = request.form.get('phone')
        current_user.address = request.form.get('address')
        
        # Handle profile image upload
        image_file = request.files.get('profile_image')
        if image_file and image_file.filename != '':
            image_url = upload_file_to_cloudinary(image_file)
            if image_url:
                current_user.profile_image = image_url
        
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('customer.profile'))
        
    return render_template('dashboard_info_edit.html')


@bp.route('/trigger-404-error')
def trigger_404():
    return render_template('404.html'), 404

