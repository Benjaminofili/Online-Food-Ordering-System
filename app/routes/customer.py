from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask import flash, redirect, url_for

bp = Blueprint('customer', __name__, url_prefix='/customer')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'customer':
        flash('Access denied. You are not a customer.', 'danger')
        return redirect(url_for('index'))
    return render_template('customer/dashboard.html')