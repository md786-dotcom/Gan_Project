# Image Processing Service

A backend service for image processing similar to Cloudinary, built with Flask and Python.

## Features

### User Authentication
- User registration and login
- JWT-based authentication
- Secure password hashing

### Image Management
- Upload images to cloud storage (AWS S3)
- List all user images with pagination
- Retrieve specific image details
- Delete images

### Image Transformations
- **Resize**: Change image dimensions with aspect ratio preservation
- **Crop**: Extract specific portions of images
- **Rotate**: Rotate images by specified angles
- **Flip**: Horizontal and vertical flipping
- **Filters**: Apply grayscale, sepia, and other filters
- **Watermark**: Add text watermarks with customizable position and opacity
- **Format Conversion**: Convert between JPEG, PNG, WebP formats
- **Compression**: Optimize image file sizes

## Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **Image Processing**: Pillow (PIL)
- **Cloud Storage**: AWS S3 (boto3)
- **Database**: SQLite (development), PostgreSQL (production)
- **Rate Limiting**: Flask-Limiter
- **API Documentation**: Built-in Flask routes

## Project Structure

```
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # Database models
│   │   ├── user.py         # User model
│   │   └── image.py        # Image model
│   ├── routes/             # API endpoints
│   │   ├── auth.py         # Authentication routes
│   │   └── images.py       # Image management routes
│   ├── services/           # Business logic
│   │   ├── s3_service.py   # AWS S3 integration
│   │   └── image_service.py # Image processing
│   └── utils/              # Helper functions
│       ├── validators.py   # Input validation
│       └── helpers.py      # Utility functions
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── run.py                 # Application entry point
```

## Setup Instructions

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd coursera-github-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# Required variables:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - S3_BUCKET_NAME
# - SECRET_KEY
# - JWT_SECRET_KEY
```

### 3. Database Setup

```bash
# Initialize database
python run.py init_db
```

### 4. Run the Application

```bash
# Development mode
python run.py

# Production mode with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Image Management
- `POST /api/images/upload` - Upload image
- `GET /api/images/` - List user images (with pagination)
- `GET /api/images/<id>` - Get specific image
- `DELETE /api/images/<id>` - Delete image
- `POST /api/images/<id>/transform` - Apply transformations

### Health Check
- `GET /health` - Service health status

## API Usage Examples

### User Registration
```bash
curl -X POST http://localhost:5000/api/auth/signup \\
  -H "Content-Type: application/json" \\
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Image Upload
```bash
curl -X POST http://localhost:5000/api/images/upload \\
  -H "Authorization: Bearer <your-jwt-token>" \\
  -F "file=@/path/to/image.jpg"
```

### Image Transformation
```bash
curl -X POST http://localhost:5000/api/images/1/transform \\
  -H "Authorization: Bearer <your-jwt-token>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "width": 800,
    "height": 600,
    "rotate": 90,
    "filter": "grayscale",
    "watermark": {
      "text": "Sample Watermark",
      "position": "bottom-right",
      "opacity": 0.7
    }
  }'
```

## Transformation Parameters

### Resize
- `width`: Target width in pixels
- `height`: Target height in pixels
- `maintain_aspect_ratio`: Boolean (default: true)

### Rotate
- `rotate`: Angle in degrees (0, 90, 180, 270)

### Flip
- `flip`: Direction ("horizontal" or "vertical")

### Filters
- `filter`: Filter type ("grayscale", "sepia")

### Watermark
- `watermark.text`: Watermark text
- `watermark.position`: Position ("top-left", "top-right", "bottom-left", "bottom-right", "center")
- `watermark.opacity`: Opacity (0.0 to 1.0)

### Format & Compression
- `format`: Target format ("jpeg", "png", "webp")
- `quality`: Compression quality (1-100)
- `compress`: Enable compression

## Security Features

- Password hashing with bcrypt
- JWT authentication for API access
- File type validation for uploads
- Rate limiting to prevent abuse
- Input validation and sanitization
- Secure file naming and storage

## Error Handling

The API returns appropriate HTTP status codes and error messages:
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (authentication required)
- `404`: Not Found (resource doesn't exist)
- `409`: Conflict (resource already exists)
- `500`: Internal Server Error

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
```

### Linting
```bash
flake8 app/
```

## Deployment

### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

### Environment Variables for Production
- Set `FLASK_ENV=production`
- Use PostgreSQL for `DATABASE_URL`
- Configure proper AWS credentials
- Set secure `SECRET_KEY` and `JWT_SECRET_KEY`
- Configure Redis for caching (optional)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License