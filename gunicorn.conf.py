# Gunicorn configuration file
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = 2
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = 'info'
accesslog = '-'
errorlog = '-'

# Process naming
proc_name = 'pixlz_image_processor'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Application
preload_app = True