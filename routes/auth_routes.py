import json
from flask import request
from flask_restx import Namespace, Resource, fields
from models import db, User
from flask_jwt_extended import create_access_token, jwt_required, JWTManager

auth_ns = Namespace("auth", description="Authentication endpoints")

register_model = auth_ns.model("Register", {
    "username": fields.String(required=True, description="Username"),
    "password": fields.String(required=True, description="Password")
})

login_model = auth_ns.model("Login", {
    "username": fields.String(required=True, description="Username"),
    "password": fields.String(required=True, description="Password")
})

def init_auth_routes(app, api):
    api.add_namespace(auth_ns)

    with open("config.json") as config_file:
        config = json.load(config_file)
        app.config['JWT_SECRET_KEY'] = config.get("jwt_secret_key")
        jwt = JWTManager(app)
    auth_ns.authorizations = {
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "JWT authorization header. Example: 'Bearer <JWT_TOKEN>'"
        }
    }

    @auth_ns.route("/register")
    class RegisterUser(Resource):
        @auth_ns.expect(register_model)
        @auth_ns.response(400, 'Username and password are required or username already exists')
        @auth_ns.response(201, 'User successfully registered')
        def post(self):
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return {"error": "Username and password are required"}, 400

            if User.query.filter_by(username=username).first():
                return {"error": "Username already exists"}, 400

            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            return {"message": "User successfully registered"}, 201

    @auth_ns.route("/login")
    class LoginUser(Resource):
        @auth_ns.expect(login_model)
        @auth_ns.response(401, 'Invalid username or password')
        @auth_ns.response(200, 'Login successful')
        def post(self):
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                token = create_access_token(identity=str(user.id))
                return {"message": "Login successful", "token": token}, 200

            return {"error": "Invalid username or password"}, 401

    @auth_ns.route("/users/<int:user_id>")
    class GetUser(Resource):
        @jwt_required()
        @auth_ns.doc(params={"user_id": "The ID of the user"}, security="BearerAuth")
        @auth_ns.response(401, 'Unauthorized - Missing or invalid token')
        @auth_ns.response(200, 'Success')
        @auth_ns.response(404, 'User not found')
        def get(self, user_id):
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}, 404

            return {"username": user.username}, 200
