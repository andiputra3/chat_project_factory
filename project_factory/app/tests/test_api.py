"""
Unit tests for Project Factory Flask Application
"""

import unittest
import json
import os
import tempfile
import shutil
from app import create_app


class TestProjectFactory(unittest.TestCase):
    """Test cases for Project Factory API"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.app = create_app()
        self.app.config['WORKSPACE_ROOT'] = self.test_dir
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('workspace', data)
    
    def test_create_project(self):
        """Test project creation"""
        project_data = {
            'name': 'test_project',
            'description': 'Test project for unit testing'
        }
        
        response = self.client.post(
            '/api/projects',
            data=json.dumps(project_data),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], 'test_project')
        
        # Verify project directory structure was created
        project_dir = os.path.join(self.test_dir, 'test_project')
        self.assertTrue(os.path.exists(project_dir))
        
        # Verify expected folders exist
        expected_folders = ['docs', 'source', 'reference', 'runtime', 'tests', 'exports', 'reports', 'chat']
        for folder in expected_folders:
            self.assertTrue(os.path.exists(os.path.join(project_dir, folder)))
    
    def test_list_projects(self):
        """Test listing projects"""
        # Create a project first
        project_data = {'name': 'project1'}
        self.client.post('/api/projects', data=json.dumps(project_data), content_type='application/json')
        
        response = self.client.get('/api/projects')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['count'], 1)
    
    def test_get_project(self):
        """Test getting project details"""
        # Create a project first
        project_data = {'name': 'project_details_test'}
        self.client.post('/api/projects', data=json.dumps(project_data), content_type='application/json')
        
        response = self.client.get('/api/projects/project_details_test')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], 'project_details_test')
    
    def test_duplicate_project(self):
        """Test creating duplicate project fails"""
        project_data = {'name': 'duplicate_test'}
        
        # Create first project
        self.client.post('/api/projects', data=json.dumps(project_data), content_type='application/json')
        
        # Try to create duplicate
        response = self.client.post(
            '/api/projects',
            data=json.dumps(project_data),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 409)
        self.assertFalse(data['success'])
        self.assertIn('already exists', data['error'])
    
    def test_delete_project(self):
        """Test project deletion"""
        # Create a project first
        project_data = {'name': 'delete_test'}
        self.client.post('/api/projects', data=json.dumps(project_data), content_type='application/json')
        
        # Delete the project
        response = self.client.delete('/api/projects/delete_test')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        
        # Verify project directory was removed
        project_dir = os.path.join(self.test_dir, 'delete_test')
        self.assertFalse(os.path.exists(project_dir))
    
    def test_create_session(self):
        """Test session creation"""
        # Create a project first
        project_data = {'name': 'session_test_project'}
        self.client.post('/api/projects', data=json.dumps(project_data), content_type='application/json')
        
        # Create a session
        session_data = {
            'name': 'Test Session',
            'description': 'Test session description'
        }
        
        response = self.client.post(
            '/api/sessions/session_test_project',
            data=json.dumps(session_data),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], 'Test Session')
        
        # Verify session directory was created
        session_id = data['data']['id']
        session_dir = os.path.join(self.test_dir, 'session_test_project', 'chat', session_id)
        self.assertTrue(os.path.exists(session_dir))
        
        # Verify session files exist
        self.assertTrue(os.path.exists(os.path.join(session_dir, 'session.json')))
        self.assertTrue(os.path.exists(os.path.join(session_dir, 'history.jsonl')))
        self.assertTrue(os.path.exists(os.path.join(session_dir, 'summary.md')))
    
    def test_list_sessions(self):
        """Test listing sessions"""
        # Create project and session
        project_data = {'name': 'list_sessions_test'}
        self.client.post('/api/projects', data=json.dumps(project_data), content_type='application/json')
        
        session_data = {'name': 'Session 1'}
        self.client.post('/api/sessions/list_sessions_test', data=json.dumps(session_data), content_type='application/json')
        
        response = self.client.get('/api/sessions/list_sessions_test')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['count'], 1)
    
    def test_send_message(self):
        """Test sending chat message"""
        # Create project and session
        project_data = {'name': 'chat_test_project'}
        self.client.post('/api/projects', data=json.dumps(project_data), content_type='application/json')
        
        session_data = {'name': 'Chat Session'}
        session_response = self.client.post('/api/sessions/chat_test_project', data=json.dumps(session_data), content_type='application/json')
        session_id = json.loads(session_response.data)['data']['id']
        
        # Send a message
        message_data = {'content': 'Hello, this is a test message'}
        response = self.client.post(
            f'/api/chat/chat_test_project/{session_id}/messages',
            data=json.dumps(message_data),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('user_message', data['data'])
        self.assertIn('ai_message', data['data'])
    
    def test_get_messages(self):
        """Test retrieving messages"""
        # Create project, session, and send a message
        project_data = {'name': 'get_messages_test'}
        self.client.post('/api/projects', data=json.dumps(project_data), content_type='application/json')
        
        session_data = {'name': 'Message Session'}
        session_response = self.client.post('/api/sessions/get_messages_test', data=json.dumps(session_data), content_type='application/json')
        session_id = json.loads(session_response.data)['data']['id']
        
        message_data = {'content': 'Test message'}
        self.client.post(f'/api/chat/get_messages_test/{session_id}/messages', data=json.dumps(message_data), content_type='application/json')
        
        response = self.client.get(f'/api/chat/get_messages_test/{session_id}/messages')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['count'], 1)
    
    def test_file_tree(self):
        """Test file tree retrieval"""
        # Create a project
        project_data = {'name': 'file_tree_test'}
        self.client.post('/api/projects', data=json.dumps(project_data), content_type='application/json')
        
        response = self.client.get('/api/files/file_tree_test/tree')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('children', data['data'])
    
    def test_create_file(self):
        """Test file creation"""
        # Create a project
        project_data = {'name': 'create_file_test'}
        self.client.post('/api/projects', data=json.dumps(project_data), content_type='application/json')
        
        # Use path relative to project root with forward slashes
        file_data = {
            'path': 'docs/test.md',
            'content': '# Test Document\n\nThis is a test.'
        }
        
        response = self.client.post(
            '/api/files/create_file_test/file',
            data=json.dumps(file_data),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        
        # Verify file was created - path uses OS separator
        import ntpath
        file_path = os.path.join(self.test_dir, 'create_file_test', 'docs', 'test.md')
        self.assertTrue(os.path.exists(file_path))
    
    def test_read_file(self):
        """Test file reading"""
        # Create project and file
        project_data = {'name': 'read_file_test'}
        self.client.post('/api/projects', data=json.dumps(project_data), content_type='application/json')
        
        # Create file first
        file_data = {'path': 'docs/readme.md', 'content': '# README\n\nTest content'}
        self.client.post('/api/files/read_file_test/file', data=json.dumps(file_data), content_type='application/json')
        
        response = self.client.get('/api/files/read_file_test/file?path=docs/readme.md')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('# README', data['data']['content'])
    
    def test_audit_project(self):
        """Test project audit"""
        # Create a project with some content
        project_data = {'name': 'audit_test'}
        self.client.post('/api/projects', data=json.dumps(project_data), content_type='application/json')
        
        # Create a spec file
        spec_data = {'path': 'docs/FIRST_SPEC.md', 'content': '# First Specification\n\nThis is the first specification document with enough content to pass quality checks.'}
        self.client.post('/api/files/audit_test/file', data=json.dumps(spec_data), content_type='application/json')
        
        response = self.client.get('/api/audit/audit_test')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('audits', data['data'])
        self.assertIn('summary', data['data'])
        self.assertIn('overall_score', data['data']['summary'])


class TestProjectConstitution(unittest.TestCase):
    """Test project constitution compliance"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.app = create_app()
        self.app.config['WORKSPACE_ROOT'] = self.test_dir
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_workspace_structure_compliance(self):
        """Test that workspace structure follows specification"""
        project_data = {'name': 'structure_test'}
        response = self.client.post('/api/projects', data=json.dumps(project_data), content_type='application/json')
        
        project_dir = os.path.join(self.test_dir, 'structure_test')
        
        # Verify required directories exist (as per specification)
        required_dirs = ['docs', 'source', 'reference', 'runtime', 'tests', 'exports', 'reports', 'chat']
        for dir_name in required_dirs:
            dir_path = os.path.join(project_dir, dir_name)
            self.assertTrue(os.path.exists(dir_path), f"Required directory {dir_name} not found")
    
    def test_session_isolation(self):
        """Test that sessions are properly isolated per project"""
        # Create two projects with unique names
        import time
        timestamp_a = str(int(time.time() * 1000))
        time.sleep(0.1)  # Ensure different timestamp for project names
        timestamp_b = str(int(time.time() * 1000))
        
        self.client.post('/api/projects', data=json.dumps({'name': f'project_a_{timestamp_a}'}), content_type='application/json')
        self.client.post('/api/projects', data=json.dumps({'name': f'project_b_{timestamp_b}'}), content_type='application/json')
        
        # Create sessions in each - session ID uses datetime format YYYYMMDDHHMMSS
        # Need to wait at least 1 second between session creations
        response_a = self.client.post(f'/api/sessions/project_a_{timestamp_a}', data=json.dumps({'name': 'Session A'}), content_type='application/json')
        session_id_a = json.loads(response_a.data)['data']['id']
        
        time.sleep(1.1)  # Wait more than 1 second to ensure different session ID
        
        response_b = self.client.post(f'/api/sessions/project_b_{timestamp_b}', data=json.dumps({'name': 'Session B'}), content_type='application/json')
        session_id_b = json.loads(response_b.data)['data']['id']
        
        # Verify sessions are separate by checking IDs are different
        self.assertNotEqual(session_id_a, session_id_b)
        
        # Verify each project only sees its own sessions
        list_a = json.loads(self.client.get(f'/api/sessions/project_a_{timestamp_a}').data)['data']
        list_b = json.loads(self.client.get(f'/api/sessions/project_b_{timestamp_b}').data)['data']
        
        # Each should have exactly one session
        self.assertEqual(len(list_a), 1)
        self.assertEqual(len(list_b), 1)
        
        # Session IDs should not overlap
        ids_a = {s['id'] for s in list_a}
        ids_b = {s['id'] for s in list_b}
        
        self.assertEqual(ids_a.intersection(ids_b), set())


if __name__ == '__main__':
    unittest.main()
