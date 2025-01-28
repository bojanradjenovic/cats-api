from flask import jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Image

def init_content_routes(app):
    @app.route('/user/images', methods=['GET'])
    @jwt_required()
    def get_user_images():
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        images = [
            {"id": image.id, "filename": image.filename, "name": image.name, "description": image.description, "upload_time": image.upload_time}
            for image in user.images
        ]
        return jsonify({"images": images}), 200
    @app.route('/images', methods=['GET'])
    @jwt_required()
    def get_all_images():
        # Query all images from the database
        images = Image.query.all()
        if not images:
            return jsonify({"message": "No images found"}), 404

        # Return a list of image details
        images_data = [
            {"id": image.id, "filename": image.filename, "name": image.name, "description": image.description, "user_id": image.user_id}
            for image in images
        ]
        return jsonify(images_data), 200

    @app.route('/images/<int:id>', methods=['GET'])
    @jwt_required()
    def get_image_by_id(id):
        # Query the image by its ID
        image = Image.query.filter_by(id=id).first()

        if not image:
            return jsonify({"error": "Image not found"}), 404

        # Return image details and serve the file
        image_data = {"id": image.id, "filename": image.filename, "name": image.name, "description": image.description, "user_id": image.user_id}
        return jsonify(image_data), 200

    @app.route('/images/<int:id>/file', methods=['GET'])
    @jwt_required()
    def get_image_file(id):
        # Query the image by its ID
        image = Image.query.filter_by(id=id).first()

        if not image:
            return jsonify({"error": "Image not found"}), 404

        # Serve the image file from the UPLOAD_FOLDER
        return send_from_directory('cats', image.filename)
