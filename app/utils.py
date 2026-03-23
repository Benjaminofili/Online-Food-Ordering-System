import cloudinary
import cloudinary.uploader
from flask import current_app

def upload_file_to_cloudinary(file, resource_type="auto"):
    """
    Uploads a file object to Cloudinary and returns the secure URL.
    Returns None if no file is provided or an error occurs.
    """
    if not file or file.filename == '':
        return None
    
    try:
        # The CLOUDINARY_URL environment variable is automatically used if present.
        # We enforce a strict 15-second timeout so Gunicorn doesn't hang (causes 502 error)
        upload_result = cloudinary.uploader.upload(file, resource_type=resource_type, timeout=15)
        return upload_result.get('secure_url')
    except Exception as e:
        current_app.logger.error(f"Error uploading to cloudinary: {e}")
        return None
