import os
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from models import db, Image
from flask_restx import Namespace, Resource, fields

delete_ns = Namespace("delete", description="Image delete endpoints")


with open("config.json") as config_file:
    config = json.load(config_file)
    UPLOAD_FOLDER = config.get("upload_folder")

def init_delete_routes(app, api):
    api.add_namespace(delete_ns)

    delete_ns.authorizations = {
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "JWT authorization header. Example: 'Bearer <JWT_TOKEN>'"
        }
    }

    @delete_ns.route('/delete/<int:id>')
    class DeleteCatImage(Resource):
        @jwt_required()
        @delete_ns.doc(security="BearerAuth")
        @delete_ns.response(200, 'Cat successfully deleted')
        @delete_ns.response(404, 'Cat not found')
        @delete_ns.response(401, 'Unauthorized')
        @delete_ns.response(500, 'Internal server error')
        def delete(self, id):
            user_id = get_jwt_identity()
            image = Image.query.filter_by(id=id).first()
            if image is None:
                return {"error": "Cat not found"}, 404
            if image.user_id != int(user_id):
                return {"error": "Unauthorized"}, 401
            for filename in os.listdir(UPLOAD_FOLDER):
                if filename.startswith(f"{id}."):
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    try:
                        os.remove(file_path)
                        db.session.delete(image)
                        db.session.commit()
                        return {
                            "message": "Cat successfully deleted",
                            "id": id
                        }, 200
                    except OSError as e:
                        return {"error": f"Failed to delete cat: {str(e)}"}, 500
            return {"error": "Cat not found"}, 404
