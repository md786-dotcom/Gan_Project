import re
from werkzeug.datastructures import FileStorage

def validate_email(email):
    """Validate email format."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def validate_password(password):
    """Validate password strength."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Password is valid"

def validate_image_file(file):
    """Validate uploaded image file."""
    if not file or not isinstance(file, FileStorage):
        return False, "No file provided"
    
    if file.filename == '':
        return False, "No file selected"
    
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_extension not in allowed_extensions:
        return False, f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
    
    # Check MIME type
    allowed_mime_types = {
        'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 
        'image/bmp', 'image/tiff', 'image/webp'
    }
    
    if file.mimetype not in allowed_mime_types:
        return False, "Invalid file type"
    
    return True, "File is valid"

def validate_transformation_params(params):
    """Validate image transformation parameters."""
    errors = []
    
    # Width and height validation
    if 'width' in params:
        try:
            width = int(params['width'])
            if width <= 0 or width > 5000:
                errors.append("Width must be between 1 and 5000 pixels")
        except (ValueError, TypeError):
            errors.append("Width must be a valid integer")
    
    if 'height' in params:
        try:
            height = int(params['height'])
            if height <= 0 or height > 5000:
                errors.append("Height must be between 1 and 5000 pixels")
        except (ValueError, TypeError):
            errors.append("Height must be a valid integer")
    
    # Quality validation
    if 'quality' in params:
        try:
            quality = int(params['quality'])
            if quality < 1 or quality > 100:
                errors.append("Quality must be between 1 and 100")
        except (ValueError, TypeError):
            errors.append("Quality must be a valid integer")
    
    # Rotation validation
    if 'rotate' in params:
        try:
            rotation = int(params['rotate'])
            if rotation not in [0, 90, 180, 270]:
                errors.append("Rotation must be 0, 90, 180, or 270 degrees")
        except (ValueError, TypeError):
            errors.append("Rotation must be a valid integer")
    
    # Format validation
    if 'format' in params:
        allowed_formats = {'jpeg', 'png', 'webp', 'avif'}
        if params['format'].lower() not in allowed_formats:
            errors.append(f"Format must be one of: {', '.join(allowed_formats)}")
    
    return len(errors) == 0, errors