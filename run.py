#!/usr/bin/env python3
"""
Run script for Take.app Clone
"""

from app import app

if __name__ == '__main__':
    print("Starting Take.app Clone...")
    print("Visit http://localhost:5000 to access the application")
    print("Press Ctrl+C to stop the server")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    ) 