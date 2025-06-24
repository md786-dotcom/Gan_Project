import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import url_for

class LocalFileStorage:
    """Local file storage service - secure and simple alternative to cloud storage."""
    
    def __init__(self):
        self.base_upload_dir = Path('static/uploads')
        self.base_processed_dir = Path('static/processed')
        
        # Create directories if they don't exist
        self.base_upload_dir.mkdir(parents=True, exist_ok=True)
        self.base_processed_dir.mkdir(parents=True, exist_ok=True)
    
    def _sanitize_filename(self, filename):
        """Sanitize filename to prevent path traversal attacks."""
        # Remove any path components and sanitize
        filename = secure_filename(filename)
        
        # Generate unique filename to prevent conflicts
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        return f"{timestamp}_{unique_id}_{name}{ext}"
    
    def save_upload(self, file_obj, user_id, original_filename):
        """
        Save uploaded file to local storage.
        
        Args:
            file_obj: File object to save
            user_id: ID of the user uploading the file
            original_filename: Original name of the file
            
        Returns:
            dict: Contains 'filename', 'file_path', and 'url'
        """
        try:
            # Create user-specific directory
            user_dir = self.base_upload_dir / str(user_id)
            user_dir.mkdir(exist_ok=True)
            
            # Generate secure filename
            filename = self._sanitize_filename(original_filename)
            file_path = user_dir / filename
            
            # Save file
            file_obj.save(str(file_path))
            
            # Generate URL for accessing the file
            relative_path = f"uploads/{user_id}/{filename}"
            file_url = url_for('static', filename=relative_path, _external=True)
            
            return {
                'filename': filename,
                'file_path': str(file_path),
                'url': file_url,
                'relative_path': relative_path
            }
            
        except Exception as e:
            raise Exception(f"Failed to save file: {str(e)}")
    
    def save_processed(self, file_data, user_id, original_filename, transformation_info=""):
        """
        Save processed image data to local storage.
        
        Args:
            file_data: Processed image data as bytes
            user_id: ID of the user
            original_filename: Original filename
            transformation_info: String describing transformations applied
            
        Returns:
            dict: Contains 'filename', 'file_path', and 'url'
        """
        try:
            # Create user-specific processed directory
            user_dir = self.base_processed_dir / str(user_id)
            user_dir.mkdir(exist_ok=True)
            
            # Generate filename for processed image
            name, ext = os.path.splitext(original_filename)
            if transformation_info:
                filename = f"{name}_{transformation_info}{ext}"
            else:
                filename = f"{name}_processed{ext}"
            
            filename = self._sanitize_filename(filename)
            file_path = user_dir / filename
            
            # Save processed image data
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Generate URL
            relative_path = f"processed/{user_id}/{filename}"
            file_url = url_for('static', filename=relative_path, _external=True)
            
            return {
                'filename': filename,
                'file_path': str(file_path),
                'url': file_url,
                'relative_path': relative_path
            }
            
        except Exception as e:
            raise Exception(f"Failed to save processed file: {str(e)}")
    
    def delete_file(self, file_path):
        """
        Delete file from local storage.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Failed to delete file: {str(e)}")
            return False
    
    def file_exists(self, file_path):
        """
        Check if file exists in local storage.
        
        Args:
            file_path: Path to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        return os.path.exists(file_path)
    
    def get_file_size(self, file_path):
        """Get file size in bytes."""
        try:
            return os.path.getsize(file_path)
        except:
            return 0
    
    def get_user_files(self, user_id):
        """
        Get list of all files for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Contains 'uploads' and 'processed' file lists
        """
        user_upload_dir = self.base_upload_dir / str(user_id)
        user_processed_dir = self.base_processed_dir / str(user_id)
        
        uploads = []
        processed = []
        
        # Get uploaded files
        if user_upload_dir.exists():
            for file_path in user_upload_dir.iterdir():
                if file_path.is_file():
                    uploads.append({
                        'filename': file_path.name,
                        'path': str(file_path),
                        'size': self.get_file_size(file_path),
                        'url': url_for('static', filename=f"uploads/{user_id}/{file_path.name}", _external=True)
                    })
        
        # Get processed files
        if user_processed_dir.exists():
            for file_path in user_processed_dir.iterdir():
                if file_path.is_file():
                    processed.append({
                        'filename': file_path.name,
                        'path': str(file_path),
                        'size': self.get_file_size(file_path),
                        'url': url_for('static', filename=f"processed/{user_id}/{file_path.name}", _external=True)
                    })
        
        return {
            'uploads': uploads,
            'processed': processed
        }
    
    def cleanup_user_files(self, user_id):
        """Remove all files for a user (for account deletion)."""
        try:
            user_upload_dir = self.base_upload_dir / str(user_id)
            user_processed_dir = self.base_processed_dir / str(user_id)
            
            if user_upload_dir.exists():
                shutil.rmtree(user_upload_dir)
            
            if user_processed_dir.exists():
                shutil.rmtree(user_processed_dir)
            
            return True
        except Exception as e:
            print(f"Failed to cleanup user files: {str(e)}")
            return False