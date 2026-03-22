"""
Frontend/GUI tests for Option Pricer - Minimal Core Tests

These 5 tests verify the essential web interface and API contract.
The actual pricing calculations are tested separately in test_option_pricer.py
"""
import pytest


@pytest.fixture
def client():
    """Test client for making HTTP requests"""
    from src.web_server import create_app
    app = create_app()
    return app.test_client()


class TestFrontendCore:
    """Minimal tests for frontend core logic"""
    
    def test_root_serves_html(self, client):
        """Verify GET / returns HTML with 200 status"""
        response = client.get('/')
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')
    
    def test_api_accepts_post(self, client):
        """Verify POST /api/price accepts JSON and returns JSON"""
        response = client.post(
            '/api/price',
            json={'s0': 100, 'k1': 120, 'k2': 130, 'c_k1': 5.0, 'alpha': 3}
        )
        assert response.status_code == 200
        assert response.content_type.startswith('application/json')
    
    def test_success_response_has_price(self, client):
        """Verify successful response returns {'price': float}"""
        response = client.post(
            '/api/price',
            json={'s0': 100, 'k1': 120, 'k2': 130, 'c_k1': 5.0, 'alpha': 3}
        )
        data = response.get_json()
        assert 'price' in data
        assert isinstance(data['price'], (int, float))
    
    def test_error_response_has_error(self, client):
        """Verify error response returns {'error': str} with 400 status"""
        response = client.post(
            '/api/price',
            json={'s0': 100, 'k1': 120, 'k2': 130, 'c_k1': 5.0, 'alpha': 0.5}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert isinstance(data['error'], str)
    
    def test_html_contains_input_fields(self, client):
        """Verify HTML has input fields for all 5 parameters"""
        response = client.get('/')
        html = response.data.decode('utf-8').lower()
        for field in ['s0', 'k1', 'k2', 'c_k1', 'alpha']:
            assert field in html, f"Missing input field: {field}"
