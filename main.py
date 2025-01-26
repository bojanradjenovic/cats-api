from flask import Flask
from routes.create_routes import init_create_routes
from routes.delete_routes import init_delete_routes
app = Flask(__name__)

init_create_routes(app)
init_delete_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
