// Main JavaScript for Take.app Clone

// Initialize Stripe
let stripe;
if (typeof Stripe !== 'undefined') {
    stripe = Stripe('pk_test_YOUR_STRIPE_PUBLIC_KEY'); // Replace with your Stripe public key
}

// Payment handling
function handlePayment(paymentMethod, orderId, amount) {
    const loadingSpinner = document.getElementById('loading-spinner');
    const paymentForm = document.getElementById('payment-form');
    
    if (loadingSpinner) loadingSpinner.style.display = 'block';
    if (paymentForm) paymentForm.style.display = 'none';
    
    switch (paymentMethod) {
        case 'stripe':
            handleStripePayment(orderId, amount);
            break;
        case 'paypal':
            handlePayPalPayment(orderId, amount);
            break;
        case 'evc_plus':
        case 'golis_saad':
        case 'edahab':
            handleMobilePayment(paymentMethod, orderId, amount);
            break;
        case 'cod':
            handleCashOnDelivery(orderId);
            break;
    }
}

// Stripe payment handling
async function handleStripePayment(orderId, amount) {
    try {
        const response = await fetch('/payment/stripe/create-payment-intent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                order_id: orderId,
                amount: amount
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
            return;
        }
        
        const result = await stripe.confirmCardPayment(data.client_secret, {
            payment_method: {
                card: elements.getElement('card'),
                billing_details: {
                    name: document.getElementById('cardholder-name').value
                }
            }
        });
        
        if (result.error) {
            showError(result.error.message);
        } else {
            window.location.href = `/store/order/${orderId}/confirmation`;
        }
    } catch (error) {
        showError('Payment failed. Please try again.');
    }
}

// PayPal payment handling
async function handlePayPalPayment(orderId, amount) {
    try {
        const response = await fetch('/payment/paypal/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                order_id: orderId,
                amount: amount
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
            return;
        }
        
        window.location.href = data.approval_url;
    } catch (error) {
        showError('Payment failed. Please try again.');
    }
}

// Mobile payment handling (Somaliland)
async function handleMobilePayment(paymentMethod, orderId, amount) {
    const phone = document.getElementById('phone-number').value;
    
    if (!phone) {
        showError('Please enter your phone number');
        return;
    }
    
    try {
        const response = await fetch(`/payment/${paymentMethod}/initiate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                order_id: orderId,
                amount: amount,
                phone: phone
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
            return;
        }
        
        showSuccess(`Payment initiated! Transaction ID: ${data.transaction_id}`);
        setTimeout(() => {
            window.location.href = `/store/order/${orderId}/confirmation`;
        }, 2000);
    } catch (error) {
        showError('Payment failed. Please try again.');
    }
}

// Cash on delivery
function handleCashOnDelivery(orderId) {
    window.location.href = `/store/order/${orderId}/confirmation`;
}

// Cart functionality
function addToCart(productId, storeId) {
    const quantity = document.getElementById(`quantity-${productId}`).value;
    
    fetch(`/store/add-to-cart/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Product added to cart!');
            updateCartCount();
        } else {
            showError(data.error);
        }
    })
    .catch(error => {
        showError('Failed to add product to cart');
    });
}

function updateCartCount() {
    // Update cart count in navigation
    const cartCount = document.getElementById('cart-count');
    if (cartCount) {
        // This would need to be implemented based on your cart data
        // For now, just increment the current count
        const currentCount = parseInt(cartCount.textContent) || 0;
        cartCount.textContent = currentCount + 1;
    }
}

// Utility functions
function showSuccess(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Image preview for file uploads
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById(previewId).src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Search functionality
function searchProducts(query) {
    const products = document.querySelectorAll('.product-card');
    const searchTerm = query.toLowerCase();
    
    products.forEach(product => {
        const productName = product.querySelector('.product-name').textContent.toLowerCase();
        const productDesc = product.querySelector('.product-description').textContent.toLowerCase();
        
        if (productName.includes(searchTerm) || productDesc.includes(searchTerm)) {
            product.style.display = 'block';
        } else {
            product.style.display = 'none';
        }
    });
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
}); 