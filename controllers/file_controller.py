import uuid
import logging
from flask import Blueprint, request, jsonify, send_file, current_app
from services.file_service import save_file, update_file, delete_file
from models.uploaded_file import UploadedFile

file_bp = Blueprint('file_bp', __name__)

# ---------------------------
# POST — Upload file
# ---------------------------
@file_bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'No file uploaded'}), 400

        file = request.files['file']
        # Use current_app instead of importing app
        folder = f"{current_app.config['UPLOAD_FOLDER']}/{uuid.uuid4().hex}"
        uploaded = save_file(file, folder)

        return jsonify({
            'message': 'Upload successful',
            'id': uploaded.id,
            'path': uploaded.file_path
        }), 201

    except Exception as e:
        logging.error(f"Upload error: {e}")
        return jsonify({'message': str(e)}), 400

# ---------------------------
# GET — Retrieve file info or download
# ---------------------------
@file_bp.route('/file/<int:file_id>', methods=['GET'])
def get_file(file_id):
    try:
        file = UploadedFile.query.get(file_id)
        if not file:
            return jsonify({'message': 'File not found'}), 404

        return send_file(file.file_path, as_attachment=True)

    except Exception as e:
        logging.error(f"Get error: {e}")
        return jsonify({'message': str(e)}), 400

# ---------------------------
# PUT — Update file
# ---------------------------
@file_bp.route('/file/<int:file_id>', methods=['PUT'])
def update_existing_file(file_id):
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'No file provided'}), 400

        file = request.files['file']
        updated = update_file(file_id, file, current_app.config['UPLOAD_FOLDER'])

        return jsonify({
            'message': 'File updated successfully',
            'path': updated.file_path
        }), 200

    except Exception as e:
        logging.error(f"Update error: {e}")
        return jsonify({'message': str(e)}), 400

# ---------------------------
# DELETE — Delete file
# ---------------------------
@file_bp.route('/file/<int:file_id>', methods=['DELETE'])
def delete_existing_file(file_id):
    try:
        delete_file(file_id)
        return jsonify({'message': 'File deleted successfully'}), 200

    except Exception as e:
        logging.error(f"Delete error: {e}")
        return jsonify({'message': str(e)}), 400
