"""
Unit tests for CLI Dashboard module
Tests the CLI functions without requiring a running server
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add cli directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestCLIDashboard(unittest.TestCase):
    """Test cases for CLI Dashboard functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        pass
    
    def test_colors_defined(self):
        """Test that color codes are properly defined"""
        from cli.dashboard import Colors
        
        self.assertTrue(hasattr(Colors, 'HEADER'))
        self.assertTrue(hasattr(Colors, 'BLUE'))
        self.assertTrue(hasattr(Colors, 'CYAN'))
        self.assertTrue(hasattr(Colors, 'GREEN'))
        self.assertTrue(hasattr(Colors, 'WARNING'))
        self.assertTrue(hasattr(Colors, 'FAIL'))
        self.assertTrue(hasattr(Colors, 'ENDC'))
        self.assertTrue(hasattr(Colors, 'BOLD'))
    
    @patch('cli.dashboard.requests.get')
    def test_make_request_get_success(self, mock_get):
        """Test successful GET request"""
        from cli.dashboard import make_request
        
        mock_response = MagicMock()
        mock_response.json.return_value = {'success': True, 'data': []}
        mock_get.return_value = mock_response
        
        result = make_request('GET', '/projects')
        
        self.assertTrue(result['success'])
        mock_get.assert_called_once()
    
    @patch('cli.dashboard.requests.post')
    def test_make_request_post_success(self, mock_post):
        """Test successful POST request"""
        from cli.dashboard import make_request
        
        mock_response = MagicMock()
        mock_response.json.return_value = {'success': True, 'data': {'id': '123'}}
        mock_post.return_value = mock_response
        
        result = make_request('POST', '/projects', {'name': 'test'})
        
        self.assertTrue(result['success'])
        mock_post.assert_called_once()
    
    @patch('cli.dashboard.requests.put')
    def test_make_request_put_success(self, mock_put):
        """Test successful PUT request"""
        from cli.dashboard import make_request
        
        mock_response = MagicMock()
        mock_response.json.return_value = {'success': True}
        mock_put.return_value = mock_response
        
        result = make_request('PUT', '/projects/test', {'description': 'updated'})
        
        self.assertTrue(result['success'])
        mock_put.assert_called_once()
    
    @patch('cli.dashboard.requests.delete')
    def test_make_request_delete_success(self, mock_delete):
        """Test successful DELETE request"""
        from cli.dashboard import make_request
        
        mock_response = MagicMock()
        mock_response.json.return_value = {'success': True}
        mock_delete.return_value = mock_response
        
        result = make_request('DELETE', '/projects/test')
        
        self.assertTrue(result['success'])
        mock_delete.assert_called_once()
    
    @patch('cli.dashboard.requests.get')
    def test_make_request_connection_error(self, mock_get):
        """Test connection error handling"""
        from cli.dashboard import make_request
        import requests
        
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        result = make_request('GET', '/projects')
        
        self.assertFalse(result['success'])
        self.assertIn('Cannot connect', result['error'])
    
    def test_make_request_invalid_method(self):
        """Test invalid HTTP method"""
        from cli.dashboard import make_request
        
        result = make_request('PATCH', '/projects')
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Invalid method')


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI with API"""
    
    @patch('cli.dashboard.make_request')
    def test_health_check_format(self, mock_request):
        """Test health check response format"""
        from cli.dashboard import make_request
        
        mock_request.return_value = {
            'status': 'healthy',
            'workspace': '/test/workspace'
        }
        
        result = mock_request('GET', '/health')
        
        self.assertEqual(result['status'], 'healthy')
        self.assertIn('workspace', result)
    
    @patch('cli.dashboard.make_request')
    def test_project_structure(self, mock_request):
        """Test project data structure"""
        from cli.dashboard import make_request
        
        mock_request.return_value = {
            'success': True,
            'data': {
                'name': 'test_project',
                'status': 'active',
                'directory': '/workspace/test_project'
            }
        }
        
        result = mock_request('GET', '/projects/test_project')
        
        self.assertTrue(result['success'])
        self.assertIn('name', result['data'])
        self.assertIn('status', result['data'])


if __name__ == '__main__':
    unittest.main()
