#!/usr/bin/env python3
"""
Image Processing Service - Simplified Entry Point

Simply run: python app.py
No configuration needed - everything works out of the box!
"""

import os
import sys
from app import create_app, db

def setup_directories():
    """Create necessary directories for the application."""
    directories = [
        'uploads',
        'processed',
        'static/uploads',
        'static/processed'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Created application directories")

def main():
    """Main entry point for the application."""
    print("🚀 Starting Image Processing Service...")
    print("=" * 50)
    
    # Setup directories
    setup_directories()
    
    # Create Flask app
    app = create_app()
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            sys.exit(1)
    
    print("\n🎉 Image Processing Service is ready!")
    print("📱 Open your browser and go to: http://localhost:5001")
    print("💡 No configuration needed - everything works out of the box!")
    print("\nFeatures available:")
    print("- 🖼️  Upload and process images")
    print("- ✨ Apply transformations (resize, rotate, filters, etc.)")
    print("- 👤 User registration and authentication")
    print("- 📱 Beautiful web interface")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=True,
            use_reloader=False  # Prevent double startup messages
        )
    except KeyboardInterrupt:
        print("\n👋 Thanks for using Image Processing Service!")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()