from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from models import Order, Payment
import stripe
import paypalrestsdk
import requests
import json

payments_bp = Blueprint('payments', __name__)

# Stripe config waa in lagu sameeyaa create_app() ee app.py, ha isticmaalin current_app banaanka function.
# PayPal config sidoo kale waa in lagu sameeyaa create_app() ee app.py, ha isticmaalin current_app banaanka function.
# Haddii aad u baahan tahay config, isticmaal gudaha function sida:
# from flask import current_app
# def some_func():
#     key = current_app.config['PAYPAL_CLIENT_ID']

paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": current_app.config['PAYPAL_CLIENT_ID'],
    "client_secret": current_app.config['PAYPAL_CLIENT_SECRET']
})

@payments_bp.route('/payment/stripe/create-payment-intent', methods=['POST'])
def create_stripe_payment_intent():
    """Create Stripe payment intent"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        amount = data.get('amount')
        
        order = Order.query.get_or_404(order_id)
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency='usd',
            metadata={'order_id': order_id}
        )
        
        return jsonify({
            'client_secret': intent.client_secret
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@payments_bp.route('/payment/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, current_app.config.get('STRIPE_WEBHOOK_SECRET', '')
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400
    
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata']['order_id']
        
        # Update order and payment status
        order = Order.query.get(order_id)
        if order:
            order.status = 'paid'
            
            payment = Payment(
                order_id=order_id,
                payment_method='stripe',
                amount=payment_intent['amount'] / 100,
                currency='usd',
                status='completed',
                transaction_id=payment_intent['id'],
                gateway_response=json.dumps(payment_intent)
            )
            
            db.session.add(payment)
            db.session.commit()
    
    return jsonify({'status': 'success'})

@payments_bp.route('/payment/paypal/create', methods=['POST'])
def create_paypal_payment():
    """Create PayPal payment"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        amount = data.get('amount')
        
        order = Order.query.get_or_404(order_id)
        
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": url_for('payments.paypal_success', _external=True),
                "cancel_url": url_for('payments.paypal_cancel', _external=True)
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"Order {order.order_number}",
                        "sku": order.order_number,
                        "price": str(amount),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(amount),
                    "currency": "USD"
                },
                "description": f"Payment for order {order.order_number}"
            }]
        })
        
        if payment.create():
            # Store payment ID in session for later reference
            session['paypal_payment_id'] = payment.id
            session['paypal_order_id'] = order_id
            
            # Get approval URL
            for link in payment.links:
                if link.rel == "approval_url":
                    return jsonify({'approval_url': link.href})
        else:
            return jsonify({'error': payment.error}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@payments_bp.route('/payment/paypal/success')
def paypal_success():
    """Handle PayPal payment success"""
    payment_id = session.get('paypal_payment_id')
    order_id = session.get('paypal_order_id')
    
    if not payment_id or not order_id:
        flash('Payment session expired', 'error')
        return redirect(url_for('home'))
    
    payment = paypalrestsdk.Payment.find(payment_id)
    
    if payment.execute({"payer_id": request.args.get('PayerID')}):
        # Payment successful
        order = Order.query.get(order_id)
        if order:
            order.status = 'paid'
            
            payment_record = Payment(
                order_id=order_id,
                payment_method='paypal',
                amount=float(payment.transactions[0].amount.total),
                currency='usd',
                status='completed',
                transaction_id=payment_id,
                gateway_response=json.dumps(payment.to_dict())
            )
            
            db.session.add(payment_record)
            db.session.commit()
            
            flash('Payment completed successfully!', 'success')
        else:
            flash('Order not found', 'error')
    else:
        flash('Payment failed', 'error')
    
    # Clear session
    session.pop('paypal_payment_id', None)
    session.pop('paypal_order_id', None)
    
    return redirect(url_for('home'))

@payments_bp.route('/payment/paypal/cancel')
def paypal_cancel():
    """Handle PayPal payment cancellation"""
    flash('Payment was cancelled', 'info')
    session.pop('paypal_payment_id', None)
    session.pop('paypal_order_id', None)
    return redirect(url_for('home'))

@payments_bp.route('/payment/evc-plus/initiate', methods=['POST'])
def initiate_evc_plus_payment():
    """Initiate EVC Plus payment"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        amount = data.get('amount')
        phone = data.get('phone')
        
        order = Order.query.get_or_404(order_id)
        
        # EVC Plus API call (example - replace with actual API)
        api_url = "https://api.evcplus.com/payment/initiate"
        payload = {
            "amount": amount,
            "phone": phone,
            "reference": order.order_number,
            "description": f"Payment for order {order.order_number}"
        }
        
        headers = {
            "Authorization": f"Bearer {current_app.config['EVC_PLUS_API_KEY']}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            # Create payment record
            payment = Payment(
                order_id=order_id,
                payment_method='evc_plus',
                amount=amount,
                currency='usd',
                status='pending',
                transaction_id=result.get('transaction_id'),
                gateway_response=json.dumps(result)
            )
            
            db.session.add(payment)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'transaction_id': result.get('transaction_id'),
                'message': 'Payment initiated successfully'
            })
        else:
            return jsonify({'error': 'Payment initiation failed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@payments_bp.route('/payment/golis-saad/initiate', methods=['POST'])
def initiate_golis_saad_payment():
    """Initiate Golis Saad Service payment"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        amount = data.get('amount')
        phone = data.get('phone')
        
        order = Order.query.get_or_404(order_id)
        
        # Golis Saad API call (example - replace with actual API)
        api_url = "https://api.golissaad.com/payment/initiate"
        payload = {
            "amount": amount,
            "phone": phone,
            "reference": order.order_number,
            "description": f"Payment for order {order.order_number}"
        }
        
        headers = {
            "Authorization": f"Bearer {current_app.config['GOLIS_SAAD_API_KEY']}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            payment = Payment(
                order_id=order_id,
                payment_method='golis_saad',
                amount=amount,
                currency='usd',
                status='pending',
                transaction_id=result.get('transaction_id'),
                gateway_response=json.dumps(result)
            )
            
            db.session.add(payment)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'transaction_id': result.get('transaction_id'),
                'message': 'Payment initiated successfully'
            })
        else:
            return jsonify({'error': 'Payment initiation failed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@payments_bp.route('/payment/edahab/initiate', methods=['POST'])
def initiate_edahab_payment():
    """Initiate Edahab payment"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        amount = data.get('amount')
        phone = data.get('phone')
        
        order = Order.query.get_or_404(order_id)
        
        # Edahab API call (example - replace with actual API)
        api_url = "https://api.edahab.com/payment/initiate"
        payload = {
            "amount": amount,
            "phone": phone,
            "reference": order.order_number,
            "description": f"Payment for order {order.order_number}"
        }
        
        headers = {
            "Authorization": f"Bearer {current_app.config['EDAHAB_API_KEY']}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            payment = Payment(
                order_id=order_id,
                payment_method='edahab',
                amount=amount,
                currency='usd',
                status='pending',
                transaction_id=result.get('transaction_id'),
                gateway_response=json.dumps(result)
            )
            
            db.session.add(payment)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'transaction_id': result.get('transaction_id'),
                'message': 'Payment initiated successfully'
            })
        else:
            return jsonify({'error': 'Payment initiation failed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400 