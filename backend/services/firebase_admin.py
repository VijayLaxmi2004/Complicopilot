import firebase_admin
from firebase_admin import credentials, auth as fb_auth
import os

# Check if we're in development mode
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "true").lower() == "true"

if not firebase_admin._apps:
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # For development: initialize without credentials
        # This allows the app to start but Firebase features won't work
        firebase_admin.initialize_app()

def verify_firebase_token(id_token):
    # In development mode, skip actual verification for easier testing
    if DEVELOPMENT_MODE and os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is None:
        print("DEVELOPMENT MODE: Skipping Firebase token verification")
        # Return a mock user for development
        return {
            "uid": "dev-user-123",
            "email": "dev@example.com",
            "name": "Development User"
        }
    
    try:
        decoded_token = fb_auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Firebase token verification failed: {e}")
        return None
    