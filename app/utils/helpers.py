import uuid
import os
from datetime import datetime

def generate_filename(original_filename):
    """Generate a unique filename while preserving the extension."""
    if not original_filename:
        return str(uuid.uuid4())
    
    name, ext = os.path.splitext(original_filename)
    unique_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    
    return f"{timestamp}_{unique_id}{ext}"

def allowed_file(filename):
    """Check if file has an allowed extension."""
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_size_mb(file_size_bytes):
    """Convert file size from bytes to MB."""
    return round(file_size_bytes / (1024 * 1024), 2)

def sanitize_filename(filename):
    """Sanitize filename by removing or replacing unsafe characters."""
    import re
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove any leading/trailing whitespace or dots
    filename = filename.strip('. ')
    return filename