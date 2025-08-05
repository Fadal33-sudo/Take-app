from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import Store, Product, Order
from forms import StoreForm, ProductForm

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    stores = Store.query.filter_by(owner_id=current_user.id).all()
    total_orders = Order.query.join(Store).filter(Store.owner_id == current_user.id).count()
    total_products = Product.query.join(Store).filter(Store.owner_id == current_user.id).count()
    recent_orders = Order.query.join(Store).filter(Store.owner_id == current_user.id).order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('dashboard/index.html', 
                         stores=stores, 
                         total_orders=total_orders,
                         total_products=total_products,
                         recent_orders=recent_orders)

@dashboard_bp.route('/dashboard/stores')
@login_required
def stores():
    stores = Store.query.filter_by(owner_id=current_user.id).all()
    return render_template('dashboard/stores.html', stores=stores)

@dashboard_bp.route('/dashboard/stores/new', methods=['GET', 'POST'])
@login_required
def new_store():
    form = StoreForm()
    if form.validate_on_submit():
        slug = form.name.data.lower().replace(' ', '-')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        
        counter = 1
        original_slug = slug
        while Store.query.filter_by(slug=slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        store = Store(
            name=form.name.data,
            slug=slug,
            description=form.description.data,
            address=form.address.data,
            phone=form.phone.data,
            email=form.email.data,
            website=form.website.data,
            theme=form.theme.data,
            owner_id=current_user.id
        )
        
        db.session.add(store)
        db.session.commit()
        flash('Store created successfully!', 'success')
        return redirect(url_for('dashboard.stores'))
    
    return render_template('dashboard/new_store.html', form=form)

@dashboard_bp.route('/dashboard/stores/<int:store_id>/products')
@login_required
def products(store_id):
    store = Store.query.filter_by(id=store_id, owner_id=current_user.id).first_or_404()
    products = Product.query.filter_by(store_id=store_id).all()
    return render_template('dashboard/products.html', store=store, products=products)

@dashboard_bp.route('/dashboard/stores/<int:store_id>/products/new', methods=['GET', 'POST'])
@login_required
def new_product(store_id):
    store = Store.query.filter_by(id=store_id, owner_id=current_user.id).first_or_404()
    form = ProductForm()
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            compare_price=form.compare_price.data,
            stock_quantity=form.stock_quantity.data,
            is_featured=form.is_featured.data,
            store_id=store_id
        )
        
        db.session.add(product)
        db.session.commit()
        flash('Product created successfully!', 'success')
        return redirect(url_for('dashboard.products', store_id=store_id))
    
    return render_template('dashboard/new_product.html', form=form, store=store)

@dashboard_bp.route('/dashboard/orders')
@login_required
def orders():
    orders = Order.query.join(Store).filter(Store.owner_id == current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('dashboard/orders.html', orders=orders) 