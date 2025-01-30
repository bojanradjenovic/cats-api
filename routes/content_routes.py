from flask import send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from models import User, Image
from flask_restx import Namespace, Resource, fields

content_ns = Namespace("content", description="Content endpoints")

image_model = content_ns.model('Image', {
    'id': fields.Integer(required=True, description='Image ID'),
    'filename': fields.String(required=True, description='Filename of the image'),
    'name': fields.String(required=True, description='Name of the image'),
    'description': fields.String(required=True, description='Description of the image'),
    'user_id': fields.Integer(required=True, description='ID of the user who uploaded the image'),
    'username': fields.String(required=True, description='Username of the user who uploaded the image'),
    'upload_time': fields.String(required=True, description='Time when the image was uploaded', example="2025-01-29 18:32:19")
})

images_model = content_ns.model('Images', {
    'images': fields.List(fields.Nested(image_model), description='List of images', required=True)
})

with open("config.json") as config_file:
    config = json.load(config_file)
    UPLOAD_FOLDER = config.get("upload_folder")

def init_content_routes(app, api):
    api.add_namespace(content_ns)

    content_ns.authorizations = {
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "JWT authorization header. Example: 'Bearer <JWT_TOKEN>'"
        }
    }

    content_ns.models['Images'] = images_model

    @content_ns.route('/user/images')
    class GetUserImages(Resource):
        @jwt_required()
        @content_ns.doc(security="BearerAuth")
        @content_ns.response(200, 'Successfully retrieved user images', model=images_model)
        @content_ns.response(404, 'User not found')
        @content_ns.response(401, 'Unauthorized: Missing or invalid token')
        def get(self):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return {"error": "User not found"}, 404

            images = [
                {
                    "id": image.id,
                    "filename": image.filename,
                    "name": image.name,
                    "description": image.description,
                    "upload_time": image.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "username": image.user.username,
                    "user_id": image.user_id
                }
                for image in user.images
            ]
            return {"images": images}, 200

    @content_ns.route('/images')
    class GetAllImages(Resource):
        @content_ns.response(200, 'Successfully retrieved all images', model=images_model)
        @content_ns.response(404, 'No images found')
        def get(self):
            images = Image.query.all()
            if not images:
                return {"message": "No images found"}, 404

            images_data = [
                {
                    "id": image.id,
                    "filename": image.filename,
                    "name": image.name,
                    "description": image.description,
                    "upload_time": image.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "username": image.user.username,
                    "user_id": image.user_id
                }
                for image in images
            ]
            return {"images": images_data}, 200

    @content_ns.route('/images/<int:id>')
    class GetImageById(Resource):
        @content_ns.response(200, 'Successfully retrieved image', model=image_model)
        @content_ns.response(404, 'Image not found')
        def get(self, id):
            image = Image.query.filter_by(id=id).first()

            if not image:
                return {"error": "Image not found"}, 404

            image_data = {
                "id": image.id,
                "filename": image.filename,
                "name": image.name,
                "description": image.description,
                "upload_time": image.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
                "username": image.user.username,
                "user_id": image.user_id
            }
            return image_data, 200

    @content_ns.route('/images/<int:id>/file')
    class GetImageFile(Resource):
        @content_ns.response(200, 'Successfully retrieved image file')
        @content_ns.response(404, 'Image not found')
        def get(self, id):
            image = Image.query.filter_by(id=id).first()

            if not image:
                return {"error": "Image not found"}, 404

            return send_from_directory(UPLOAD_FOLDER, image.filename)
