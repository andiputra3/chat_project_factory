"""
File management routes
Handles file operations: create, read, update, delete, upload, download
"""

from flask import Blueprint, request, jsonify, current_app, send_file
import os
import json
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename

bp = Blueprint('files', __name__)


def get_project_dir(project_name):
    """Get project directory path"""
    workspace_root = current_app.config['WORKSPACE_ROOT']
    return os.path.join(workspace_root, project_name)


@bp.route('/<project_name>/tree', methods=['GET'])
def get_file_tree(project_name):
    """Get file tree for a project"""
    try:
        project_dir = get_project_dir(project_name)
        
        if not os.path.exists(project_dir):
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        def build_tree(path, prefix=''):
            """Build tree structure recursively"""
            result = []
            items = sorted(os.listdir(path))
            
            for i, item in enumerate(items):
                if item.startswith('.'):
                    continue
                
                item_path = os.path.join(path, item)
                is_last = (i == len(items) - 1)
                
                node = {
                    'name': item,
                    'path': os.path.relpath(item_path, project_dir),
                    'type': 'directory' if os.path.isdir(item_path) else 'file',
                    'is_last': is_last
                }
                
                if os.path.isdir(item_path):
                    node['children'] = build_tree(item_path, prefix + ('    ' if is_last else '|   '))
                
                result.append(node)
            
            return result
        
        tree = build_tree(project_dir)
        
        return jsonify({
            'success': True,
            'data': {
                'name': project_name,
                'path': project_name,
                'type': 'directory',
                'children': tree
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>/file', methods=['GET'])
def get_file(project_name):
    """Get file content"""
    try:
        file_path = request.args.get('path')
        
        if not file_path:
            return jsonify({'success': False, 'error': 'File path is required'}), 400
        
        # Security: normalize path and prevent traversal
        # Split path into components and sanitize each
        path_parts = os.path.normpath(file_path).split(os.sep)
        safe_parts = [secure_filename(part) for part in path_parts if part and part != '..']
        safe_path = os.path.join(*safe_parts)
        
        full_path = os.path.join(get_project_dir(project_name), safe_path)
        
        if not os.path.exists(full_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        if os.path.isdir(full_path):
            return jsonify({'success': False, 'error': 'Cannot read directory as file'}), 400
        
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'data': {
                'path': safe_path,
                'content': content,
                'size': os.path.getsize(full_path)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>/file', methods=['POST'])
def create_file(project_name):
    """Create or update a file"""
    try:
        data = request.get_json()
        
        if not data or 'path' not in data or 'content' not in data:
            return jsonify({'success': False, 'error': 'Path and content are required'}), 400
        
        file_path = data['path']
        content = data['content']
        
        # Security: normalize path and prevent traversal
        # Split path into components and sanitize each
        path_parts = os.path.normpath(file_path).split(os.sep)
        safe_parts = [secure_filename(part) for part in path_parts if part and part != '..']
        safe_path = os.path.join(*safe_parts)
        
        full_path = os.path.join(get_project_dir(project_name), safe_path)
        
        # Ensure parent directory exists
        parent_dir = os.path.dirname(full_path)
        os.makedirs(parent_dir, exist_ok=True)
        
        # Write file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            'success': True,
            'data': {
                'path': safe_path,
                'size': len(content)
            },
            'message': 'File created/updated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>/file', methods=['DELETE'])
def delete_file(project_name):
    """Delete a file or directory"""
    try:
        data = request.get_json() or {}
        file_path = data.get('path')
        
        if not file_path:
            return jsonify({'success': False, 'error': 'File path is required'}), 400
        
        # Security: prevent path traversal
        file_path = secure_filename(file_path)
        full_path = os.path.join(get_project_dir(project_name), file_path)
        
        if not os.path.exists(full_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Prevent deleting root project directories
        protected_dirs = ['docs', 'source', 'reference', 'runtime', 'tests', 'exports', 'reports', 'chat']
        if os.path.isdir(full_path):
            dir_name = os.path.basename(full_path)
            if dir_name in protected_dirs:
                return jsonify({'success': False, 'error': 'Cannot delete protected directory'}), 403
        
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        
        return jsonify({
            'success': True,
            'message': 'File/directory deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>/upload', methods=['POST'])
def upload_file(project_name):
    """Upload a file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        target_path = request.form.get('path', '')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Security: sanitize filename
        filename = secure_filename(file.filename)
        
        # Build full path
        project_dir = get_project_dir(project_name)
        if target_path:
            target_path = secure_filename(target_path)
            full_path = os.path.join(project_dir, target_path, filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
        else:
            full_path = os.path.join(project_dir, filename)
        
        # Save file
        file.save(full_path)
        
        return jsonify({
            'success': True,
            'data': {
                'filename': filename,
                'path': os.path.relpath(full_path, project_dir),
                'size': os.path.getsize(full_path)
            },
            'message': 'File uploaded successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>/download', methods=['GET'])
def download_file(project_name):
    """Download a file"""
    try:
        file_path = request.args.get('path')
        
        if not file_path:
            return jsonify({'success': False, 'error': 'File path is required'}), 400
        
        # Security: prevent path traversal
        file_path = secure_filename(file_path)
        full_path = os.path.join(get_project_dir(project_name), file_path)
        
        if not os.path.exists(full_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        if os.path.isdir(full_path):
            return jsonify({'success': False, 'error': 'Cannot download directory'}), 400
        
        return send_file(
            full_path,
            as_attachment=True,
            download_name=os.path.basename(full_path)
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>/rename', methods=['PUT'])
def rename_file(project_name):
    """Rename a file or directory"""
    try:
        data = request.get_json()
        
        if not data or 'old_path' not in data or 'new_path' not in data:
            return jsonify({'success': False, 'error': 'old_path and new_path are required'}), 400
        
        old_path = secure_filename(data['old_path'])
        new_path = secure_filename(data['new_path'])
        
        old_full_path = os.path.join(get_project_dir(project_name), old_path)
        new_full_path = os.path.join(get_project_dir(project_name), new_path)
        
        if not os.path.exists(old_full_path):
            return jsonify({'success': False, 'error': 'Source not found'}), 404
        
        if os.path.exists(new_full_path):
            return jsonify({'success': False, 'error': 'Destination already exists'}), 409
        
        os.rename(old_full_path, new_full_path)
        
        return jsonify({
            'success': True,
            'message': 'Renamed successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
