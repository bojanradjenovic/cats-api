from flask import Flask
from routes.create_routes import init_create_routes
app = Flask(__name__)

init_create_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
