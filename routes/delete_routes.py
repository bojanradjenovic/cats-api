import os
from flask import jsonify

UPLOAD_FOLDER = 'cats'

def init_delete_routes(app):
    @app.route('/delete/<int:id>', methods=['DELETE'])
    def delete_cat_image(id):
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.startswith(f"{id}."):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    os.remove(file_path)
                    return jsonify({"message": "Cat successfully deleted", "id": id}), 200
                except OSError as e:
                    return jsonify({"error": f"Failed to delete cat: {str(e)}"}), 500
            return jsonify({"error": "Cat not found"}), 404
