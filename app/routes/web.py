from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_wtf.csrf import generate_csrf
from app.models.user import User
from app.models.image import Image
from app import db
import re

web_bp = Blueprint('web', __name__)

def is_valid_email(email):
    """Validate email format to prevent XSS."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text):
    """Sanitize text input to prevent XSS attacks."""
    if not text:
        return ""
    # Remove potential script tags and dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        text = text.replace(char, '')
    return text.strip()

@web_bp.route('/')
def index():
    """Landing page - shows login/signup or dashboard based on authentication."""
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            # User is logged in, show dashboard
            return redirect(url_for('web.dashboard'))
    
    # Show landing page for non-authenticated users
    return render_template('index.html', csrf_token=generate_csrf())

@web_bp.route('/dashboard')
def dashboard():
    """Main dashboard for authenticated users."""
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('web.index'))
    
    user = User.query.get(user_id)
    if not user:
        session.clear()
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('web.index'))
    
    # Get user's images with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Show 12 images per page
    
    images = Image.query.filter_by(user_id=user_id)\
                       .order_by(Image.created_at.desc())\
                       .paginate(
                           page=page, 
                           per_page=per_page, 
                           error_out=False
                       )
    
    return render_template(
        'dashboard.html', 
        user=user, 
        images=images,
        csrf_token=generate_csrf()
    )

@web_bp.route('/upload')
def upload_page():
    """Image upload page."""
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to upload images.', 'warning')
        return redirect(url_for('web.index'))
    
    user = User.query.get(user_id)
    return render_template('upload.html', user=user, csrf_token=generate_csrf())

@web_bp.route('/transform/<int:image_id>')
def transform_page(image_id):
    """Image transformation page."""
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to transform images.', 'warning')
        return redirect(url_for('web.index'))
    
    image = Image.query.filter_by(id=image_id, user_id=user_id).first()
    if not image:
        flash('Image not found or access denied.', 'error')
        return redirect(url_for('web.dashboard'))
    
    user = User.query.get(user_id)
    return render_template(
        'transform.html', 
        user=user, 
        image=image, 
        csrf_token=generate_csrf()
    )

@web_bp.route('/gallery')
def gallery():
    """Image gallery page."""
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view your gallery.', 'warning')
        return redirect(url_for('web.index'))
    
    user = User.query.get(user_id)
    
    # Get all user images for gallery view
    images = Image.query.filter_by(user_id=user_id)\
                       .order_by(Image.created_at.desc())\
                       .all()
    
    return render_template('gallery.html', user=user, images=images)

@web_bp.route('/help')
def help_page():
    """Help and instructions page."""
    user_id = session.get('user_id')
    user = None
    if user_id:
        user = User.query.get(user_id)
    
    return render_template('help.html', user=user)

@web_bp.route('/web/login', methods=['POST'])
def web_login():
    """Handle web login form submission."""
    try:
        email = sanitize_input(request.form.get('email', '').strip().lower())
        password = request.form.get('password', '')
        
        # Validate inputs
        if not email or not password:
            flash('Email and password are required.', 'error')
            return redirect(url_for('web.index'))
        
        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('web.index'))
        
        # Find user and verify password
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('web.index'))
        
        # Set session
        session['user_id'] = user.id
        session['user_email'] = user.email
        
        flash(f'Welcome back, {email}!', 'success')
        return redirect(url_for('web.dashboard'))
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        flash('An error occurred during login. Please try again.', 'error')
        return redirect(url_for('web.index'))

@web_bp.route('/web/signup', methods=['POST'])
def web_signup():
    """Handle web signup form submission."""
    try:
        email = sanitize_input(request.form.get('email', '').strip().lower())
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate inputs
        if not email or not password or not confirm_password:
            flash('All fields are required.', 'error')
            return redirect(url_for('web.index'))
        
        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('web.index'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('web.index'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('web.index'))
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.', 'error')
            return redirect(url_for('web.index'))
        
        # Create new user
        user = User(email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Set session
        session['user_id'] = user.id
        session['user_email'] = user.email
        
        flash(f'Welcome to Image Processing Service, {email}!', 'success')
        return redirect(url_for('web.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Signup error: {str(e)}")
        flash('An error occurred during registration. Please try again.', 'error')
        return redirect(url_for('web.index'))

@web_bp.route('/logout')
def logout():
    """Handle user logout."""
    user_email = session.get('user_email', 'User')
    session.clear()
    flash(f'Goodbye, {user_email}! You have been logged out.', 'info')
    return redirect(url_for('web.index'))