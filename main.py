from flask import Flask
from routes.create_routes import init_create_routes
from routes.delete_routes import init_delete_routes
from routes.auth_routes import init_auth_routes
from routes.content_routes import init_content_routes
from models import db
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

init_content_routes(app)
init_auth_routes(app)
init_create_routes(app)
init_delete_routes(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
