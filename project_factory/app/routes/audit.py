"""
Audit routes
Handles project audit operations as per specification
"""

from flask import Blueprint, request, jsonify, current_app
import os
import json
from datetime import datetime

bp = Blueprint('audit', __name__)


def get_project_dir(project_name):
    """Get project directory path"""
    workspace_root = current_app.config['WORKSPACE_ROOT']
    return os.path.join(workspace_root, project_name)


@bp.route('/<project_name>', methods=['GET'])
def run_audit(project_name):
    """Run comprehensive audit on a project"""
    try:
        project_dir = get_project_dir(project_name)
        
        if not os.path.exists(project_dir):
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        # Run all audits
        audit_results = {
            'project_name': project_name,
            'timestamp': datetime.now().isoformat(),
            'audits': {}
        }
        
        # Audit 0: Input Quality
        audit_results['audits']['input_quality'] = audit_input_quality(project_dir)
        
        # Audit 1-5: Discovery audits
        audit_results['audits']['knowledge_extraction'] = audit_knowledge_extraction(project_dir)
        audit_results['audits']['requirement_discovery'] = audit_requirement_discovery(project_dir)
        audit_results['audits']['component_discovery'] = audit_component_discovery(project_dir)
        audit_results['audits']['artifact_discovery'] = audit_artifact_discovery(project_dir)
        audit_results['audits']['file_discovery'] = audit_file_discovery(project_dir)
        
        # Audit 6-10: Quality audits
        audit_results['audits']['traceability'] = audit_traceability(project_dir)
        audit_results['audits']['architecture'] = audit_architecture(project_dir)
        audit_results['audits']['specification_quality'] = audit_specification_quality(project_dir)
        audit_results['audits']['document_relation'] = audit_document_relation(project_dir)
        
        # Calculate overall scores
        audit_results['summary'] = calculate_audit_summary(audit_results['audits'])
        
        # Save audit report
        reports_dir = os.path.join(project_dir, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        audit_file = os.path.join(reports_dir, f'audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(audit_file, 'w') as f:
            json.dump(audit_results, f, indent=2)
        
        return jsonify({
            'success': True,
            'data': audit_results,
            'message': 'Audit completed successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def audit_input_quality(project_dir):
    """Audit 0: Input Quality Audit"""
    result = {
        'status': 'PASS',
        'issues': [],
        'metrics': {}
    }
    
    # Count files
    total_files = 0
    empty_files = []
    
    for root, dirs, files in os.walk(project_dir):
        for file in files:
            if file.startswith('.'):
                continue
            total_files += 1
            file_path = os.path.join(root, file)
            if os.path.getsize(file_path) == 0:
                empty_files.append(file_path)
    
    result['metrics']['total_files'] = total_files
    result['metrics']['empty_files'] = len(empty_files)
    
    if empty_files:
        result['status'] = 'WARNING'
        result['issues'].append(f'Found {len(empty_files)} empty files')
    
    return result


def audit_knowledge_extraction(project_dir):
    """Audit 1: Knowledge Extraction Audit"""
    result = {
        'status': 'PASS',
        'knowledge_areas': [],
        'metrics': {}
    }
    
    # Check for knowledge files
    knowledge_areas = ['Business', 'Architecture', 'Pipeline', 'Workflow', 
                       'Rules', 'Formula', 'Requirement', 'Decision', 'Constraint']
    
    docs_dir = os.path.join(project_dir, 'docs')
    if os.path.exists(docs_dir):
        for area in knowledge_areas:
            area_file = os.path.join(docs_dir, f'{area.lower()}.md')
            if os.path.exists(area_file):
                result['knowledge_areas'].append(area)
    
    result['metrics']['knowledge_areas_found'] = len(result['knowledge_areas'])
    result['metrics']['knowledge_coverage'] = len(result['knowledge_areas']) / len(knowledge_areas) * 100
    
    return result


def audit_requirement_discovery(project_dir):
    """Audit 2: Requirement Discovery Audit"""
    result = {
        'status': 'PASS',
        'requirements': [],
        'metrics': {}
    }
    
    # Look for requirement files
    req_file = os.path.join(project_dir, 'docs', 'requirements.md')
    if os.path.exists(req_file):
        with open(req_file, 'r') as f:
            content = f.read()
            # Count requirements (lines starting with REQ-)
            requirements = [line for line in content.split('\n') if line.strip().startswith('REQ-')]
            result['requirements'] = requirements[:10]  # First 10
            result['metrics']['total_requirements'] = len(requirements)
    else:
        result['metrics']['total_requirements'] = 0
        result['status'] = 'WARNING'
        result['issues'] = ['Requirements file not found']
    
    return result


def audit_component_discovery(project_dir):
    """Audit 4: Component Discovery Audit"""
    result = {
        'status': 'PASS',
        'components': [],
        'metrics': {}
    }
    
    source_dir = os.path.join(project_dir, 'source')
    components = []
    
    if os.path.exists(source_dir):
        for item in os.listdir(source_dir):
            components.append(item)
    
    result['components'] = components[:20]  # First 20
    result['metrics']['total_components'] = len(components)
    
    return result


def audit_artifact_discovery(project_dir):
    """Audit 5: Artifact Discovery Audit"""
    result = {
        'status': 'PASS',
        'artifacts': [],
        'metrics': {}
    }
    
    expected_artifacts = [
        'FIRST_SPEC.md', 'FINAL_SPEC.md', 'Operational_Orientation.md',
        'Build_Passport.md', 'Constitution.md'
    ]
    
    found_artifacts = []
    for artifact in expected_artifacts:
        artifact_path = os.path.join(project_dir, 'docs', artifact)
        if os.path.exists(artifact_path):
            found_artifacts.append(artifact)
    
    result['artifacts'] = found_artifacts
    result['metrics']['total_artifacts'] = len(found_artifacts)
    result['metrics']['expected_artifacts'] = len(expected_artifacts)
    result['metrics']['artifact_coverage'] = len(found_artifacts) / len(expected_artifacts) * 100
    
    if len(found_artifacts) < len(expected_artifacts):
        result['status'] = 'WARNING'
        missing = set(expected_artifacts) - set(found_artifacts)
        result['issues'] = [f'Missing artifacts: {", ".join(missing)}']
    
    return result


def audit_file_discovery(project_dir):
    """Audit 6: File Discovery Audit"""
    result = {
        'status': 'PASS',
        'files': [],
        'directories': [],
        'metrics': {}
    }
    
    for root, dirs, files in os.walk(project_dir):
        rel_root = os.path.relpath(root, project_dir)
        if rel_root != '.':
            result['directories'].append(rel_root)
        
        for file in files:
            if not file.startswith('.'):
                result['files'].append(os.path.join(rel_root, file))
    
    result['metrics']['total_files'] = len(result['files'])
    result['metrics']['total_directories'] = len(result['directories'])
    
    return result


def audit_traceability(project_dir):
    """Audit 7: Traceability Audit"""
    result = {
        'status': 'PASS',
        'traceability_chain': [],
        'metrics': {}
    }
    
    # Check traceability chain: Requirements -> Documents -> Source -> Tests
    chain_complete = True
    
    req_file = os.path.join(project_dir, 'docs', 'requirements.md')
    source_dir = os.path.join(project_dir, 'source')
    tests_dir = os.path.join(project_dir, 'tests')
    
    has_requirements = os.path.exists(req_file)
    has_source = os.path.exists(source_dir) and len(os.listdir(source_dir)) > 0
    has_tests = os.path.exists(tests_dir) and len(os.listdir(tests_dir)) > 0
    
    result['traceability_chain'] = {
        'requirements': has_requirements,
        'source': has_source,
        'tests': has_tests
    }
    
    if not has_requirements or not has_source:
        chain_complete = False
        result['status'] = 'FAIL'
    
    result['metrics']['traceability_score'] = 100 if chain_complete else 50
    
    return result


def audit_architecture(project_dir):
    """Audit 10: Architecture Audit"""
    result = {
        'status': 'PASS',
        'layers': {},
        'metrics': {}
    }
    
    # Check expected folder structure
    expected_folders = ['docs', 'source', 'reference', 'runtime', 'tests', 'exports', 'reports', 'chat']
    found_folders = []
    
    for folder in expected_folders:
        folder_path = os.path.join(project_dir, folder)
        if os.path.exists(folder_path):
            found_folders.append(folder)
    
    result['layers']['expected_folders'] = expected_folders
    result['layers']['found_folders'] = found_folders
    result['metrics']['folder_coverage'] = len(found_folders) / len(expected_folders) * 100
    
    if len(found_folders) < len(expected_folders):
        result['status'] = 'WARNING'
        missing = set(expected_folders) - set(found_folders)
        result['issues'] = [f'Missing folders: {", ".join(missing)}']
    
    return result


def audit_specification_quality(project_dir):
    """Audit 13: Specification Quality Audit"""
    result = {
        'status': 'PASS',
        'quality_metrics': {},
        'score': 0
    }
    
    # Check specification files
    spec_files = ['FIRST_SPEC.md', 'FINAL_SPEC.md']
    found_specs = []
    
    for spec in spec_files:
        spec_path = os.path.join(project_dir, 'docs', spec)
        if os.path.exists(spec_path):
            found_specs.append(spec)
            with open(spec_path, 'r') as f:
                content = f.read()
                # Basic quality checks
                word_count = len(content.split())
                if word_count < 100:
                    result['status'] = 'WARNING'
                    result['issues'] = [f'{spec} seems too short ({word_count} words)']
    
    result['quality_metrics']['specs_found'] = len(found_specs)
    result['quality_metrics']['specs_expected'] = len(spec_files)
    result['score'] = len(found_specs) / len(spec_files) * 100
    
    return result


def audit_document_relation(project_dir):
    """Audit 14: Document Relation Audit"""
    result = {
        'status': 'PASS',
        'relations': [],
        'metrics': {}
    }
    
    # Check document relationships
    doc_chain = [
        ('Constitution.md', 'requirements.md'),
        ('requirements.md', 'FIRST_SPEC.md'),
        ('FIRST_SPEC.md', 'FINAL_SPEC.md')
    ]
    
    valid_relations = 0
    for doc1, doc2 in doc_chain:
        path1 = os.path.join(project_dir, 'docs', doc1)
        path2 = os.path.join(project_dir, 'docs', doc2)
        
        exists1 = os.path.exists(path1)
        exists2 = os.path.exists(path2)
        
        relation = {
            'from': doc1,
            'to': doc2,
            'valid': exists1 and exists2
        }
        result['relations'].append(relation)
        
        if relation['valid']:
            valid_relations += 1
    
    result['metrics']['valid_relations'] = valid_relations
    result['metrics']['total_relations'] = len(doc_chain)
    result['metrics']['relation_score'] = valid_relations / len(doc_chain) * 100
    
    return result


def calculate_audit_summary(audits):
    """Calculate overall audit summary"""
    total_score = 0
    score_count = 0
    warnings = 0
    failures = 0
    
    for audit_name, audit_result in audits.items():
        if 'score' in audit_result:
            total_score += audit_result['score']
            score_count += 1
        elif 'metrics' in audit_result:
            for metric_name, metric_value in audit_result['metrics'].items():
                if isinstance(metric_value, (int, float)) and metric_value <= 100:
                    total_score += metric_value
                    score_count += 1
        
        if audit_result.get('status') == 'WARNING':
            warnings += 1
        elif audit_result.get('status') == 'FAIL':
            failures += 1
    
    overall_score = total_score / score_count if score_count > 0 else 0
    
    return {
        'overall_score': round(overall_score, 2),
        'warnings': warnings,
        'failures': failures,
        'recommendation': 'READY_FOR_BUILD' if failures == 0 and overall_score >= 70 else 'NEEDS_IMPROVEMENT'
    }
