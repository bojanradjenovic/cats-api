from flask import Flask
from flask_cors import CORS
from routes.create_routes import init_create_routes
from routes.delete_routes import init_delete_routes
from routes.auth_routes import init_auth_routes
from routes.content_routes import init_content_routes
from models import db
from flask_restx import Api
app = Flask(__name__)
cors = CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app, title="cats :3", version="1.0", description="API for cats by a cat")
db.init_app(app)

init_content_routes(app, api)
init_auth_routes(app, api)
init_create_routes(app, api)
init_delete_routes(app, api)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
