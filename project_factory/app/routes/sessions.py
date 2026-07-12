"""
Session management routes
Handles session creation, resume, and management
"""

from flask import Blueprint, request, jsonify, current_app
import os
import json
from datetime import datetime

bp = Blueprint('sessions', __name__)


def get_project_dir(project_name):
    """Get project directory path"""
    workspace_root = current_app.config['WORKSPACE_ROOT']
    return os.path.join(workspace_root, project_name)


def get_sessions_file(project_name):
    """Get path to sessions file for a project"""
    project_dir = get_project_dir(project_name)
    return os.path.join(project_dir, 'chat', 'sessions.json')


def load_sessions(project_name):
    """Load all sessions for a project"""
    sessions_file = get_sessions_file(project_name)
    if not os.path.exists(sessions_file):
        return []
    
    with open(sessions_file, 'r') as f:
        return json.load(f)


def save_sessions(project_name, sessions):
    """Save sessions to JSON file"""
    sessions_file = get_sessions_file(project_name)
    chat_dir = os.path.dirname(sessions_file)
    os.makedirs(chat_dir, exist_ok=True)
    
    with open(sessions_file, 'w') as f:
        json.dump(sessions, f, indent=2)


@bp.route('/<project_name>', methods=['GET'])
def list_sessions(project_name):
    """List all sessions for a project"""
    try:
        # Verify project exists
        project_dir = get_project_dir(project_name)
        if not os.path.exists(project_dir):
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        sessions = load_sessions(project_name)
        return jsonify({
            'success': True,
            'data': sessions,
            'count': len(sessions)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>', methods=['POST'])
def create_session(project_name):
    """Create a new session"""
    try:
        data = request.get_json() or {}
        
        # Verify project exists
        project_dir = get_project_dir(project_name)
        if not os.path.exists(project_dir):
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        session_name = data.get('name', f'Session {datetime.now().strftime("%Y%m%d_%H%M%S")}')
        description = data.get('description', '')
        
        # Load existing sessions
        sessions = load_sessions(project_name)
        
        # Check for duplicate name
        for session in sessions:
            if session['name'] == session_name:
                return jsonify({'success': False, 'error': 'Session already exists'}), 409
        
        # Create session directory
        session_id = datetime.now().strftime('%Y%m%d%H%M%S')
        session_dir = os.path.join(project_dir, 'chat', session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Create session metadata
        session = {
            'id': session_id,
            'name': session_name,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'status': 'active',
            'message_count': 0,
            'token_usage': 0,
            'summary': '',
            'directory': session_dir
        }
        
        # Save session metadata
        session_meta_file = os.path.join(session_dir, 'session.json')
        with open(session_meta_file, 'w') as f:
            json.dump(session, f, indent=2)
        
        # Create history file
        history_file = os.path.join(session_dir, 'history.jsonl')
        with open(history_file, 'w') as f:
            pass  # Create empty file
        
        # Create summary file
        summary_file = os.path.join(session_dir, 'summary.md')
        with open(summary_file, 'w') as f:
            f.write(f'# Session Summary: {session_name}\n\n')
        
        # Add to sessions list
        sessions.append(session)
        save_sessions(project_name, sessions)
        
        return jsonify({
            'success': True,
            'data': session,
            'message': f'Session created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>/<session_id>', methods=['GET'])
def get_session(project_name, session_id):
    """Get session details"""
    try:
        # Verify project exists
        project_dir = get_project_dir(project_name)
        if not os.path.exists(project_dir):
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        session_dir = os.path.join(project_dir, 'chat', session_id)
        if not os.path.exists(session_dir):
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Load session metadata
        session_meta_file = os.path.join(session_dir, 'session.json')
        with open(session_meta_file, 'r') as f:
            session = json.load(f)
        
        # Load history
        history_file = os.path.join(session_dir, 'history.jsonl')
        history = []
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                for line in f:
                    if line.strip():
                        history.append(json.loads(line))
        
        session['history'] = history
        
        return jsonify({'success': True, 'data': session})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>/<session_id>', methods=['DELETE'])
def delete_session(project_name, session_id):
    """Delete a session"""
    try:
        import shutil
        
        # Verify project exists
        project_dir = get_project_dir(project_name)
        if not os.path.exists(project_dir):
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        session_dir = os.path.join(project_dir, 'chat', session_id)
        if not os.path.exists(session_dir):
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Remove session directory
        shutil.rmtree(session_dir)
        
        # Remove from sessions list
        sessions = load_sessions(project_name)
        sessions = [s for s in sessions if s['id'] != session_id]
        save_sessions(project_name, sessions)
        
        return jsonify({
            'success': True,
            'message': 'Session deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>/<session_id>/summary', methods=['PUT'])
def update_session_summary(project_name, session_id):
    """Update session summary"""
    try:
        data = request.get_json()
        
        if not data or 'summary' not in data:
            return jsonify({'success': False, 'error': 'Summary is required'}), 400
        
        # Verify session exists
        project_dir = get_project_dir(project_name)
        session_dir = os.path.join(project_dir, 'chat', session_id)
        
        if not os.path.exists(session_dir):
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Update summary file
        summary_file = os.path.join(session_dir, 'summary.md')
        with open(summary_file, 'w') as f:
            f.write(data['summary'])
        
        # Update session metadata
        session_meta_file = os.path.join(session_dir, 'session.json')
        with open(session_meta_file, 'r') as f:
            session = json.load(f)
        
        session['summary'] = data['summary']
        session['updated_at'] = datetime.now().isoformat()
        
        with open(session_meta_file, 'w') as f:
            json.dump(session, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Summary updated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>/<session_id>/archive', methods=['POST'])
def archive_session(project_name, session_id):
    """Archive a session"""
    try:
        # Verify session exists
        project_dir = get_project_dir(project_name)
        session_dir = os.path.join(project_dir, 'chat', session_id)
        
        if not os.path.exists(session_dir):
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Update session status
        session_meta_file = os.path.join(session_dir, 'session.json')
        with open(session_meta_file, 'r') as f:
            session = json.load(f)
        
        session['status'] = 'archived'
        session['updated_at'] = datetime.now().isoformat()
        
        with open(session_meta_file, 'w') as f:
            json.dump(session, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Session archived successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
