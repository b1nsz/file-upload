import os
import uuid
import logging
from werkzeug.utils import secure_filename
from extensions import db  # use extensions instead of app
from models.uploaded_file import UploadedFile


# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt'}

def allowed_file(filename):
    """Check if file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, base_folder):
    """Save a new file and create a database record."""
    if not allowed_file(file.filename):
        raise ValueError('File type not allowed')

    # Ensure folder exists
    os.makedirs(base_folder, exist_ok=True)

    # Secure filename and create a unique name
    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    save_path = os.path.join(base_folder, unique_name)

    # Save file to disk
    file.save(save_path)

    # Create DB record
    new_file = UploadedFile(filename=unique_name, file_path=save_path)
    db.session.add(new_file)
    db.session.commit()

    logging.info(f"File saved: {save_path}")
    return new_file

def update_file(file_id, new_file, base_folder):
    """Update an existing file record with a new file."""
    existing = UploadedFile.query.get(file_id)
    if not existing:
        raise ValueError('File not found')

    # Remove old file
    if os.path.exists(existing.file_path):
        os.remove(existing.file_path)

    # Save new file
    filename = secure_filename(new_file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    save_path = os.path.join(base_folder, unique_name)
    os.makedirs(base_folder, exist_ok=True)
    new_file.save(save_path)

    # Update DB record
    existing.filename = unique_name
    existing.file_path = save_path
    db.session.commit()

    logging.info(f"File updated: {save_path}")
    return existing

def delete_file(file_id):
    """Delete a file record and remove the file from disk."""
    file_record = UploadedFile.query.get(file_id)
    if not file_record:
        raise ValueError('File not found')

    # Remove file from disk
    if os.path.exists(file_record.file_path):
        os.remove(file_record.file_path)

    # Remove DB record
    db.session.delete(file_record)
    db.session.commit()
    logging.info(f"File deleted: {file_record.file_path}")
