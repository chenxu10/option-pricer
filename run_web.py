#!/usr/bin/env python3
"""Entry point to run the web GUI server."""
from src.web_server import create_app


def run_web_server(host='127.0.0.1', port=5000, debug=False):
    """Run the Flask web server for the GUI."""
    app = create_app()
    print(f"Starting Option Pricer GUI server on http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run the Option Pricer web GUI')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    run_web_server(host=args.host, port=args.port, debug=args.debug)
