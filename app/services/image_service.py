from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import io
import os

class ImageService:
    """Service for image processing operations using Pillow."""
    
    @staticmethod
    def get_image_info(image_bytes):
        """
        Get basic information about an image.
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            dict: Image information including dimensions, format, etc.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            return {
                'width': image.width,
                'height': image.height,
                'format': image.format,
                'mode': image.mode,
                'size_bytes': len(image_bytes)
            }
        except Exception as e:
            raise Exception(f"Failed to get image info: {str(e)}")
    
    @staticmethod
    def resize_image(image_bytes, width=None, height=None, maintain_aspect_ratio=True):
        """
        Resize an image.
        
        Args:
            image_bytes: Image data as bytes
            width: Target width
            height: Target height
            maintain_aspect_ratio: Whether to maintain aspect ratio
            
        Returns:
            bytes: Processed image as bytes
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            if width is None and height is None:
                return image_bytes
            
            original_width, original_height = image.size
            
            if maintain_aspect_ratio:
                if width and height:
                    # Calculate aspect ratio and resize accordingly
                    aspect_ratio = original_width / original_height
                    if width / height > aspect_ratio:
                        width = int(height * aspect_ratio)
                    else:
                        height = int(width / aspect_ratio)
                elif width:
                    height = int(width * original_height / original_width)
                elif height:
                    width = int(height * original_width / original_height)
            
            resized_image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            resized_image.save(output, format=image.format)
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to resize image: {str(e)}")
    
    @staticmethod
    def crop_image(image_bytes, x, y, width, height):
        """
        Crop an image.
        
        Args:
            image_bytes: Image data as bytes
            x, y: Top-left corner coordinates
            width, height: Crop dimensions
            
        Returns:
            bytes: Cropped image as bytes
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Ensure crop area is within image bounds
            x = max(0, min(x, image.width))
            y = max(0, min(y, image.height))
            width = min(width, image.width - x)
            height = min(height, image.height - y)
            
            cropped_image = image.crop((x, y, x + width, y + height))
            
            output = io.BytesIO()
            cropped_image.save(output, format=image.format)
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to crop image: {str(e)}")
    
    @staticmethod
    def rotate_image(image_bytes, angle):
        """
        Rotate an image.
        
        Args:
            image_bytes: Image data as bytes
            angle: Rotation angle in degrees
            
        Returns:
            bytes: Rotated image as bytes
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            rotated_image = image.rotate(angle, expand=True)
            
            output = io.BytesIO()
            rotated_image.save(output, format=image.format)
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to rotate image: {str(e)}")
    
    @staticmethod
    def flip_image(image_bytes, direction='horizontal'):
        """
        Flip an image.
        
        Args:
            image_bytes: Image data as bytes
            direction: 'horizontal' or 'vertical'
            
        Returns:
            bytes: Flipped image as bytes
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            if direction == 'horizontal':
                flipped_image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            elif direction == 'vertical':
                flipped_image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            else:
                raise ValueError("Direction must be 'horizontal' or 'vertical'")
            
            output = io.BytesIO()
            flipped_image.save(output, format=image.format)
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to flip image: {str(e)}")
    
    @staticmethod
    def apply_filter(image_bytes, filter_type):
        """
        Apply filters to an image.
        
        Args:
            image_bytes: Image data as bytes
            filter_type: Type of filter ('grayscale', 'sepia', 'blur', etc.)
            
        Returns:
            bytes: Filtered image as bytes
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            if filter_type == 'grayscale':
                filtered_image = image.convert('L').convert('RGB')
            elif filter_type == 'sepia':
                filtered_image = ImageService._apply_sepia_filter(image)
            else:
                raise ValueError(f"Unsupported filter type: {filter_type}")
            
            output = io.BytesIO()
            filtered_image.save(output, format=image.format)
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to apply filter: {str(e)}")
    
    @staticmethod
    def _apply_sepia_filter(image):
        """Apply sepia filter to an image."""
        pixels = image.load()
        width, height = image.size
        
        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y][:3]
                
                # Sepia formula
                new_r = int(0.393 * r + 0.769 * g + 0.189 * b)
                new_g = int(0.349 * r + 0.686 * g + 0.168 * b)
                new_b = int(0.272 * r + 0.534 * g + 0.131 * b)
                
                # Clamp values to 0-255 range
                new_r = min(255, new_r)
                new_g = min(255, new_g)
                new_b = min(255, new_b)
                
                pixels[x, y] = (new_r, new_g, new_b)
        
        return image
    
    @staticmethod
    def add_watermark(image_bytes, text, position='bottom-right', opacity=0.5):
        """
        Add text watermark to an image.
        
        Args:
            image_bytes: Image data as bytes
            text: Watermark text
            position: Position of watermark
            opacity: Watermark opacity (0.0 to 1.0)
            
        Returns:
            bytes: Watermarked image as bytes
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Create a transparent overlay
            overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Try to use a font, fallback to default if not available
            try:
                font_size = max(20, image.width // 30)
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Calculate text position
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            margin = 20
            if position == 'top-left':
                x, y = margin, margin
            elif position == 'top-right':
                x, y = image.width - text_width - margin, margin
            elif position == 'bottom-left':
                x, y = margin, image.height - text_height - margin
            elif position == 'bottom-right':
                x, y = image.width - text_width - margin, image.height - text_height - margin
            elif position == 'center':
                x, y = (image.width - text_width) // 2, (image.height - text_height) // 2
            else:
                x, y = image.width - text_width - margin, image.height - text_height - margin
            
            # Draw text with specified opacity
            alpha = int(255 * opacity)
            draw.text((x, y), text, font=font, fill=(255, 255, 255, alpha))
            
            # Composite the overlay onto the original image
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            watermarked = Image.alpha_composite(image, overlay)
            
            # Convert back to RGB if original was RGB
            if image.mode == 'RGB':
                watermarked = watermarked.convert('RGB')
            
            output = io.BytesIO()
            watermarked.save(output, format='PNG' if image.mode == 'RGBA' else 'JPEG')
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to add watermark: {str(e)}")
    
    @staticmethod
    def change_format(image_bytes, new_format, quality=85):
        """
        Change image format.
        
        Args:
            image_bytes: Image data as bytes
            new_format: Target format ('JPEG', 'PNG', 'WEBP', etc.)
            quality: Image quality for lossy formats
            
        Returns:
            bytes: Converted image as bytes
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Handle transparency for JPEG conversion
            if new_format.upper() == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            output = io.BytesIO()
            
            if new_format.upper() in ['JPEG', 'WEBP']:
                image.save(output, format=new_format.upper(), quality=quality, optimize=True)
            else:
                image.save(output, format=new_format.upper())
            
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to change format: {str(e)}")
    
    @staticmethod
    def compress_image(image_bytes, quality=85):
        """
        Compress an image.
        
        Args:
            image_bytes: Image data as bytes
            quality: Compression quality (1-100)
            
        Returns:
            bytes: Compressed image as bytes
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            output = io.BytesIO()
            
            if image.format == 'PNG':
                # PNG compression through optimization
                image.save(output, format='PNG', optimize=True)
            else:
                # JPEG compression with quality setting
                if image.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                
                image.save(output, format='JPEG', quality=quality, optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to compress image: {str(e)}")