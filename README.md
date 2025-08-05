# Take.app Clone

A comprehensive e-commerce platform built with Flask, featuring support for both global and Somaliland payment methods. This project is a clone of Take.app with enhanced features for the Somaliland market.

## Features

### 🛍️ E-commerce Features
- **Store Management**: Create and manage multiple online stores
- **Product Catalog**: Add, edit, and organize products with images
- **Shopping Cart**: Full cart functionality with session management
- **Order Management**: Complete order lifecycle from creation to delivery
- **Inventory Tracking**: Real-time stock management

### 💳 Payment Integration
- **Global Payments**:
  - Stripe (Credit/Debit Cards)
  - PayPal
- **Somaliland Payments**:
  - EVC Plus (Telesom)
  - Golis Saad Service
  - Edahab
- **Cash on Delivery**

### 🎨 User Experience
- **Responsive Design**: Mobile-first approach with Bootstrap 5
- **Multiple Themes**: Customizable store themes
- **WhatsApp Integration**: Direct ordering via WhatsApp
- **SEO Optimized**: Meta tags, sitemap, and robots.txt

### 💰 Revenue Generation
- **Google AdSense**: Integrated ad display
- **Adsterra**: Fallback ad network
- **Premium Subscriptions**: Tiered pricing model
- **Affiliate Links**: Commission-based revenue

### 🔧 Technical Features
- **User Authentication**: Secure login/register system
- **Admin Panel**: Complete administrative dashboard
- **Email Notifications**: Order confirmations and updates
- **Security**: CSRF protection, SQL injection prevention
- **Database**: SQLite (development) / PostgreSQL (production)

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: Bootstrap 5, JavaScript
- **Database**: SQLite / PostgreSQL
- **Payment**: Stripe, PayPal, Somaliland APIs
- **Ads**: Google AdSense, Adsterra
- **Hosting**: Replit + Custom Domain

## Installation

### Prerequisites
- Python 3.8+
- pip
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/take-app-clone.git
   cd take-app-clone
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize Database**
   ```bash
   python app.py
   ```

6. **Run the Application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-secret-key
FLASK_ENV=development
FLASK_DEBUG=True

# Database
DATABASE_URL=sqlite:///takeapp.db

# Email
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Stripe
STRIPE_PUBLIC_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key

# PayPal
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_client_secret

# Somaliland Payments
EVC_PLUS_API_KEY=your_api_key
GOLIS_SAAD_API_KEY=your_api_key
EDAHAB_API_KEY=your_api_key

# AdSense
ADSENSE_PUBLISHER_ID=ca-pub-your_id
```

### Payment Gateway Setup

#### Stripe
1. Create a Stripe account
2. Get your API keys from the dashboard
3. Configure webhooks for payment notifications

#### PayPal
1. Create a PayPal Developer account
2. Create an app to get client credentials
3. Set up return and cancel URLs

#### Somaliland Payment APIs
Contact the respective service providers for API access:
- EVC Plus: Telesom
- Golis Saad: Golis Telecom
- Edahab: Dahabshiil

## Project Structure

```
take-app-clone/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── forms.py               # WTForms definitions
├── auth.py                # Authentication blueprint
├── dashboard.py           # Dashboard blueprint
├── store.py               # Store/public pages blueprint
├── payments.py            # Payment processing blueprint
├── admin.py               # Admin panel blueprint
├── requirements.txt       # Python dependencies
├── env.example            # Environment variables template
├── static/                # Static files
│   ├── css/
│   ├── js/
│   └── images/
├── templates/             # HTML templates
│   ├── auth/
│   ├── dashboard/
│   ├── store/
│   └── admin/
└── README.md
```

## Usage

### For Store Owners

1. **Register an Account**
   - Visit the homepage and click "Create Your Store"
   - Complete the registration form

2. **Create Your Store**
   - Log in to your dashboard
   - Click "New Store" and fill in store details
   - Choose a theme and upload logo/banner

3. **Add Products**
   - Navigate to your store's products section
   - Click "Add Product" and fill in product details
   - Upload product images

4. **Manage Orders**
   - View incoming orders in the dashboard
   - Update order status as you process them
   - Track payments and inventory

### For Customers

1. **Browse Stores**
   - Visit the stores page to see all active stores
   - Click on any store to view their products

2. **Shop Products**
   - Add products to cart
   - Proceed to checkout
   - Choose payment method

3. **Complete Purchase**
   - Fill in shipping details
   - Complete payment using preferred method
   - Receive order confirmation

## Deployment

### Replit Deployment

1. **Create Replit Account**
   - Sign up at replit.com
   - Create a new Python project

2. **Upload Code**
   - Import from GitHub or upload files
   - Set environment variables in Replit secrets

3. **Configure Domain**
   - Set up custom domain in Replit
   - Configure DNS settings

### Production Considerations

- Use PostgreSQL instead of SQLite
- Set up SSL certificates
- Configure proper logging
- Set up monitoring and backups
- Use production-grade email service
- Implement rate limiting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact: support@takeapp-clone.com

## Roadmap

- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] Mobile app
- [ ] API for third-party integrations
- [ ] Advanced inventory management
- [ ] Bulk import/export
- [ ] Advanced reporting
- [ ] Customer reviews and ratings

## Acknowledgments

- Flask community for the excellent framework
- Bootstrap team for the responsive design framework
- Payment gateway providers for their APIs
- Open source contributors

---

**Note**: This is a clone/educational project. For production use, ensure compliance with all applicable laws and regulations, especially regarding payment processing and data protection.