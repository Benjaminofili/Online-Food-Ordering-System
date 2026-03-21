from flask import Blueprint, render_template, flash, redirect, url_for, request, session, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Restaurant, Dish, Order, OrderItem, Review, Coupon, Category, FoodType, Wishlist
from sqlalchemy import func
from datetime import datetime

bp = Blueprint('customer', __name__, url_prefix='/customer')

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

    dish_query = Dish.query.filter_by(is_available=True).join(Restaurant)

    if category_id:
        dish_query = dish_query.filter(Dish.category_id == category_id)
    if food_type_id:
        dish_query = dish_query.filter(Dish.food_type_id == food_type_id)
    if query:
        dish_query = dish_query.filter(Dish.name.ilike(f'%{query}%') | Dish.description.ilike(f'%{query}%'))

    # Paginate dishes (12 per page)
    paginated_dishes = dish_query.order_by(Dish.id.desc()).paginate(page=page, per_page=12, error_out=False)

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
    restaurant = Restaurant.query.get_or_404(id)
    dishes = Dish.query.filter_by(restaurant_id=restaurant.id, is_available=True).all()
    reviews = Review.query.filter_by(restaurant_id=restaurant.id).order_by(Review.created_at.desc()).all()
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
    
    cart = session.get('cart', {})
    cart_items = []
    cart_total = 0.0
    for dish_id_str, qty in cart.items():
        cart_dish = Dish.query.get(int(dish_id_str))
        if cart_dish:
            sub = float(cart_dish.price) * qty
            cart_total += sub
            cart_items.append({'dish': cart_dish, 'quantity': qty, 'subtotal': sub})
            
    return render_template('menu_details.html', restaurant=restaurant, dishes=dishes, reviews=reviews, avg_rating=avg_rating, cart_items=cart_items, cart_total=cart_total)

@bp.route('/dish/<int:id>')
@customer_required
def dish_details(id):
    dish = Dish.query.get_or_404(id)
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
    dish = Dish.query.get_or_404(dish_id)
    # Prevent duplicate entries
    existing = Wishlist.query.filter_by(user_id=current_user.id, dish_id=dish_id).first()
    if existing:
        flash('Dish already in your wishlist.', 'info')
    else:
        entry = Wishlist(user_id=current_user.id, dish_id=dish_id)
        db.session.add(entry)
        db.session.commit()
        flash('Dish added to wishlist.', 'success')
    # Redirect back to the page the user came from
    return redirect(request.referrer or url_for('customer.global_menu'))

@bp.route('/wishlist/remove/<int:dish_id>', methods=['POST'])
@customer_required
def remove_from_wishlist(dish_id):
    Wishlist.query.filter_by(user_id=current_user.id, dish_id=dish_id).delete()
    db.session.commit()
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
        dish = Dish.query.get(int(dish_id_str))
        if dish:
            subtotal = float(dish.price) * qty
            total += subtotal
            cart_items.append({'dish': dish, 'quantity': qty, 'subtotal': subtotal})
    
    coupon_id = session.get('applied_coupon_id')
    applied_coupon = None
    discount_amount = 0.0
    
    if coupon_id:
        coupon = Coupon.query.get(coupon_id)
        if coupon and coupon.is_active:
            # Check if common rest_id matches
            rest_ids = {item['dish'].restaurant_id for item in cart_items}
            if coupon.restaurant_id in rest_ids:
                applied_coupon = coupon
                # Simple logic for cart view: apply to total if rest matches
                rest_total = sum(item['subtotal'] for item in cart_items if item['dish'].restaurant_id == coupon.restaurant_id)
                if coupon.discount_type == 'percent':
                    discount_amount = rest_total * (float(coupon.discount_value) / 100.0)
                else:
                    discount_amount = float(coupon.discount_value)
                discount_amount = min(discount_amount, rest_total)

    final_total = max(0.0, total - discount_amount)
    return render_template('cart_view.html', cart_items=cart_items, total=total, discount_amount=discount_amount, applied_coupon=applied_coupon, final_total=final_total)

@bp.route('/cart/add/<int:dish_id>', methods=['POST'])
def add_to_cart(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    cart = session.get('cart', {})
    
    qty = request.form.get('quantity', 1, type=int)
    dish_id_str = str(dish_id)
    if dish_id_str in cart:
        cart[dish_id_str] += qty
    else:
        cart[dish_id_str] = qty
        
    session['cart'] = cart
    session.modified = True
    
    if request.headers.get('Accept') == 'application/json' or request.is_json:
        return {'success': True, 'count': sum(cart.values()), 'message': f'{dish.name} added to cart.'}
        
    flash(f'{dish.name} added to cart.', 'success')
    return redirect(request.referrer or url_for('customer.global_menu'))

@bp.route('/cart/clear', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    session.pop('applied_coupon_id', None)
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
def apply_coupon():
    code = request.form.get('coupon_code')
    cart = session.get('cart', {})
    
    if not cart:
        flash('Add items to your cart first.', 'warning')
        return redirect(url_for('customer.view_cart'))
        
    coupon = Coupon.query.filter_by(code=code, is_active=True).first()
    
    if not coupon:
        flash('Invalid or inactive promo code.', 'danger')
        session.pop('applied_coupon_id', None)
        return redirect(url_for('customer.view_cart'))
        
    if coupon.valid_until and coupon.valid_until < datetime.now():
        flash('This promo code has expired.', 'danger')
        session.pop('applied_coupon_id', None)
        return redirect(url_for('customer.view_cart'))

    # Check if coupon applies to any restaurant in the cart
    cart_items = [Dish.query.get(int(did)) for did in cart.keys() if Dish.query.get(int(did))]
    rest_ids = {dish.restaurant_id for dish in cart_items if dish}
    if coupon.restaurant_id not in rest_ids:
        flash(f'Promo code {code} is only valid for a specific restaurant.', 'danger')
        session.pop('applied_coupon_id', None)
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
        
    total = 0.0
    orders_data = {} # { rest_id: {'total': 0.0, 'items': []} }
    
    for dish_id_str, qty in cart.items():
        dish = Dish.query.get(int(dish_id_str))
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
        coupon = Coupon.query.get(coupon_id)
        if coupon and coupon.is_active and (not coupon.valid_until or coupon.valid_until >= datetime.now()) and coupon.restaurant_id in orders_data:
            applied_coupon = coupon
            rest_total = orders_data[coupon.restaurant_id]['total']
            if coupon.discount_type == 'percent':
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
        flash('Order(s) placed successfully!', 'success')
        return redirect(url_for('customer.my_orders'))
        
    cart_restaurants = [Restaurant.query.get(rid) for rid in orders_data.keys()]
    return render_template('check_out.html', total=final_total, original_total=total, discount_amount=discount_amount, applied_coupon=applied_coupon, restaurants=cart_restaurants)

@bp.route('/my-orders')
@customer_required
def my_orders():
    orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('dashboard_order.html', orders=orders)

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
        
    return render_template('dashboard_review.html', restaurant=restaurant, review=review)

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


@bp.route('/trigger-404-error')
def trigger_404():
    return render_template('404.html'), 404

