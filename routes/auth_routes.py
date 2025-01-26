import json
from flask import request, jsonify
from models import db, User
from flask_jwt_extended import create_access_token, jwt_required, JWTManager

def init_auth_routes(app):
    with open("config.json") as config_file:
        config = json.load(config_file)
        app.config['JWT_SECRET_KEY'] = config.get("jwt_secret_key")
        jwt = JWTManager(app)
    @app.route('/register', methods=['POST'])
    def register_user():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return jsonify({"message": "User successfully registered"}), 201
    @app.route('/login', methods=['POST'])
    def login_user():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            token = create_access_token(identity=str(user.id))
            return jsonify({"message": "Login successful", "token": token}), 200
        return jsonify({"error": "Invalid username or password"}), 401