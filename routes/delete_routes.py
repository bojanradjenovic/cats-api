import os
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Image
UPLOAD_FOLDER = 'cats'

def init_delete_routes(app):
    @app.route('/delete/<int:id>', methods=['DELETE'])
    @jwt_required()
    def delete_cat_image(id):
        user_id = get_jwt_identity()
        image = Image.query.filter_by(id=id).first()
        if image is None:
            return jsonify({"error": "Cat not found"}), 404
        if image.user_id != int(user_id):
            return jsonify({"error": "Unauthorized"}), 401
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.startswith(f"{id}."):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    os.remove(file_path)
                    db.session.delete(image)
                    db.session.commit()
                    return jsonify({"message": "Cat successfully deleted", "id": id}), 200
                except OSError as e:
                    return jsonify({"error": f"Failed to delete cat: {str(e)}"}), 500
            return jsonify({"error": "Cat not found"}), 404
