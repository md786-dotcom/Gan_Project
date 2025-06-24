from flask import Blueprint, request, jsonify, current_app, session, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import io
from app import db
from app.models.image import Image
from app.models.user import User
from app.services.file_storage import LocalFileStorage
from app.services.image_service import ImageService
from app.utils.validators import validate_image_file, validate_transformation_params
from app.utils.helpers import generate_filename

images_bp = Blueprint('images', __name__)

# Initialize services
file_storage = LocalFileStorage()
image_service = ImageService()

def get_current_user():
    """Get current user from session or JWT token."""
    # Try session first (for web interface)
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    
    # Try JWT token (for API)
    try:
        user_id = get_jwt_identity()
        if user_id:
            return User.query.get(user_id)
    except:
        pass
    
    return None

@images_bp.route('/upload', methods=['POST'])
def upload_image():
    """Upload an image file (API and Web)."""
    try:
        # Get current user (from session or JWT)
        current_user = get_current_user()
        if not current_user:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to upload images.', 'error')
            return redirect(url_for('web.index'))
        
        # Check if file is present in request
        if 'file' not in request.files:
            error_msg = 'No file provided'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('web.upload_page'))
        
        file = request.files['file']
        
        # Validate file
        is_valid, message = validate_image_file(file)
        if not is_valid:
            if request.is_json:
                return jsonify({'error': message}), 400
            flash(message, 'error')
            return redirect(url_for('web.upload_page'))
        
        # Get image information
        file.seek(0)  # Reset file pointer
        file_data = file.read()
        image_info = image_service.get_image_info(file_data)
        
        # Save file using local storage
        file.seek(0)  # Reset file pointer for saving
        upload_result = file_storage.save_upload(
            file, 
            current_user.id, 
            file.filename
        )
        
        # Save image record to database
        image_record = Image(
            user_id=current_user.id,
            original_name=file.filename,
            filename=upload_result['filename'],
            s3_key=upload_result['relative_path'],  # Store relative path
            s3_url=upload_result['url'],
            mime_type=file.mimetype,
            file_size=len(file_data),
            width=image_info['width'],
            height=image_info['height']
        )
        
        db.session.add(image_record)
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'message': 'Image uploaded successfully',
                'image': image_record.to_dict()
            }), 201
        else:
            flash('Image uploaded successfully!', 'success')
            return redirect(url_for('web.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Image upload error: {str(e)}")
        error_msg = 'Failed to upload image'
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('web.upload_page'))

@images_bp.route('/', methods=['GET'])
def list_images():
    """List all images for the authenticated user (API only)."""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Query user images with pagination
        images = Image.query.filter_by(user_id=current_user.id)\
                          .order_by(Image.created_at.desc())\
                          .paginate(
                              page=page, 
                              per_page=per_page, 
                              error_out=False
                          )
        
        return jsonify({
            'images': [image.to_dict() for image in images.items],
            'pagination': {
                'page': images.page,
                'pages': images.pages,
                'per_page': images.per_page,
                'total': images.total
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"List images error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve images'}), 500

@images_bp.route('/<int:image_id>', methods=['GET'])
def get_image(image_id):
    """Get specific image details (API only)."""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authentication required'}), 401
        
        image = Image.query.filter_by(id=image_id, user_id=current_user.id).first()
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        return jsonify({'image': image.to_dict()}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get image error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve image'}), 500

@images_bp.route('/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """Delete an image (API and Web)."""
    try:
        current_user = get_current_user()
        if not current_user:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to delete images.', 'error')
            return redirect(url_for('web.index'))
        
        image = Image.query.filter_by(id=image_id, user_id=current_user.id).first()
        
        if not image:
            error_msg = 'Image not found'
            if request.is_json:
                return jsonify({'error': error_msg}), 404
            flash(error_msg, 'error')
            return redirect(url_for('web.dashboard'))
        
        # Delete from local storage
        file_storage.delete_file(image.s3_key)  # s3_key contains the relative path
        
        # Delete from database
        db.session.delete(image)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Image deleted successfully'}), 200
        else:
            flash('Image deleted successfully!', 'success')
            return redirect(url_for('web.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete image error: {str(e)}")
        error_msg = 'Failed to delete image'
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('web.dashboard'))

@images_bp.route('/<int:image_id>/transform', methods=['POST'])
def transform_image(image_id):
    """Apply transformations to an image (API and Web)."""
    try:
        current_user = get_current_user()
        if not current_user:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to transform images.', 'error')
            return redirect(url_for('web.index'))
        
        # Get the original image
        image = Image.query.filter_by(id=image_id, user_id=current_user.id).first()
        
        if not image:
            error_msg = 'Image not found'
            if request.is_json:
                return jsonify({'error': error_msg}), 404
            flash(error_msg, 'error')
            return redirect(url_for('web.dashboard'))
        
        # Get transformation parameters (from JSON or form data)
        if request.is_json:
            transform_params = request.get_json() or {}
        else:
            # Handle form data from web interface
            transform_params = {}
            if request.form.get('width'):
                transform_params['width'] = int(request.form.get('width'))
            if request.form.get('height'):
                transform_params['height'] = int(request.form.get('height'))
            if request.form.get('rotate'):
                transform_params['rotate'] = int(request.form.get('rotate'))
            if request.form.get('flip'):
                transform_params['flip'] = request.form.get('flip')
            if request.form.get('filter'):
                transform_params['filter'] = request.form.get('filter')
            if request.form.get('watermark_text'):
                transform_params['watermark'] = {
                    'text': request.form.get('watermark_text'),
                    'position': request.form.get('watermark_position', 'bottom-right'),
                    'opacity': float(request.form.get('watermark_opacity', 0.5))
                }
            if request.form.get('format'):
                transform_params['format'] = request.form.get('format')
            if request.form.get('quality'):
                transform_params['quality'] = int(request.form.get('quality'))
        
        # Validate transformation parameters
        is_valid, errors = validate_transformation_params(transform_params)
        if not is_valid:
            error_msg = 'Invalid transformation parameters'
            if request.is_json:
                return jsonify({'error': error_msg, 'details': errors}), 400
            flash(f"{error_msg}: {', '.join(errors)}", 'error')
            return redirect(url_for('web.transform_page', image_id=image_id))
        
        # Read original image from local storage
        image_path = f"app/static/{image.s3_key}"  # s3_key contains relative path
        if not file_storage.file_exists(image_path):
            error_msg = 'Original image file not found'
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            flash(error_msg, 'error')
            return redirect(url_for('web.dashboard'))
        
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        # Apply transformations
        transformed_bytes = image_bytes
        applied_transformations = []
        transformation_summary = []
        
        # Resize
        if 'width' in transform_params or 'height' in transform_params:
            width = transform_params.get('width')
            height = transform_params.get('height')
            transformed_bytes = image_service.resize_image(
                transformed_bytes, 
                width, 
                height, 
                maintain_aspect_ratio=transform_params.get('maintain_aspect_ratio', True)
            )
            applied_transformations.append({
                'type': 'resize',
                'width': width,
                'height': height
            })
            transformation_summary.append(f"resize_{width}x{height}")
        
        # Rotate
        if 'rotate' in transform_params:
            angle = int(transform_params['rotate'])
            if angle != 0:
                transformed_bytes = image_service.rotate_image(transformed_bytes, angle)
                applied_transformations.append({
                    'type': 'rotate',
                    'angle': angle
                })
                transformation_summary.append(f"rotate_{angle}")
        
        # Flip
        if 'flip' in transform_params:
            direction = transform_params['flip']
            if direction in ['horizontal', 'vertical']:
                transformed_bytes = image_service.flip_image(transformed_bytes, direction)
                applied_transformations.append({
                    'type': 'flip',
                    'direction': direction
                })
                transformation_summary.append(f"flip_{direction}")
        
        # Apply filters
        if 'filter' in transform_params:
            filter_type = transform_params['filter']
            if filter_type in ['grayscale', 'sepia']:
                transformed_bytes = image_service.apply_filter(transformed_bytes, filter_type)
                applied_transformations.append({
                    'type': 'filter',
                    'filter_type': filter_type
                })
                transformation_summary.append(f"filter_{filter_type}")
        
        # Add watermark
        if 'watermark' in transform_params:
            watermark_params = transform_params['watermark']
            if isinstance(watermark_params, dict) and 'text' in watermark_params:
                text = watermark_params['text'][:50]  # Limit watermark text length
                transformed_bytes = image_service.add_watermark(
                    transformed_bytes,
                    text,
                    watermark_params.get('position', 'bottom-right'),
                    watermark_params.get('opacity', 0.5)
                )
                applied_transformations.append({
                    'type': 'watermark',
                    'text': text,
                    'position': watermark_params.get('position', 'bottom-right'),
                    'opacity': watermark_params.get('opacity', 0.5)
                })
                transformation_summary.append("watermark")
        
        # Change format
        if 'format' in transform_params:
            new_format = transform_params['format'].upper()
            quality = transform_params.get('quality', 85)
            transformed_bytes = image_service.change_format(transformed_bytes, new_format, quality)
            applied_transformations.append({
                'type': 'format_change',
                'format': new_format,
                'quality': quality
            })
            transformation_summary.append(f"format_{new_format.lower()}")
        
        # Compress
        if 'compress' in transform_params:
            quality = transform_params.get('quality', 85)
            transformed_bytes = image_service.compress_image(transformed_bytes, quality)
            applied_transformations.append({
                'type': 'compress',
                'quality': quality
            })
            transformation_summary.append(f"compress_q{quality}")
        
        # Get transformed image info
        transformed_info = image_service.get_image_info(transformed_bytes)
        
        # Generate filename for transformed image
        transformation_string = "_".join(transformation_summary[:3])  # Limit filename length
        base_name, ext = image.original_name.rsplit('.', 1) if '.' in image.original_name else (image.original_name, 'jpg')
        transformed_filename = f"{base_name}_{transformation_string}.{ext}"
        
        # Save transformed image to local storage
        upload_result = file_storage.save_processed(
            transformed_bytes,
            current_user.id,
            transformed_filename,
            transformation_string
        )
        
        # Create new image record for transformed image
        transformed_image = Image(
            user_id=current_user.id,
            original_name=transformed_filename,
            filename=upload_result['filename'],
            s3_key=upload_result['relative_path'],
            s3_url=upload_result['url'],
            mime_type=f"image/{ext.lower()}",
            file_size=len(transformed_bytes),
            width=transformed_info['width'],
            height=transformed_info['height']
        )
        
        # Set transformations
        transformed_image.set_transformations(applied_transformations)
        
        db.session.add(transformed_image)
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'message': 'Image transformed successfully',
                'original_image': image.to_dict(),
                'transformed_image': transformed_image.to_dict(),
                'applied_transformations': applied_transformations
            }), 201
        else:
            flash('Image transformed successfully!', 'success')
            return redirect(url_for('web.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Transform image error: {str(e)}")
        error_msg = 'Failed to transform image'
        if request.is_json:
            return jsonify({'error': error_msg, 'details': str(e)}), 500
        flash(error_msg, 'error')
        if 'image_id' in locals():
            return redirect(url_for('web.transform_page', image_id=image_id))
        return redirect(url_for('web.dashboard'))