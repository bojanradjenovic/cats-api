from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
import os
from werkzeug.utils import secure_filename
from models import db, Image
with open("config.json") as config_file:
    config = json.load(config_file)
    UPLOAD_FOLDER = config.get("upload_folder")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ID_FILE = os.path.join(UPLOAD_FOLDER, 'id.txt')

# Initialize the ID file if it doesn't exist
if not os.path.exists(ID_FILE):
    with open(ID_FILE, 'w') as f:
        f.write('0')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_last_id():
    with open(ID_FILE, 'r') as f:
        return int(f.read())

def next_id():
    id = get_last_id()
    with open(ID_FILE, 'w') as f:
        f.write(str(id + 1))
    return id + 1

def init_create_routes(app):
    @app.route('/upload', methods=['POST'])
    @jwt_required()
    def upload_cat_image():
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected for uploading"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Allowed file types are png, jpg, jpeg, gif"}), 400

        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            return jsonify({"error": "Name is required"}), 400
        if not description:
            return jsonify({"error": "Description is required"}), 400

        user_id = get_jwt_identity()

        # Generate a unique ID for the image
        file_id = next_id()
        file_extension = secure_filename(file.filename).rsplit('.', 1)[1].lower()
        filename = f"{file_id}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        file.save(file_path)

        # Save image details to the database
        image = Image(
            id=file_id,
            filename=filename,
            user_id=user_id,
            name=name,
            description=description
        )
        db.session.add(image)
        db.session.commit()

        return jsonify({
            "message": "Cat successfully uploaded",
            "id": file_id,
            "name": name,
            "description": description
        }), 201
