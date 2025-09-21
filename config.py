import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    # Redirect URL where incoming requests will be forwarded
    REDIRECT_URL = os.environ.get('REDIRECT_URL', 'http://localhost:8080/webhook')
    
    # Port for the webhook to listen on
    LISTEN_PORT = int(os.environ.get('LISTEN_PORT', 5000))
    
    # Debug mode
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Host to bind to (0.0.0.0 means accessible from outside localhost)
    HOST = os.environ.get('HOST', '0.0.0.0')