"""
Frontend/GUI tests for Option Pricer

These tests verify the web interface and API contract.
They are decoupled from the pricing calculation logic - they test that:
1. The web server serves the GUI properly
2. The API endpoints accept/reject requests correctly
3. The frontend displays results to users
4. Error handling works in the UI

The actual pricing calculations are tested separately in test_option_pricer.py
"""
import pytest
from flask import Flask


# ============================================================================
# Test Fixtures - Decoupled from pricing logic
# ============================================================================

@pytest.fixture
def app():
    """Create application for testing - decoupled from pricing logic"""
    from src.web_server import create_app
    return create_app()


@pytest.fixture
def client(app):
    """Test client for making HTTP requests"""
    return app.test_client()


# ============================================================================
# Contract Tests - API and Web Interface
# ============================================================================

class TestWebServerContract:
    """Test that web server follows the contract/API specification"""
    
    def test_server_creates_flask_app(self, app):
        """Contract: create_app() must return a Flask application"""
        assert isinstance(app, Flask)
    
    def test_root_serves_html(self, client):
        """Contract: GET / must return HTML with 200 status"""
        response = client.get('/')
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')
    
    def test_api_price_accepts_post(self, client):
        """Contract: POST /api/price must accept JSON and return JSON"""
        response = client.post(
            '/api/price',
            json={'s0': 100, 'k1': 120, 'k2': 130, 'c_k1': 5.0, 'alpha': 3}
        )
        assert response.status_code == 200
        assert response.content_type.startswith('application/json')


class TestAPIResponseContract:
    """Test API response structure - decoupled from calculation logic"""
    
    def test_success_response_has_price_field(self, client):
        """Contract: Successful calculation must return {'price': float}"""
        response = client.post(
            '/api/price',
            json={'s0': 100, 'k1': 120, 'k2': 130, 'c_k1': 5.0, 'alpha': 3}
        )
        data = response.get_json()
        assert 'price' in data
        assert isinstance(data['price'], (int, float))
    
    def test_error_response_has_error_field(self, client):
        """Contract: Error response must return {'error': str} with 400 status"""
        response = client.post(
            '/api/price',
            json={'s0': 100, 'k1': 120, 'k2': 130, 'c_k1': 5.0, 'alpha': 0.5}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert isinstance(data['error'], str)


# ============================================================================
# Frontend Presentation Tests
# ============================================================================

class TestFrontendPresentation:
    """Test how the frontend presents information to users"""
    
    def test_html_contains_all_input_fields(self, client):
        """Presentation: Form must have inputs for all 5 parameters"""
        response = client.get('/')
        html = response.data.decode('utf-8').lower()
        
        required_fields = ['s0', 'k1', 'k2', 'c_k1', 'alpha']
        for field in required_fields:
            assert field in html, f"Missing input field: {field}"
    
    def test_html_has_calculate_button(self, client):
        """Presentation: Form must have a submit/calculate button"""
        response = client.get('/')
        html = response.data.decode('utf-8').lower()
        
        has_button = (
            '<button' in html and 
            ('type="submit"' in html or 'calculate' in html)
        )
        assert has_button, "Missing calculate/submit button"
    
    def test_html_has_result_display_area(self, client):
        """Presentation: Page must have an area to display results"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        assert 'id="result"' in html or 'result' in html.lower(), \
            "Missing result display area"
    
    def test_result_shows_ck2_format(self, client):
        """Presentation: Result must display in C(K2) = X.XXXXXX format like CLI"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # JavaScript should format as C(K2) = X.XXXXXX
        assert 'C(K2)' in html or 'c(k2)' in html.lower(), \
            "Result should use C(K2) format like CLI"


class TestFrontendErrorHandling:
    """Test frontend error presentation to users"""
    
    def test_javascript_has_error_handling(self, client):
        """Presentation: JavaScript must handle errors and show to user"""
        response = client.get('/')
        html = response.data.decode('utf-8').lower()
        
        # Should have try-catch for error handling
        has_try_catch = 'try' in html and 'catch' in html
        
        # Should display error in the result div
        displays_error = 'error' in html
        
        # Should have helpful error message for common issues
        has_helpful_message = (
            'server' in html or 
            'flask' in html or
            'run_web' in html
        )
        
        assert has_try_catch, "JavaScript must have try-catch for error handling"
        assert displays_error, "JavaScript must display errors to user"
        assert has_helpful_message, "JavaScript should guide user if server not running"
    
    def test_error_display_has_styling(self, client):
        """Presentation: Error display should have visual distinction"""
        response = client.get('/')
        html = response.data.decode('utf-8').lower()
        
        # Should have CSS for error styling (different color/background)
        has_error_style = (
            '.error' in html or 
            'error' in html and ('color' in html or 'background' in html)
        )
        assert has_error_style, "Error display should have visual styling"


class TestFrontendInteractivity:
    """Test frontend JavaScript interactivity"""
    
    def test_javascript_fetches_api(self, client):
        """Interactivity: JavaScript must fetch from /api/price"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        assert '/api/price' in html, "JavaScript must fetch from /api/price"
        assert 'fetch(' in html or 'xmlhttprequest' in html.lower(), \
            "JavaScript must use fetch or XMLHttpRequest"
    
    def test_javascript_prevents_form_submission(self, client):
        """Interactivity: JavaScript must prevent default form submission"""
        response = client.get('/')
        html = response.data.decode('utf-8').lower()
        
        assert 'preventdefault' in html.replace(' ', ''), \
            "JavaScript must prevent default form submission"


# ============================================================================
# Integration Tests - Frontend + Backend Together
# ============================================================================

class TestFrontendBackendIntegration:
    """Test that frontend and backend work together"""
    
    def test_api_accepts_data_from_form_fields(self, client):
        """Integration: API must accept the data structure from form"""
        # Simulates what the JavaScript form collects
        form_data = {
            's0': 100.0,
            'k1': 120.0, 
            'k2': 130.0,
            'c_k1': 5.0,
            'alpha': 3.0
        }
        
        response = client.post('/api/price', json=form_data)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'price' in data
    
    def test_end_to_end_valid_calculation(self, client):
        """Integration: Complete flow from form to result display works"""
        # 1. Get the form page
        response = client.get('/')
        assert response.status_code == 200
        
        # 2. Submit calculation
        calc_response = client.post('/api/price', json={
            's0': 100,
            'k1': 120,
            'k2': 130,
            'c_k1': 5.0,
            'alpha': 3
        })
        
        assert calc_response.status_code == 200
        data = calc_response.get_json()
        assert 'price' in data
        assert isinstance(data['price'], float)
    
    def test_end_to_end_error_display(self, client):
        """Integration: Error flow from API to error display works"""
        # Submit invalid data (alpha < 1)
        response = client.post('/api/price', json={
            's0': 100,
            'k1': 120,
            'k2': 130,
            'c_k1': 5.0,
            'alpha': 0.5
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


# ============================================================================
# Test that we don't depend on specific calculation results
# ============================================================================

class TestDecouplingFromPricingLogic:
    """
    These tests verify that frontend tests don't depend on specific 
    calculation values - they only test contracts and presentation.
    If the pricing formula changes, these tests should still pass.
    """
    
    def test_we_only_test_contract_not_values(self, client):
        """
        Meta-test: Verify we don't hardcode expected calculation results
        in frontend tests. Frontend tests should only check that:
        - API returns a number in 'price' field
        - Not what that number actually is
        """
        response = client.post('/api/price', json={
            's0': 100, 'k1': 120, 'k2': 130, 'c_k1': 5.0, 'alpha': 3
        })
        
        data = response.get_json()
        
        # We only care that price exists and is a number
        # NOT that it equals a specific value
        assert 'price' in data
        assert isinstance(data['price'], (int, float))
        
        # Don't do this in frontend tests:
        # assert data['price'] == 2.222222  # <-- This couples us to pricing logic!


# ============================================================================
# Bug Fix Tests - Specific Issues Found in Production
# ============================================================================

class TestFetchFailureBug:
    """
    Test to diagnose and fix the 'Failed to fetch' error shown in the screenshot.
    The error shows 'Error: Failed to fetch' which means the JavaScript fetch()
    failed to connect or got an error response.
    """
    
    def test_exact_user_input_from_screenshot(self, client):
        """
        Reproduce the exact scenario from the screenshot:
        S0=581.73, K1=590, K2=600, C(K1)=0.03, Alpha=2.6
        
        This should work but shows 'Failed to fetch' error.
        """
        response = client.post('/api/price', json={
            's0': 581.73,
            'k1': 590,
            'k2': 600,
            'c_k1': 0.03,
            'alpha': 2.6
        })
        
        # Should succeed, not fail with 400 or 500
        assert response.status_code == 200, \
            f"Expected 200 but got {response.status_code}. Data: {response.get_json()}"
        
        data = response.get_json()
        assert 'price' in data
        assert isinstance(data['price'], float)
    
    def test_server_handles_all_valid_edge_cases(self, client):
        """
        Test various edge cases that might cause fetch to fail.
        """
        test_cases = [
            # Small values
            {'s0': 1, 'k1': 2, 'k2': 3, 'c_k1': 0.01, 'alpha': 2},
            # Large values
            {'s0': 10000, 'k1': 11000, 'k2': 12000, 'c_k1': 100, 'alpha': 5},
            # Very small c_k1
            {'s0': 100, 'k1': 120, 'k2': 130, 'c_k1': 0.0001, 'alpha': 3},
            # The exact screenshot values
            {'s0': 581.73, 'k1': 590, 'k2': 600, 'c_k1': 0.03, 'alpha': 2.6},
        ]
        
        for i, test_input in enumerate(test_cases):
            response = client.post('/api/price', json=test_input)
            assert response.status_code == 200, \
                f"Test case {i} failed with status {response.status_code}: {test_input}"
            
            data = response.get_json()
            assert 'price' in data, f"Test case {i} missing price field: {data}"
