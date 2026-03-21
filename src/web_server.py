from flask import Flask, jsonify, request, send_from_directory
import os
from src.option_pricer import price_call


def create_app():
    """Create and configure the Flask application for serving the GUI"""
    # Get the project root directory (parent of src)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return send_from_directory(project_root, 'index.html')
    
    @app.route('/api/price', methods=['POST'])
    def price_endpoint():
        try:
            data = request.get_json()
            result = price_call(
                s0=data['s0'],
                k1=data['k1'],
                k2=data['k2'],
                c_k1=data['c_k1'],
                alpha=data['alpha']
            )
            return jsonify({'price': result})
        except (ValueError, KeyError) as e:
            return jsonify({'error': str(e)}), 400
    
    return app
