"""
AI Project Factory - Flask Application
Main application entry point
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    app.config['WORKSPACE_ROOT'] = os.getenv('WORKSPACE_ROOT', os.path.join(os.getcwd(), 'workspace'))
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
    
    # Enable CORS
    CORS(app)
    
    # Ensure workspace directory exists
    os.makedirs(app.config['WORKSPACE_ROOT'], exist_ok=True)
    
    # Register blueprints
    from app.routes import projects, sessions, chat, files, audit
    app.register_blueprint(projects.bp, url_prefix='/api/projects')
    app.register_blueprint(sessions.bp, url_prefix='/api/sessions')
    app.register_blueprint(chat.bp, url_prefix='/api/chat')
    app.register_blueprint(files.bp, url_prefix='/api/files')
    app.register_blueprint(audit.bp, url_prefix='/api/audit')
    
    # Health check endpoint
    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'workspace': app.config['WORKSPACE_ROOT']
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
