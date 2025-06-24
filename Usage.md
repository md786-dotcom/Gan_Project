# Image Processing Service - Usage Guide

This guide will help you set up and use the Image Processing Service on both Mac and Windows systems.

**🎉 NEW: Complete Web Interface!** The service now features a beautiful, user-friendly web interface that requires no configuration. Simply run the app and access it through your browser!

## Table of Contents
- [Quick Start (Recommended)](#quick-start-recommended)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Service](#running-the-service)
- [Using the Web Interface](#using-the-web-interface)
- [Using the API](#using-the-api)
- [Troubleshooting](#troubleshooting)

## Quick Start (Recommended)

**Get started in 3 simple steps - no configuration required!**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python app.py

# 3. Open your browser and go to:
# http://localhost:5000
```

That's it! 🎉 The service will automatically:
- ✅ Create all necessary directories
- ✅ Initialize the database 
- ✅ Set up secure file storage
- ✅ Start the web server

**Features available immediately:**
- 🖼️ Upload images via drag-and-drop
- ✨ Apply transformations with visual controls
- 👤 User registration and authentication
- 📱 Beautiful responsive web interface
- 🔒 Secure local file storage (no cloud setup needed)

## Prerequisites

### Required Software

#### For Mac:
1. **Python 3.8+** (built-in on macOS 10.15+)
   ```bash
   # Check Python version
   python3 --version
   
   # If not installed, install via Homebrew
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install python
   ```

2. **pip** (comes with Python)
   ```bash
   python3 -m pip --version
   ```

#### For Windows:
1. **Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - ⚠️ **Important**: Check "Add Python to PATH" during installation
   
2. **Git** (optional, for cloning)
   - Download from [git-scm.com](https://git-scm.com/download/win)

### AWS Account Setup (Required)
1. Create an AWS account at [aws.amazon.com](https://aws.amazon.com)
2. Create an S3 bucket for image storage
3. Create IAM user with S3 permissions
4. Get Access Key ID and Secret Access Key

## Installation

### Step 1: Download the Project

#### Option A: Using Git (Recommended)
```bash
# Mac/Linux
git clone <repository-url>
cd coursera-github-project

# Windows (Command Prompt)
git clone <repository-url>
cd coursera-github-project
```

#### Option B: Download ZIP
1. Download the project ZIP file
2. Extract to a folder (e.g., `coursera-github-project`)
3. Open terminal/command prompt in that folder

### Step 2: Create Virtual Environment

#### Mac/Linux:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv)
```

#### Windows:
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Your prompt should now show (venv)
```

### Step 3: Install Dependencies

```bash
# Install required packages (same for Mac/Windows)
pip install -r requirements.txt
```

**If you encounter installation issues:**

#### Mac:
```bash
# Install Xcode command line tools if needed
xcode-select --install

# If Pillow fails to install
pip install --upgrade pip
pip install Pillow
```

#### Windows:
```cmd
# Upgrade pip first
python -m pip install --upgrade pip

# If Visual C++ errors occur, install Microsoft C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

## Configuration

### Step 1: Create Environment File

#### Mac/Linux:
```bash
cp .env.example .env
```

#### Windows:
```cmd
copy .env.example .env
```

### Step 2: Edit Configuration

Open the `.env` file in a text editor and update the following:

```env
# Basic Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-super-secure-secret-key-here-change-this
JWT_SECRET_KEY=your-jwt-secret-key-here-change-this

# Database (SQLite for development)
DATABASE_URL=sqlite:///image_service.db

# AWS S3 Configuration (REQUIRED)
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name

# Optional Settings
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
MAX_CONTENT_LENGTH=10485760
```

**🔐 Security Note**: Never commit the `.env` file to version control!

### Step 3: AWS S3 Setup

1. **Create S3 Bucket:**
   - Go to AWS S3 Console
   - Click "Create bucket"
   - Choose a unique bucket name
   - Select your preferred region
   - Keep default settings for development

2. **Create IAM User:**
   - Go to AWS IAM Console
   - Create new user with programmatic access
   - Attach policy: `AmazonS3FullAccess` (or create custom policy)
   - Save Access Key ID and Secret Access Key

3. **Test AWS Connection:**
   ```bash
   # Mac/Linux
   python3 -c "import boto3; print('AWS SDK installed successfully')"
   
   # Windows
   python -c "import boto3; print('AWS SDK installed successfully')"
   ```

## Running the Service

### Step 1: Initialize Database

#### Mac/Linux:
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Initialize database
python3 run.py init_db
```

#### Windows:
```cmd
# Make sure virtual environment is activated
venv\Scripts\activate

# Initialize database
python run.py init_db
```

### Step 2: Start the Server

#### Mac/Linux:
```bash
# Development mode
python3 run.py

# Production mode (optional)
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

#### Windows:
```cmd
# Development mode
python run.py

# Production mode (install gunicorn first)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

**✅ Success Indicators:**
- Server starts without errors
- Console shows: "Image Processing Service is ready!"
- Console shows: "Open your browser and go to: http://localhost:5000"
- Visit http://localhost:5000 - should show the beautiful landing page

## Using the Web Interface

### Getting Started with the Web Interface

1. **Open your browser** and navigate to `http://localhost:5000`
2. **Sign up** for a new account or **sign in** if you already have one
3. Start uploading and processing images immediately!

### Web Interface Features

#### 🏠 **Landing Page**
- Beautiful introduction to the service
- Quick signup/login with modal dialogs
- Feature overview and instructions
- No registration required to explore

#### 📊 **Dashboard**
- Welcome message with your name
- Statistics about your images (total count, processed images, storage used)
- Quick action buttons for common tasks
- Recent images gallery with hover actions
- One-click access to transform, download, or delete images

#### 📤 **Upload Page**
- **Drag-and-drop upload zone** - just drop your images!
- **Click to browse** - traditional file picker
- **Real-time preview** - see your image before uploading
- **Progress tracking** - watch upload progress in real-time
- **File validation** - automatic format and size checking
- **Recent uploads** - quick access to your latest images

#### 🎨 **Transform Page**
- **Live image preview** with original image information
- **Intuitive controls** organized in panels:
  - **Resize & Dimensions**: Width, height with aspect ratio lock
  - **Rotate & Flip**: 90° rotation buttons and flip controls
  - **Filters & Effects**: Grayscale, sepia, and more
  - **Watermarks**: Custom text with position and opacity
  - **Format & Quality**: Convert formats and adjust compression
- **Real-time preview** - see filter changes immediately
- **Keyboard shortcuts** for power users (G for grayscale, S for sepia, R to reset)
- **Transformation history** - see what's been applied to images

#### 🖼️ **Gallery Page**
- **Grid view** of all your images
- **Hover actions** for quick transform, download, or delete
- **Full-screen viewer** - click any image to view larger
- **Batch operations** - select multiple images for actions
- **Search and filter** - find images quickly

#### ❓ **Help Page**
- **Complete user guide** with step-by-step instructions
- **Keyboard shortcuts** reference
- **FAQ section** with common questions
- **Feature explanations** with examples
- **Troubleshooting tips**

### Web Interface Tips

#### 🔥 **Power User Features**
- **Keyboard shortcuts**: 
  - `U` - Go to upload page
  - `G` - Go to gallery
  - `G` (on transform page) - Apply grayscale
  - `S` (on transform page) - Apply sepia
  - `R` (on transform page) - Reset form

#### 📱 **Mobile Friendly**
- Fully responsive design works on phones and tablets
- Touch-friendly controls and buttons
- Optimized layouts for small screens

#### 🔒 **Security Features**
- All uploads are private to your account
- Secure authentication with session management
- Protected against common web vulnerabilities
- Files stored securely on the server

#### 🚀 **Performance**
- Fast image processing with progress indicators
- Efficient thumbnail generation
- Optimized file storage and retrieval
- Smooth animations and transitions

## Using the API

### Method 1: Using cURL (Command Line)

#### 1. Register a New User
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

**Expected Response:**
```json
{
  "message": "User created successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

#### 2. Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

#### 3. Upload an Image
```bash
# Replace YOUR_JWT_TOKEN with the token from login response
curl -X POST http://localhost:5000/api/images/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/your/image.jpg"
```

#### 4. List Your Images
```bash
curl -X GET http://localhost:5000/api/images/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 5. Transform an Image
```bash
curl -X POST http://localhost:5000/api/images/1/transform \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "width": 800,
    "height": 600,
    "rotate": 90,
    "filter": "grayscale",
    "watermark": {
      "text": "My Watermark",
      "position": "bottom-right",
      "opacity": 0.7
    }
  }'
```

### Method 2: Using Postman (GUI)

1. **Download Postman** from [postman.com](https://www.postman.com/)

2. **Create a Collection** named "Image Processing Service"

3. **Add Requests:**

   **Register User:**
   - Method: POST
   - URL: `http://localhost:5000/api/auth/signup`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
     ```json
     {
       "email": "user@example.com",
       "password": "password123"
     }
     ```

   **Upload Image:**
   - Method: POST
   - URL: `http://localhost:5000/api/images/upload`
   - Headers: `Authorization: Bearer YOUR_JWT_TOKEN`
   - Body: form-data with key `file` and select your image file

### Method 3: Using Python Script

Create a test script `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# 1. Register user
def register_user(email, password):
    response = requests.post(f"{BASE_URL}/api/auth/signup", 
                           json={"email": email, "password": password})
    return response.json()

# 2. Login user
def login_user(email, password):
    response = requests.post(f"{BASE_URL}/api/auth/login", 
                           json={"email": email, "password": password})
    return response.json()

# 3. Upload image
def upload_image(token, image_path):
    headers = {"Authorization": f"Bearer {token}"}
    with open(image_path, 'rb') as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/api/images/upload", 
                               headers=headers, files=files)
    return response.json()

# 4. Transform image
def transform_image(token, image_id, transformations):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/api/images/{image_id}/transform", 
                           headers=headers, json=transformations)
    return response.json()

# Example usage
if __name__ == "__main__":
    # Register and login
    user_data = register_user("test@example.com", "password123")
    token = user_data["access_token"]
    
    # Upload image
    image_data = upload_image(token, "path/to/your/image.jpg")
    image_id = image_data["image"]["id"]
    
    # Transform image
    transformations = {
        "width": 800,
        "height": 600,
        "filter": "grayscale",
        "watermark": {
            "text": "Test Watermark",
            "position": "bottom-right"
        }
    }
    
    result = transform_image(token, image_id, transformations)
    print(json.dumps(result, indent=2))
```

Run the script:
```bash
python test_api.py
```

## Transformation Examples

### Resize Image
```json
{
  "width": 800,
  "height": 600,
  "maintain_aspect_ratio": true
}
```

### Apply Multiple Transformations
```json
{
  "width": 1200,
  "rotate": 90,
  "filter": "sepia",
  "watermark": {
    "text": "© 2024 My Company",
    "position": "bottom-right",
    "opacity": 0.8
  },
  "format": "png",
  "quality": 95
}
```

### Crop and Compress
```json
{
  "width": 500,
  "height": 500,
  "maintain_aspect_ratio": false,
  "compress": true,
  "quality": 70
}
```

## Troubleshooting

### Common Issues

#### 1. "Python not found" (Windows)
**Solution:** Reinstall Python and check "Add Python to PATH"

#### 2. "Permission denied" (Mac)
**Solution:** Use `python3` instead of `python`

#### 3. "Module not found" errors
**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### 4. "AWS credentials not found"
**Solution:** Check your `.env` file has correct AWS credentials:
```env
AWS_ACCESS_KEY_ID=your-key-here
AWS_SECRET_ACCESS_KEY=your-secret-here
S3_BUCKET_NAME=your-bucket-name
```

#### 5. "Failed to upload to S3"
**Solutions:**
- Verify S3 bucket exists and is accessible
- Check IAM user has S3 permissions
- Ensure bucket name is correct in `.env`

#### 6. Port already in use
**Solution:**
```bash
# Find and kill process using port 5000
# Mac/Linux
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

#### 7. Database errors
**Solution:**
```bash
# Delete and recreate database
rm image_service.db  # Mac/Linux
del image_service.db # Windows

# Reinitialize
python run.py init_db
```

### Getting Help

1. **Check server logs** in the terminal where you ran `python run.py`
2. **Test health endpoint**: Visit http://localhost:5000/health
3. **Verify environment**: Check `.env` file configuration
4. **Test AWS connection**: Use AWS CLI or boto3 to verify credentials

## Performance Tips

1. **Image Size**: Keep uploaded images under 10MB for optimal performance
2. **Batch Operations**: Process multiple transformations in one request
3. **Caching**: Frequently accessed images are automatically cached
4. **Quality vs Size**: Use quality 70-85 for good balance

## Security Best Practices

1. **Never share your JWT tokens**
2. **Use strong passwords** (min 6 characters)
3. **Keep `.env` file secure** and never commit it
4. **Rotate AWS credentials** regularly
5. **Use HTTPS** in production

## Next Steps

1. **Deploy to production**: Use services like Heroku, AWS, or DigitalOcean
2. **Set up monitoring**: Add logging and error tracking
3. **Scale storage**: Consider CDN for faster image delivery
4. **Add features**: Implement batch processing, webhooks, or admin panel

---

**Need help?** Check the main [README.md](README.md) for more technical details or create an issue in the repository.