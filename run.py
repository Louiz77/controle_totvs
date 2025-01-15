from flask import Flask
from app.routes import chamados_bp
from app.routes import pipefy_bp
from app.routes import report_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(chamados_bp, url_prefix='/api')
    app.register_blueprint(pipefy_bp, url_prefix='/pipefy')
    app.register_blueprint(report_bp, url_prefix='/report')
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)