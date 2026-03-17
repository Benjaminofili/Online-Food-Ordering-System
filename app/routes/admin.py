from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied. You are not an admin.', 'danger')
        return redirect(url_for('index'))
    return render_template('admin/dashboard.html')