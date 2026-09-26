import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template
from config import config_by_name
from database.db import close_db
from routes.auth import auth_bp
from routes.student import student_bp
from routes.scholarships import scholarships_bp
from routes.views import views_bp
from routes.admin import admin_bp

load_dotenv()

def create_app(config_name=None):
    """Application factory for the Scholarship Recommendation System."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Teardown database connections
    app.teardown_appcontext(close_db)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(scholarships_bp)
    app.register_blueprint(views_bp)
    app.register_blueprint(admin_bp)

    # Health-check route
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "Personalized Scholarship Recommendation System",
            "version": "1.0.0",
            "environment": config_name
        }), 200

    @app.route("/api/info", methods=["GET"])
    def api_info():
        return jsonify({
            "message": "Welcome to the Personalized Scholarship Recommendation System API",
            "health_endpoint": "/api/health",
            "documentation": "/README.md"
        }), 200

    # Global error handlers
    @app.errorhandler(404)
    def handle_404(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Resource not found"}), 404
        return render_template("index.html"), 404

    @app.errorhandler(500)
    def handle_500(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error"}), 500
        return render_template("index.html"), 500

    return app

if __name__ == "__main__":
    import socket
    app = create_app()
    base_port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")

    # Automatically find an available port if preferred port is occupied
    port = base_port
    for candidate_port in [base_port, 5001, 5002, 8000, 8080]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", candidate_port)) != 0:
                port = candidate_port
                break

    print(f"\n=======================================================")
    print(f" Starting ScholarBridge Server at http://{host}:{port}")
    print(f"=======================================================\n")
    app.run(host=host, port=port, debug=app.config["DEBUG"])
