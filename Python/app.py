from flask import Flask
from routes.maximo_routes import maximo_bp
from routes.personal_data_routes import personal_bp

app = Flask(__name__)

app.register_blueprint(maximo_bp)
app.register_blueprint(personal_bp)

DATA_DIR = 'wwwroot/uploads'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)