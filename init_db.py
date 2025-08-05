#!/usr/bin/env python3
"""
Database initialization script for Take App
Run this script to create database tables
"""

from app import app, db
from models import User, Store, Product, Order, OrderItem, Payment

def init_database():
    """Initialize the database with all tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_database() 