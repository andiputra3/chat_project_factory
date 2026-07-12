"""
Project management routes
Handles CRUD operations for projects
"""

from flask import Blueprint, request, jsonify, current_app
import os
import json
import shutil
from datetime import datetime

bp = Blueprint('projects', __name__)


def get_projects_file():
    """Get path to projects database file"""
    workspace_root = current_app.config['WORKSPACE_ROOT']
    return os.path.join(workspace_root, 'projects.json')


def load_projects():
    """Load all projects from JSON file"""
    projects_file = get_projects_file()
    if not os.path.exists(projects_file):
        return []
    
    with open(projects_file, 'r') as f:
        return json.load(f)


def save_projects(projects):
    """Save projects to JSON file"""
    projects_file = get_projects_file()
    with open(projects_file, 'w') as f:
        json.dump(projects, f, indent=2)


@bp.route('', methods=['GET'])
def list_projects():
    """List all projects"""
    try:
        projects = load_projects()
        return jsonify({
            'success': True,
            'data': projects,
            'count': len(projects)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('', methods=['POST'])
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'success': False, 'error': 'Project name is required'}), 400
        
        project_name = data['name']
        description = data.get('description', '')
        
        # Load existing projects
        projects = load_projects()
        
        # Check for duplicate
        for project in projects:
            if project['name'] == project_name:
                return jsonify({'success': False, 'error': 'Project already exists'}), 409
        
        # Create project directory structure
        workspace_root = current_app.config['WORKSPACE_ROOT']
        project_dir = os.path.join(workspace_root, project_name)
        
        if os.path.exists(project_dir):
            return jsonify({'success': False, 'error': 'Project directory already exists'}), 409
        
        # Create folder structure as per specification
        folders = ['docs', 'source', 'reference', 'runtime', 'tests', 'exports', 'reports', 'chat']
        for folder in folders:
            os.makedirs(os.path.join(project_dir, folder), exist_ok=True)
        
        # Create project metadata
        project = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'name': project_name,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'status': 'active',
            'directory': project_dir,
            'constitution': {},
            'sessions': []
        }
        
        # Save project metadata
        project_meta_file = os.path.join(project_dir, 'project.json')
        with open(project_meta_file, 'w') as f:
            json.dump(project, f, indent=2)
        
        # Add to projects list
        projects.append(project)
        save_projects(projects)
        
        return jsonify({
            'success': True,
            'data': project,
            'message': f'Project {project_name} created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>', methods=['GET'])
def get_project(project_name):
    """Get project details"""
    try:
        projects = load_projects()
        
        for project in projects:
            if project['name'] == project_name:
                # Load fresh project metadata
                project_dir = os.path.join(current_app.config['WORKSPACE_ROOT'], project_name)
                project_meta_file = os.path.join(project_dir, 'project.json')
                
                if os.path.exists(project_meta_file):
                    with open(project_meta_file, 'r') as f:
                        project = json.load(f)
                
                return jsonify({'success': True, 'data': project})
        
        return jsonify({'success': False, 'error': 'Project not found'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>', methods=['PUT'])
def update_project(project_name):
    """Update project"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        projects = load_projects()
        project_index = None
        
        for i, project in enumerate(projects):
            if project['name'] == project_name:
                project_index = i
                break
        
        if project_index is None:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        # Update allowed fields
        allowed_fields = ['description', 'status', 'constitution']
        for field in allowed_fields:
            if field in data:
                projects[project_index][field] = data[field]
        
        projects[project_index]['updated_at'] = datetime.now().isoformat()
        
        # Save updated project metadata
        project_dir = os.path.join(current_app.config['WORKSPACE_ROOT'], project_name)
        project_meta_file = os.path.join(project_dir, 'project.json')
        
        with open(project_meta_file, 'w') as f:
            json.dump(projects[project_index], f, indent=2)
        
        save_projects(projects)
        
        return jsonify({
            'success': True,
            'data': projects[project_index],
            'message': 'Project updated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>', methods=['DELETE'])
def delete_project(project_name):
    """Delete a project"""
    try:
        projects = load_projects()
        project_index = None
        
        for i, project in enumerate(projects):
            if project['name'] == project_name:
                project_index = i
                break
        
        if project_index is None:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        # Remove project directory
        project_dir = os.path.join(current_app.config['WORKSPACE_ROOT'], project_name)
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
        
        # Remove from projects list
        projects.pop(project_index)
        save_projects(projects)
        
        return jsonify({
            'success': True,
            'message': f'Project {project_name} deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<project_name>/clone', methods=['POST'])
def clone_project(project_name):
    """Clone a project"""
    try:
        data = request.get_json()
        new_name = data.get('new_name')
        
        if not new_name:
            return jsonify({'success': False, 'error': 'New project name is required'}), 400
        
        projects = load_projects()
        source_project = None
        
        for project in projects:
            if project['name'] == project_name:
                source_project = project
                break
        
        if not source_project:
            return jsonify({'success': False, 'error': 'Source project not found'}), 404
        
        # Check if new name already exists
        for project in projects:
            if project['name'] == new_name:
                return jsonify({'success': False, 'error': 'Project already exists'}), 409
        
        # Clone directory
        workspace_root = current_app.config['WORKSPACE_ROOT']
        source_dir = os.path.join(workspace_root, project_name)
        target_dir = os.path.join(workspace_root, new_name)
        
        if not os.path.exists(source_dir):
            return jsonify({'success': False, 'error': 'Source directory not found'}), 404
        
        shutil.copytree(source_dir, target_dir)
        
        # Update project metadata
        cloned_project = source_project.copy()
        cloned_project['id'] = datetime.now().strftime('%Y%m%d%H%M%S')
        cloned_project['name'] = new_name
        cloned_project['created_at'] = datetime.now().isoformat()
        cloned_project['updated_at'] = datetime.now().isoformat()
        cloned_project['directory'] = target_dir
        
        # Save cloned project metadata
        project_meta_file = os.path.join(target_dir, 'project.json')
        with open(project_meta_file, 'w') as f:
            json.dump(cloned_project, f, indent=2)
        
        # Add to projects list
        projects.append(cloned_project)
        save_projects(projects)
        
        return jsonify({
            'success': True,
            'data': cloned_project,
            'message': f'Project cloned successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
