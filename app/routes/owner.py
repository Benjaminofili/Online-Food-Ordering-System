from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint('owner', __name__, url_prefix='/owner')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'owner':
        flash('Access denied. You are not a restaurant owner.', 'danger')
        return redirect(url_for('index'))
    return render_template('owner/dashboard.html')