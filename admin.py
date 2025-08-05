from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import User, Store, Product, Order, Payment

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to check if user is admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    total_users = User.query.count()
    total_stores = Store.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total)).filter(Order.status == 'paid').scalar() or 0
    
    # Recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('admin/index.html',
                         total_users=total_users,
                         total_stores=total_stores,
                         total_products=total_products,
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         recent_users=recent_users,
                         recent_orders=recent_orders)

@admin_bp.route('/admin/users')
@login_required
@admin_required
def users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/admin/users/<int:user_id>/make-admin', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    """Make user admin"""
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f'User {user.username} is now an admin.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/admin/stores')
@login_required
@admin_required
def stores():
    """Manage stores"""
    page = request.args.get('page', 1, type=int)
    stores = Store.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/stores.html', stores=stores)

@admin_bp.route('/admin/stores/<int:store_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_store_status(store_id):
    """Toggle store active status"""
    store = Store.query.get_or_404(store_id)
    store.is_active = not store.is_active
    db.session.commit()
    
    status = 'activated' if store.is_active else 'deactivated'
    flash(f'Store {store.name} has been {status}.', 'success')
    return redirect(url_for('admin.stores'))

@admin_bp.route('/admin/orders')
@login_required
@admin_required
def orders():
    """Manage orders"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Order.query
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)

@admin_bp.route('/admin/orders/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    """Order detail view"""
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@admin_bp.route('/admin/orders/<int:order_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'paid', 'shipped', 'delivered', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash(f'Order {order.order_number} status updated to {new_status}.', 'success')
    else:
        flash('Invalid status.', 'error')
    
    return redirect(url_for('admin.order_detail', order_id=order_id))

@admin_bp.route('/admin/payments')
@login_required
@admin_required
def payments():
    """View payment records"""
    page = request.args.get('page', 1, type=int)
    payments = Payment.query.order_by(Payment.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/payments.html', payments=payments)

@admin_bp.route('/admin/reports')
@login_required
@admin_required
def reports():
    """Admin reports"""
    # Revenue by month
    revenue_by_month = db.session.query(
        db.func.strftime('%Y-%m', Order.created_at).label('month'),
        db.func.sum(Order.total).label('revenue')
    ).filter(Order.status == 'paid').group_by('month').order_by('month').all()
    
    # Top selling products
    top_products = db.session.query(
        Product.name,
        db.func.sum(OrderItem.quantity).label('total_sold')
    ).join(OrderItem).group_by(Product.id).order_by(db.func.sum(OrderItem.quantity).desc()).limit(10).all()
    
    # Payment method distribution
    payment_methods = db.session.query(
        Payment.payment_method,
        db.func.count(Payment.id).label('count')
    ).group_by(Payment.payment_method).all()
    
    return render_template('admin/reports.html',
                         revenue_by_month=revenue_by_month,
                         top_products=top_products,
                         payment_methods=payment_methods) 