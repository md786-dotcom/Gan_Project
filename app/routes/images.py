from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import io
from app import db
from app.models.image import Image
from app.models.user import User
from app.services.s3_service import S3Service
from app.services.image_service import ImageService
from app.utils.validators import validate_image_file, validate_transformation_params
from app.utils.helpers import generate_filename

images_bp = Blueprint('images', __name__)

# Initialize services
s3_service = S3Service()
image_service = ImageService()

@images_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_image():
    """Upload an image file."""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Validate file
        is_valid, message = validate_image_file(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Read file data
        file_data = file.read()
        file.seek(0)  # Reset file pointer for potential reuse
        
        # Get image information
        image_info = image_service.get_image_info(file_data)
        
        # Generate secure filename
        original_filename = secure_filename(file.filename)
        new_filename = generate_filename(original_filename)
        
        # Upload to S3
        file_io = io.BytesIO(file_data)
        upload_result = s3_service.upload_file(
            file_io, 
            current_user_id, 
            new_filename, 
            file.mimetype
        )
        
        # Save image record to database
        image_record = Image(
            user_id=current_user_id,
            original_name=original_filename,
            filename=new_filename,
            s3_key=upload_result['s3_key'],
            s3_url=upload_result['s3_url'],
            mime_type=file.mimetype,
            file_size=len(file_data),
            width=image_info['width'],
            height=image_info['height']
        )
        
        db.session.add(image_record)
        db.session.commit()
        
        return jsonify({
            'message': 'Image uploaded successfully',
            'image': image_record.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Image upload error: {str(e)}")
        return jsonify({'error': 'Failed to upload image'}), 500

@images_bp.route('/', methods=['GET'])
@jwt_required()
def list_images():
    """List all images for the authenticated user."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Query user images with pagination
        images = Image.query.filter_by(user_id=current_user_id)\
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
@jwt_required()
def get_image(image_id):
    """Get specific image details."""
    try:
        current_user_id = get_jwt_identity()
        
        image = Image.query.filter_by(id=image_id, user_id=current_user_id).first()
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        return jsonify({'image': image.to_dict()}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get image error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve image'}), 500

@images_bp.route('/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_image(image_id):
    """Delete an image."""
    try:
        current_user_id = get_jwt_identity()
        
        image = Image.query.filter_by(id=image_id, user_id=current_user_id).first()
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        # Delete from S3
        s3_service.delete_file(image.s3_key)
        
        # Delete from database
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({'message': 'Image deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete image error: {str(e)}")
        return jsonify({'error': 'Failed to delete image'}), 500

@images_bp.route('/<int:image_id>/transform', methods=['POST'])
@jwt_required()
def transform_image(image_id):
    """Apply transformations to an image."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get the original image
        image = Image.query.filter_by(id=image_id, user_id=current_user_id).first()
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        # Get transformation parameters
        transform_params = request.get_json() or {}
        
        # Validate transformation parameters
        is_valid, errors = validate_transformation_params(transform_params)
        if not is_valid:
            return jsonify({'error': 'Invalid transformation parameters', 'details': errors}), 400
        
        # Download original image from S3
        # Note: In a real implementation, you might want to cache this or use a more efficient method
        import requests
        response = requests.get(image.s3_url)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to download original image'}), 500
        
        image_bytes = response.content
        
        # Apply transformations
        transformed_bytes = image_bytes
        applied_transformations = []
        
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
        
        # Rotate
        if 'rotate' in transform_params:
            angle = int(transform_params['rotate'])
            transformed_bytes = image_service.rotate_image(transformed_bytes, angle)
            applied_transformations.append({
                'type': 'rotate',
                'angle': angle
            })
        
        # Flip
        if 'flip' in transform_params:
            direction = transform_params['flip']
            transformed_bytes = image_service.flip_image(transformed_bytes, direction)
            applied_transformations.append({
                'type': 'flip',
                'direction': direction
            })
        
        # Apply filters
        if 'filter' in transform_params:
            filter_type = transform_params['filter']
            transformed_bytes = image_service.apply_filter(transformed_bytes, filter_type)
            applied_transformations.append({
                'type': 'filter',
                'filter_type': filter_type
            })
        
        # Add watermark
        if 'watermark' in transform_params:
            watermark_params = transform_params['watermark']
            if isinstance(watermark_params, dict) and 'text' in watermark_params:
                transformed_bytes = image_service.add_watermark(
                    transformed_bytes,
                    watermark_params['text'],
                    watermark_params.get('position', 'bottom-right'),
                    watermark_params.get('opacity', 0.5)
                )
                applied_transformations.append({
                    'type': 'watermark',
                    'text': watermark_params['text'],
                    'position': watermark_params.get('position', 'bottom-right'),
                    'opacity': watermark_params.get('opacity', 0.5)
                })
        
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
        
        # Compress
        if 'compress' in transform_params:
            quality = transform_params.get('quality', 85)
            transformed_bytes = image_service.compress_image(transformed_bytes, quality)
            applied_transformations.append({
                'type': 'compress',
                'quality': quality
            })
        
        # Get transformed image info
        transformed_info = image_service.get_image_info(transformed_bytes)
        
        # Generate filename for transformed image
        base_name, ext = image.original_name.rsplit('.', 1) if '.' in image.original_name else (image.original_name, 'jpg')
        transformed_filename = f"{base_name}_transformed_{image_id}.{ext}"
        
        # Upload transformed image to S3
        transformed_io = io.BytesIO(transformed_bytes)
        upload_result = s3_service.upload_file(
            transformed_io,
            current_user_id,
            transformed_filename,
            f"image/{ext.lower()}"
        )
        
        # Create new image record for transformed image
        transformed_image = Image(
            user_id=current_user_id,
            original_name=transformed_filename,
            filename=transformed_filename,
            s3_key=upload_result['s3_key'],
            s3_url=upload_result['s3_url'],
            mime_type=f"image/{ext.lower()}",
            file_size=len(transformed_bytes),
            width=transformed_info['width'],
            height=transformed_info['height']
        )
        
        # Set transformations
        transformed_image.set_transformations(applied_transformations)
        
        db.session.add(transformed_image)
        db.session.commit()
        
        return jsonify({
            'message': 'Image transformed successfully',
            'original_image': image.to_dict(),
            'transformed_image': transformed_image.to_dict(),
            'applied_transformations': applied_transformations
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Transform image error: {str(e)}")
        return jsonify({'error': 'Failed to transform image', 'details': str(e)}), 500