#!/usr/bin/env python3
"""
WSGI entry point for Take App
This file is used by Gunicorn to start the Flask application
"""

from app import create_app, db

# Create the Flask application instance
app = create_app()

# Initialize database tables
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

if __name__ == '__main__':
    app.run() 