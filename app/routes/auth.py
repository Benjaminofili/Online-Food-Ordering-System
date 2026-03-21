from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm, ChangePasswordForm

bp = Blueprint('auth', __name__, url_prefix='/auth')

def _dashboard_redirect():
    """Redirect to the correct dashboard based on user role."""
    if current_user.role == 'customer':
        return redirect(url_for('customer.dashboard'))
    elif current_user.role == 'owner':
        return redirect(url_for('owner.dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('index'))

@bp.route('/profile')
@login_required
def profile():
    if current_user.role == 'customer':
        return redirect(url_for('customer.profile'))
    elif current_user.role == 'owner':
        return redirect(url_for('owner.profile'))
    return _dashboard_redirect()

# ── JSON APIs for React Frontend ─────────────────────────────────────────────

@bp.route('/api/auth/me', methods=['GET'])
def api_me():
    if current_user.is_authenticated:
        # If user is owner, also send restaurant info
        restaurant = None
        if current_user.role == 'owner' and getattr(current_user, 'restaurants', []):
            restaurant = current_user.restaurants[0]
            
        return jsonify({
            'user': {
                'id': current_user.id,
                'name': current_user.name,
                'email': current_user.email,
                'role': current_user.role,
                'restaurant_id': restaurant.id if restaurant else None,
                'restaurant_name': restaurant.name if restaurant else None
            }
        })
    return jsonify({'user': None}), 401

@bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember_me', False)
    
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        login_user(user, remember=remember)
        return jsonify({'message': 'Logged in successfully', 'role': user.role}), 200
        
    return jsonify({'error': 'Invalid email or password'}), 401

@bp.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    email = data.get('email')
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'This email is already registered.'}), 400
        
    user = User(
        name=data.get('name'),
        email=email,
        phone=data.get('phone'),
        address=data.get('address'),
        role=data.get('role', 'customer')
    )
    user.set_password(data.get('password'))
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'Registration successful'}), 201

@bp.route('/api/auth/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

# ── End JSON APIs ────────────────────────────────────────────────────────────

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return _dashboard_redirect()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            # Role‑based redirection
            if user.role == 'customer':
                return redirect(url_for('customer.dashboard'))
            elif user.role == 'owner':
                return redirect(url_for('owner.dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('index'))  # fallback
        flash('Invalid email or password', 'danger')
    return render_template('sign_in.html', form=form)

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return _dashboard_redirect()
        else:
            flash('Current password is incorrect.', 'danger')
    return render_template('dashboard_change_password.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return _dashboard_redirect()
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('sign_up.html', form=form)

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return _dashboard_redirect()
    return render_template('forgot_password.html')