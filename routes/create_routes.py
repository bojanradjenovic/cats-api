from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
import os
from werkzeug.utils import secure_filename
from models import db, Image
from werkzeug.datastructures import FileStorage
from flask_restx import Namespace, Resource, fields, reqparse
from PIL import Image as PILImage
import io

create_ns = Namespace("create", description="Image upload endpoints")

image_model = create_ns.model('Image', {
    'id': fields.Integer(required=True, description='Image ID'),
    'filename': fields.String(required=True, description='Filename of the image'),
    'name': fields.String(required=True, description='Name of the image'),
    'description': fields.String(required=True, description='Description of the image'),
    'user_id': fields.Integer(required=True, description='ID of the user who uploaded the image'),
    'username': fields.String(required=True, description='Username of the user who uploaded the image'),
    'upload_time': fields.String(required=True, description='Time when the image was uploaded', example="2025-01-29 18:32:19")
})

upload_parser = reqparse.RequestParser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True, help='Image file to upload')
upload_parser.add_argument('name', type=str, required=True, help='Name of the image')
upload_parser.add_argument('description', type=str, required=False, help='Description of the image')

with open("config.json") as config_file:
    config = json.load(config_file)
    UPLOAD_FOLDER = config.get("upload_folder")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ID_FILE = os.path.join(UPLOAD_FOLDER, 'id.txt')

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
def strip_metadata(image_file):
    try:
        img = PILImage.open(image_file)
        data = list(img.getdata())

        img_no_metadata = PILImage.new(img.mode, img.size)
        img_no_metadata.putdata(data)

        temp_image = io.BytesIO()
        img_no_metadata.save(temp_image, format=img.format)
        temp_image.seek(0)
        return temp_image
    except Exception as e:
        print(f"Error stripping metadata: {e}")
        return image_file
def init_create_routes(app, api):
    api.add_namespace(create_ns)

    create_ns.authorizations = {
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "JWT authorization header. Example: 'Bearer <JWT_TOKEN>'"
        }
    }

    @create_ns.route('/upload')
    class UploadCatImage(Resource):
        @jwt_required()
        @create_ns.expect(upload_parser)
        @create_ns.doc(security="BearerAuth")
        @create_ns.response(201, 'Cat successfully uploaded', model=image_model)
        @create_ns.response(400, 'Bad request - Missing file or invalid data')
        @create_ns.response(401, 'Unauthorized - Missing or invalid token')
        def post(self):
            args = upload_parser.parse_args()

            file = args['file']
            if not file:
                return {"error": "No file selected for uploading"}, 400

            if not allowed_file(file.filename):
                return {"error": "Allowed file types are png, jpg, jpeg, gif"}, 400

            name = args['name']
            description = args['description']
            user_id = get_jwt_identity()

            file_id = next_id()
            file_extension = secure_filename(file.filename).rsplit('.', 1)[1].lower()
            filename = f"{file_id}.{file_extension}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            cleaned_file = strip_metadata(file)
            with open(file_path, "wb") as f:
                f.write(cleaned_file.read())


            new_image = Image(
                id=file_id,
                filename=filename,
                user_id=user_id,
                name=name,
                description=description
            )
            db.session.add(new_image)
            db.session.commit()
            image_data = {
                'id': new_image.id,
                'filename': new_image.filename,
                'name': new_image.name,
                'description': new_image.description,
                'user_id': new_image.user_id,
                'username': new_image.user.username,
                'upload_time': new_image.upload_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            return image_data, 201