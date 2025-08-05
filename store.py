from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import current_user, login_required
from app import db
from models import Store, Product, Order, OrderItem, User
from forms import OrderForm
import uuid

store_bp = Blueprint('store', __name__)

@store_bp.route('/store/<slug>')
def store_page(slug):
    """Public store page"""
    store = Store.query.filter_by(slug=slug, is_active=True).first_or_404()
    products = Product.query.filter_by(store_id=store.id, is_active=True).all()
    featured_products = Product.query.filter_by(store_id=store.id, is_active=True, is_featured=True).all()
    
    return render_template('store/store.html', 
                         store=store, 
                         products=products,
                         featured_products=featured_products)

@store_bp.route('/store/<slug>/product/<int:product_id>')
def product_detail(slug, product_id):
    """Product detail page"""
    store = Store.query.filter_by(slug=slug, is_active=True).first_or_404()
    product = Product.query.filter_by(id=product_id, store_id=store.id, is_active=True).first_or_404()
    
    # Get related products
    related_products = Product.query.filter(
        Product.store_id == store.id,
        Product.id != product_id,
        Product.is_active == True
    ).limit(4).all()
    
    return render_template('store/product_detail.html', 
                         store=store, 
                         product=product,
                         related_products=related_products)

@store_bp.route('/store/<slug>/cart')
def cart(slug):
    """Shopping cart page"""
    store = Store.query.filter_by(slug=slug, is_active=True).first_or_404()
    cart_items = session.get('cart', {}).get(str(store.id), {})
    
    products = []
    total = 0
    
    for product_id, quantity in cart_items.items():
        product = Product.query.get(product_id)
        if product and product.store_id == store.id and product.is_active:
            item_total = product.price * quantity
            products.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total
    
    return render_template('store/cart.html', store=store, products=products, total=total)

@store_bp.route('/store/<slug>/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(slug, product_id):
    """Add product to cart"""
    store = Store.query.filter_by(slug=slug, is_active=True).first_or_404()
    product = Product.query.filter_by(id=product_id, store_id=store.id, is_active=True).first_or_404()
    
    quantity = int(request.form.get('quantity', 1))
    
    if 'cart' not in session:
        session['cart'] = {}
    
    if str(store.id) not in session['cart']:
        session['cart'][str(store.id)] = {}
    
    if str(product_id) in session['cart'][str(store.id)]:
        session['cart'][str(store.id)][str(product_id)] += quantity
    else:
        session['cart'][str(store.id)][str(product_id)] = quantity
    
    session.modified = True
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('store.cart', slug=slug))

@store_bp.route('/store/<slug>/remove-from-cart/<int:product_id>', methods=['POST'])
def remove_from_cart(slug, product_id):
    """Remove product from cart"""
    store = Store.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    if 'cart' in session and str(store.id) in session['cart']:
        if str(product_id) in session['cart'][str(store.id)]:
            del session['cart'][str(store.id)][str(product_id)]
            session.modified = True
            flash('Product removed from cart!', 'success')
    
    return redirect(url_for('store.cart', slug=slug))

@store_bp.route('/store/<slug>/checkout', methods=['GET', 'POST'])
def checkout(slug):
    """Checkout page"""
    store = Store.query.filter_by(slug=slug, is_active=True).first_or_404()
    cart_items = session.get('cart', {}).get(str(store.id), {})
    
    if not cart_items:
        flash('Your cart is empty!', 'error')
        return redirect(url_for('store.store_page', slug=slug))
    
    products = []
    total = 0
    
    for product_id, quantity in cart_items.items():
        product = Product.query.get(product_id)
        if product and product.store_id == store.id and product.is_active:
            item_total = product.price * quantity
            products.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total
    
    form = OrderForm()
    
    if form.validate_on_submit():
        # Create order
        order = Order(
            customer_id=current_user.id if current_user.is_authenticated else None,
            store_id=store.id,
            subtotal=total,
            total=total,
            shipping_address=form.shipping_address.data,
            notes=form.notes.data
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Create order items
        for item in products:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price=item['product'].price,
                total=item['total']
            )
            db.session.add(order_item)
            
            # Update stock
            item['product'].stock_quantity -= item['quantity']
        
        db.session.commit()
        
        # Clear cart
        if 'cart' in session and str(store.id) in session['cart']:
            del session['cart'][str(store.id)]
            session.modified = True
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('store.order_confirmation', slug=slug, order_id=order.id))
    
    return render_template('store/checkout.html', 
                         store=store, 
                         products=products, 
                         total=total,
                         form=form)

@store_bp.route('/store/<slug>/order/<int:order_id>/confirmation')
def order_confirmation(slug, order_id):
    """Order confirmation page"""
    store = Store.query.filter_by(slug=slug, is_active=True).first_or_404()
    order = Order.query.filter_by(id=order_id, store_id=store.id).first_or_404()
    
    return render_template('store/order_confirmation.html', store=store, order=order)

@store_bp.route('/store/<slug>/whatsapp-order/<int:product_id>')
def whatsapp_order(slug, product_id):
    """Generate WhatsApp order link"""
    store = Store.query.filter_by(slug=slug, is_active=True).first_or_404()
    product = Product.query.filter_by(id=product_id, store_id=store.id, is_active=True).first_or_404()
    
    # Generate WhatsApp message
    message = f"Hi! I'd like to order:\n\n{product.name}\nPrice: ${product.price}\n\nStore: {store.name}\nStore URL: {request.host_url}store/{slug}"
    
    # WhatsApp API URL
    whatsapp_url = f"https://wa.me/{store.phone}?text={message}"
    
    return redirect(whatsapp_url) 