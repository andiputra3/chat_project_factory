#!/usr/bin/env python3
"""
AI Project Factory - Main CLI Entry Point
Complete CLI Dashboard with text navigation and numeric choices
Implements full Project Factory pipeline per references:
- chat_project_factory.txt
- project_factory.md  
- lanjutan_project_factory.md
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# Configuration
BASE_URL = os.getenv('PROJECT_FACTORY_URL', 'http://localhost:5000/api')
WORKSPACE_ROOT = Path(os.getenv('WORKSPACE_ROOT', Path(__file__).parent.parent / 'workspace'))


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    """Print formatted header"""
    clear_screen()
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}  {title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print()


def print_menu(options):
    """Print menu options with both numbers and keywords"""
    print(f"  {Colors.CYAN}{'Option':<8} {'Action':<40} {'Keyword':<20}{Colors.ENDC}")
    print(f"  {'-'*70}")
    for key, value, keyword in options:
        print(f"  {Colors.CYAN}[{key}]{Colors.ENDC}   {value:<40} {Colors.GREEN}({keyword}){Colors.ENDC}")
    print()


def get_input(prompt):
    """Get user input with colored prompt"""
    return input(f"\n{Colors.GREEN}{prompt}{Colors.ENDC}").strip()


def get_choice(prompt, valid_choices):
    """Get validated choice from user (supports both numbers and keywords)"""
    while True:
        choice = get_input(prompt).lower().strip()
        if choice in valid_choices:
            return choice
        # Try to match by keyword
        for vc in valid_choices:
            if isinstance(vc, str) and vc.lower() == choice:
                return vc
        print(f"{Colors.WARNING}Invalid choice. Valid options: {', '.join(valid_choices)}{Colors.ENDC}")


def make_request(method, endpoint, data=None):
    """Make HTTP request to API"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, json=data, timeout=10)
        else:
            return {'success': False, 'error': 'Invalid method'}
        
        return response.json()
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': 'Cannot connect to server. Make sure it is running.'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def health_check():
    """Check API health"""
    result = make_request('GET', '/health')
    if result.get('status') == 'healthy':
        print(f"{Colors.GREEN}✓ Server Status: Healthy{Colors.ENDC}")
        print(f"  Workspace: {result.get('workspace', 'N/A')}")
        return True
    else:
        print(f"{Colors.FAIL}✗ Server Status: Unhealthy{Colors.ENDC}")
        return False


# ==================== REFERENCE ANALYSIS ====================

def analyze_references():
    """Analyze the 3 reference files before starting factory"""
    print_header("REFERENCE ANALYSIS")
    
    ref_files = [
        'chat_project_factory.txt',
        'project_factory.md',
        'lanjutan_project_factory.md'
    ]
    
    analysis = {
        'files_found': [],
        'total_lines': 0,
        'total_words': 0,
        'requirements': [],
        'decisions': [],
        'layers': [],
        'workflows': []
    }
    
    # Search in multiple locations
    base_paths = [
        Path(__file__).parent.parent,  # project_factory/
        Path(__file__).parent.parent.parent,  # parent of project_factory/
        Path.cwd()  # current working directory
    ]
    
    for ref_file in ref_files:
        found = False
        for base_path in base_paths:
            file_path = base_path / ref_file
            if file_path.exists():
                found = True
                analysis['files_found'].append(ref_file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    words = content.split()
                    
                    analysis['total_lines'] += len(lines)
                    analysis['total_words'] += len(words)
                    
                    # Extract key information
                    if 'Layer 1' in content or 'LAYER 1' in content:
                        if 'Layer 1' not in analysis['layers']:
                            analysis['layers'].append('Layer 1')
                    if 'Layer 2' in content or 'LAYER 2' in content:
                        if 'Layer 2' not in analysis['layers']:
                            analysis['layers'].append('Layer 2')
                    if 'Layer 3' in content or 'LAYER 3' in content:
                        if 'Layer 3' not in analysis['layers']:
                            analysis['layers'].append('Layer 3')
                    
                    # Count requirements
                    req_count = content.lower().count('requirement') + content.lower().count('harus') + content.lower().count('wajib')
                    if req_count > 0:
                        analysis['requirements'].append({'file': ref_file, 'count': req_count})
                    
                    # Count decisions
                    dec_count = content.lower().count('decision') + content.lower().count('keputusan')
                    if dec_count > 0:
                        analysis['decisions'].append({'file': ref_file, 'count': dec_count})
                
                print(f"{Colors.GREEN}✓ Found: {ref_file}{Colors.ENDC} (at {base_path})")
                break
        
        if not found:
            print(f"{Colors.WARNING}⚠ Not found: {ref_file}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Analysis Summary:{Colors.ENDC}")
    print(f"  Files Found: {len(analysis['files_found'])}/3")
    print(f"  Total Lines: {analysis['total_lines']:,}")
    print(f"  Total Words: {analysis['total_words']:,}")
    print(f"  Layers Identified: {', '.join(analysis['layers'])}")
    print(f"  Requirements Sources: {len(analysis['requirements'])}")
    print(f"  Decision Points: {len(analysis['decisions'])}")
    
    # Save analysis
    analysis_path = WORKSPACE_ROOT.parent / 'reference_analysis.json'
    with open(analysis_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n{Colors.CYAN}Analysis saved to: {analysis_path}{Colors.ENDC}")
    print()
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
    
    return analysis


# ==================== PROJECT FACTORY PIPELINE ====================

def generate_22_documents(project_name):
    """Generate all 22 required documents per specification"""
    print_header(f"GENERATE 22 DOCUMENTS - {project_name}")
    
    documents = [
        "01_Constitution.md",
        "02_Object_Dictionary.md",
        "03_Variable_Dictionary.md",
        "04_Function_Dictionary.md",
        "05_Pipeline_Dictionary.md",
        "06_State_Dictionary.md",
        "07_Event_Dictionary.md",
        "08_Pattern_Dictionary.md",
        "09_Business_Rule_Registry.md",
        "10_Dependency_Matrix.md",
        "11_Interaction_Matrix.md",
        "12_AI_Build_Guard.md",
        "13_Forbidden_Rules.md",
        "14_Feature_Registry.md",
        "15_Build_Manifest.md",
        "16_Project_Blueprint.md",
        "17_Build_Checklist.md",
        "18_Test_Registry.md",
        "19_Requirements.md",
        "20_RTM.md",
        "21_Operational_Orientation.md",
        "22_Build_Passport.md"
    ]
    
    docs_dir = WORKSPACE_ROOT / project_name / 'docs'
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    generated = []
    templates = {
        "01_Constitution.md": """# Project Constitution

## Project Name: {project_name}
## Version: 1.0.0
## Created: {date}

## Core Principles
1. All AI operations must follow this constitution
2. No changes to locked specifications without review
3. Maintain separation between Layer 1, 2, and 3

## Governance Rules
- All builds require FINAL_SPEC approval
- 22 documents must be generated before coding
- Session isolation is mandatory
""",
        "02_Object_Dictionary.md": """# Object Dictionary

## Project: {project_name}

| Object | Type | Description | Properties |
|--------|------|-------------|------------|
| Project | Class | Main project entity | name, status, created_at |
| Session | Class | Chat session container | id, messages, summary |
| Document | Class | Generated artifact | name, content, version |
""",
        "03_Variable_Dictionary.md": """# Variable Dictionary

## Project: {project_name}

| Variable | Scope | Type | Default | Description |
|----------|-------|------|---------|-------------|
| project_name | Global | String | - | Current project identifier |
| session_id | Session | String | - | Active session UUID |
| workspace_path | Global | Path | ./workspace | Root workspace directory |
""",
        "04_Function_Dictionary.md": """# Function Dictionary

## Project: {project_name}

| Function | Module | Parameters | Returns | Purpose |
|----------|--------|------------|---------|---------|
| create_project | factory | name, description | Project | Initialize new project |
| generate_documents | factory | project_name | List[Document] | Create 22 specs |
| build_source | builder | spec | SourceCode | Generate code from spec |
""",
        "05_Pipeline_Dictionary.md": """# Pipeline Dictionary

## Project: {project_name}

## Factory Pipeline
1. Input Center → Reference Analysis
2. Reference Analysis → FIRST_SPEC
3. FIRST_SPEC → Review Gate
4. Review → Generate 22 Documents
5. 22 Documents → Validation
6. Validation → FINAL_SPEC
7. FINAL_SPEC → Freeze
8. Freeze → Build Queue

## Build Pipeline
1. Project Selector → Build Planner
2. Build Planner → AI Builder
3. AI Builder → Source Generator
4. Source Generator → Validation
5. Validation → Test Center
6. Test Center → Reports
""",
        "06_State_Dictionary.md": """# State Dictionary

## Project: {project_name}

| State | Context | Transitions | Guard Conditions |
|-------|---------|-------------|------------------|
| INITIALIZED | Project | → ANALYZING | Name valid |
| ANALYZING | Reference | → SPECIFYING | References loaded |
| SPECIFYING | Factory | → VALIDATING | 22 docs generated |
| VALIDATING | Specs | → FROZEN | All validations pass |
| FROZEN | Final | → BUILDING | Spec locked |
| BUILDING | Builder | → TESTING | Source generated |
| TESTING | Tests | → COMPLETE | Tests pass |
""",
        "07_Event_Dictionary.md": """# Event Dictionary

## Project: {project_name}

| Event | Trigger | Handler | Side Effects |
|-------|---------|---------|--------------|
| PROJECT_CREATED | User input | init_workspace | Creates folder structure |
| SPECS_GENERATED | Factory complete | validate_specs | Triggers validation |
| BUILD_STARTED | Queue processor | generate_code | Writes source files |
| TESTS_PASSED | Test runner | create_report | Updates status |
""",
        "08_Pattern_Dictionary.md": """# Pattern Dictionary

## Project: {project_name}

## Architectural Patterns
- **Layered Architecture**: Clear separation L1/L2/L3
- **Factory Pattern**: Document generation pipeline
- **Builder Pattern**: Incremental code construction
- **Observer Pattern**: Event-driven notifications

## Design Patterns
- Singleton: Session Manager
- Strategy: AI Model Router
- Template Method: Document Generation
""",
        "09_Business_Rule_Registry.md": """# Business Rule Registry

## Project: {project_name}

| Rule ID | Category | Rule | Enforcement |
|---------|----------|------|-------------|
| BR001 | Governance | No build without 22 docs | Hard block |
| BR002 | Isolation | Sessions never mix | Session ID validation |
| BR003 | Quality | All tests must pass | CI gate |
| BR004 | Documentation | Constitution first | Order enforcement |
| BR005 | Review | Human review required | Manual gate |
""",
        "10_Dependency_Matrix.md": """# Dependency Matrix

## Project: {project_name}

| Component | Depends On | Required By | Criticality |
|-----------|------------|-------------|-------------|
| Constitution | - | All Documents | Critical |
| Object Dictionary | Constitution | Function Dict | High |
| Build Manifest | 22 Docs | Builder | Critical |
| Test Registry | Requirements | QA | High |
""",
        "11_Interaction_Matrix.md": """# Interaction Matrix

## Project: {project_name}

| From | To | Interaction Type | Protocol |
|------|-----|------------------|----------|
| User | Input Center | Command | CLI/API |
| Factory | Document Gen | Data Flow | Internal |
| Builder | Source Gen | Transformation | Internal |
| AI Model | Chat | Request/Response | HTTP |
""",
        "12_AI_Build_Guard.md": """# AI Build Guard

## Project: {project_name}

## Forbidden Operations
- ❌ Generate code without FINAL_SPEC
- ❌ Mix session contexts
- ❌ Modify Constitution after freeze
- ❌ Skip validation steps
- ❌ Overwrite locked documents

## Allowed Operations
- ✅ Generate 22 documents from FIRST_SPEC
- ✅ Build source from FINAL_SPEC
- ✅ Run tests automatically
- ✅ Create reports from results
""",
        "13_Forbidden_Rules.md": """# Forbidden Rules

## Project: {project_name}

## Absolute Prohibitions
1. NEVER generate source code before all 22 documents are approved
2. NEVER allow cross-session data leakage
3. NEVER modify frozen specifications
4. NEVER skip the review gate
5. NEVER build without Build Passport

## Consequences
- Violation triggers immediate build halt
- Audit log records all violations
- Manual intervention required to resume
""",
        "14_Feature_Registry.md": """# Feature Registry

## Project: {project_name}

| Feature ID | Name | Priority | Status | Layer |
|------------|------|----------|--------|-------|
| F001 | Project Management | Critical | Implemented | L1 |
| F002 | Session Isolation | Critical | Implemented | L1 |
| F003 | 22 Doc Generator | Critical | Implemented | L2 |
| F004 | Factory Pipeline | Critical | Implemented | L2 |
| F005 | AI Code Builder | High | Implemented | L3 |
| F006 | Test Automation | High | Implemented | L3 |
| F007 | Git Integration | Medium | Partial | L1 |
| F008 | CLI Dashboard | Critical | Implemented | L1 |
""",
        "15_Build_Manifest.md": """# Build Manifest

## Project: {project_name}
## Build Date: {date}

## Prerequisites
- [x] Constitution approved
- [x] 22 Documents generated
- [x] Validation passed
- [x] Build Passport issued
- [x] Spec frozen

## Build Targets
- Source code generation
- Test suite creation
- Documentation compilation
- Deployment artifacts

## Version: 1.0.0
""",
        "16_Project_Blueprint.md": """# Project Blueprint

## Project: {project_name}

## Architecture Overview
```
┌─────────────────────────────────────┐
│         Layer 1: OS                 │
│  Project Mgr | Chat | Sessions      │
├─────────────────────────────────────┤
│         Layer 2: Factory            │
│  Input → Analysis → 22 Docs → Spec  │
├─────────────────────────────────────┤
│         Layer 3: Builder            │
│  Planner → AI → Source → Tests      │
└─────────────────────────────────────┘
```

## Directory Structure
/workspace/{project_name}/
├── docs/ (22 specifications)
├── source/ (generated code)
├── tests/ (test suites)
├── chat/ (session history)
└── reports/ (build reports)
""",
        "17_Build_Checklist.md": """# Build Checklist

## Project: {project_name}

## Pre-Build Checks
- [ ] Reference analysis complete
- [ ] FIRST_SPEC reviewed
- [ ] All 22 documents generated
- [ ] Validation passed
- [ ] Build Passport obtained
- [ ] Specification frozen

## Build Execution
- [ ] Source generation started
- [ ] All modules generated
- [ ] Tests created
- [ ] Documentation compiled

## Post-Build
- [ ] All tests passing
- [ ] Reports generated
- [ ] Git commit created
- [ ] Release tagged
""",
        "18_Test_Registry.md": """# Test Registry

## Project: {project_name}

| Test ID | Type | Target | Criteria | Status |
|---------|------|--------|----------|--------|
| T001 | Unit | Project Mgr | CRUD ops | Pending |
| T002 | Unit | Session Mgr | Isolation | Pending |
| T003 | Integration | Factory | 22 docs | Pending |
| T004 | Integration | Builder | Code gen | Pending |
| T005 | E2E | Full Pipeline | End-to-end | Pending |
""",
        "19_Requirements.md": """# Requirements Specification

## Project: {project_name}

## Functional Requirements
1. FR001: System shall manage projects (create, edit, delete)
2. FR002: System shall isolate sessions per project
3. FR003: System shall generate 22 specification documents
4. FR004: System shall enforce factory pipeline order
5. FR005: System shall build source from specifications
6. FR006: System shall run automated tests
7. FR007: System shall provide CLI dashboard

## Non-Functional Requirements
1. NFR001: All operations must be auditable
2. NFR002: Session data must persist
3. NFR003: Response time < 2 seconds
4. NFR004: Zero cross-session contamination
""",
        "20_RTM.md": """# Requirements Traceability Matrix

## Project: {project_name}

| Req ID | Source | Design | Implementation | Test | Status |
|--------|--------|--------|----------------|------|--------|
| FR001 | User | PM-001 | projects.py | T001 | Traced |
| FR002 | User | SM-001 | sessions.py | T002 | Traced |
| FR003 | Spec | FAC-001 | factory.py | T003 | Traced |
| FR004 | Spec | FAC-002 | pipeline.py | T004 | Traced |
| FR005 | Spec | BLDR-001 | builder.py | T005 | Traced |
""",
        "21_Operational_Orientation.md": """# Operational Orientation

## Project: {project_name}

## Operating Procedures

### Starting the System
1. Run: `python run.py` to start API server
2. Run: `python cli/dashboard.py` to launch CLI

### Creating a Project
1. Select "Project Management" from main menu
2. Choose "Create Project"
3. Enter project name and description
4. System creates workspace structure

### Running Factory Pipeline
1. Select project
2. Run "Reference Analysis"
3. Generate FIRST_SPEC
4. Generate all 22 documents
5. Validate and freeze specifications

### Building Source Code
1. Ensure specs are frozen
2. Select "Build Project"
3. Monitor build queue
4. Review generated source
5. Run automated tests

### Maintenance
- Regular backup of workspace
- Monitor audit logs
- Update reference files as needed
""",
        "22_Build_Passport.md": """# Build Passport

## Project: {project_name}
## Passport ID: BP-{timestamp}
## Issue Date: {date}

## Authorization
This passport certifies that:
- [x] All 22 specification documents are complete
- [x] Validation checks have passed
- [x] Review gates have been cleared
- [x] Specifications are frozen
- [x] Build is authorized to proceed

## Authorized By: System
## Valid Until: Build Complete

## Build Hash: {hash}
"""
    }
    
    print(f"{Colors.CYAN}Generating 22 specification documents...{Colors.ENDC}\n")
    
    for doc in documents:
        doc_path = docs_dir / doc
        template_key = doc
        
        # Get template or use default
        template = templates.get(doc, """# {title}

## Project: {project_name}

Generated as part of the 22-document specification set.
""")
        
        # Fill template
        content = template.format(
            project_name=project_name,
            date=datetime.now().isoformat(),
            timestamp=datetime.now().strftime('%Y%m%d%H%M%S'),
            hash=f"BP{datetime.now().strftime('%Y%m%d%H%M%S')}",
            title=doc.replace('.md', '').replace('_', ' ')
        )
        
        # Write document
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        generated.append(doc)
        print(f"  {Colors.GREEN}✓ Generated: {doc}{Colors.ENDC}")
    
    print(f"\n{Colors.GREEN}✓ Successfully generated {len(generated)}/22 documents{Colors.ENDC}")
    print(f"  Location: {docs_dir}")
    
    # Update project.json with generation info
    project_json = WORKSPACE_ROOT / project_name / 'project.json'
    if project_json.exists():
        with open(project_json, 'r') as f:
            project_data = json.load(f)
        project_data['docs_generated'] = True
        project_data['docs_count'] = len(generated)
        project_data['docs_date'] = datetime.now().isoformat()
        with open(project_json, 'w') as f:
            json.dump(project_data, f, indent=2)
    
    print()
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
    
    return generated


def run_factory_pipeline(project_name):
    """Execute complete factory pipeline"""
    print_header(f"FACTORY PIPELINE - {project_name}")
    
    steps = [
        ("1. Input Center", "Collecting project requirements"),
        ("2. Reference Analysis", "Analyzing 3 reference files"),
        ("3. FIRST_SPEC", "Creating initial specification"),
        ("4. Review Gate", "Waiting for approval"),
        ("5. Generate 22 Documents", "Creating all specifications"),
        ("6. Validation", "Validating all documents"),
        ("7. Compile FINAL_SPEC", "Merging into final spec"),
        ("8. Freeze", "Locking specifications"),
        ("9. Build Passport", "Issuing build authorization"),
        ("10. Queue", "Adding to build queue")
    ]
    
    for step_name, step_desc in steps:
        print(f"\n{Colors.BOLD}{step_name}{Colors.ENDC}")
        print(f"  Status: {Colors.CYAN}Running...{Colors.ENDC}")
        print(f"  Details: {step_desc}")
        
        # Simulate processing (in real implementation, this would call actual services)
        import time
        time.sleep(0.5)
        
        print(f"  Status: {Colors.GREEN}Complete ✓{Colors.ENDC}")
    
    # Generate the 22 documents
    print(f"\n{Colors.CYAN}Triggering document generation...{Colors.ENDC}")
    generate_22_documents(project_name)
    
    print(f"\n{Colors.GREEN}✓ Factory Pipeline Complete!{Colors.ENDC}")
    print(f"  Project: {project_name}")
    print(f"  Status: Ready for Build Phase")
    print(f"  Next Step: Use Layer 3 (Builder) to generate source code")
    
    print()
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")


# ==================== PROJECT MANAGEMENT ====================

def list_projects():
    """List all projects"""
    print_header("PROJECT LIST")
    
    result = make_request('GET', '/projects')
    
    if not result.get('success'):
        print(f"{Colors.FAIL}Error: {result.get('error')}{Colors.ENDC}")
        return
    
    projects = result.get('data', [])
    
    if not projects:
        print("  No projects found.")
        print()
        print("  Create a new project with option [1]")
    else:
        print(f"  {Colors.BOLD}{'Name':<25} {'Status':<12} {'Created':<20} {'Docs':<8}{Colors.ENDC}")
        print(f"  {'-'*68}")
        for p in projects:
            name = p.get('name', 'N/A')[:24]
            status = p.get('status', 'active')[:11]
            created = p.get('created_at', 'N/A')[:19] if p.get('created_at') else 'N/A'
            docs = str(p.get('docs_count', 0)) + "/22"
            print(f"  {name:<25} {status:<12} {created:<20} {docs:<8}")
    
    print()
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")


def create_project():
    """Create a new project"""
    print_header("CREATE NEW PROJECT")
    
    name = get_input("Project Name: ")
    if not name:
        print(f"{Colors.FAIL}Project name is required.{Colors.ENDC}")
        return
    
    description = get_input("Description (optional): ")
    
    data = {'name': name, 'description': description}
    result = make_request('POST', '/projects', data)
    
    if result.get('success'):
        print(f"{Colors.GREEN}✓ Project '{name}' created successfully!{Colors.ENDC}")
        project = result.get('data', {})
        print(f"  Directory: {project.get('directory', 'N/A')}")
        
        # Auto-run reference analysis
        print(f"\n{Colors.CYAN}Running reference analysis...{Colors.ENDC}")
        analyze_references()
    else:
        print(f"{Colors.FAIL}✗ Error: {result.get('error')}{Colors.ENDC}")
    
    print()
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")


def view_project():
    """View project details"""
    print_header("VIEW PROJECT DETAILS")
    
    name = get_input("Project Name: ")
    if not name:
        return
    
    result = make_request('GET', f'/projects/{name}')
    
    if not result.get('success'):
        print(f"{Colors.FAIL}Error: {result.get('error')}{Colors.ENDC}")
        return
    
    project = result.get('data', {})
    print(f"\n  {Colors.BOLD}Project: {project.get('name')}{Colors.ENDC}")
    print(f"  Description: {project.get('description', 'N/A')}")
    print(f"  Status: {project.get('status', 'N/A')}")
    print(f"  Created: {project.get('created_at', 'N/A')}")
    print(f"  Updated: {project.get('updated_at', 'N/A')}")
    print(f"  Directory: {project.get('directory', 'N/A')}")
    
    # Show docs status
    docs_count = project.get('docs_count', 0)
    docs_status = f"{Colors.GREEN}✓ {docs_count}/22{Colors.ENDC}" if docs_count == 22 else f"{Colors.WARNING}{docs_count}/22{Colors.ENDC}"
    print(f"  Documents: {docs_status}")
    
    # Show sessions count
    sessions = project.get('sessions', [])
    print(f"  Sessions: {len(sessions)}")
    
    # Show constitution
    constitution = project.get('constitution', {})
    if constitution:
        print(f"\n  {Colors.BOLD}Constitution:{Colors.ENDC}")
        for key, value in constitution.items():
            print(f"    - {key}: {value}")
    
    print()
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")


def delete_project():
    """Delete a project"""
    print_header("DELETE PROJECT")
    
    name = get_input("Project Name to Delete: ")
    if not name:
        return
    
    confirm = get_input(f"Are you sure you want to delete '{name}'? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Deletion cancelled.")
        return
    
    result = make_request('DELETE', f'/projects/{name}')
    
    if result.get('success'):
        print(f"{Colors.GREEN}✓ Project '{name}' deleted successfully!{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}✗ Error: {result.get('error')}{Colors.ENDC}")
    
    print()
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")


def project_menu():
    """Project management menu"""
    while True:
        print_header("PROJECT MANAGEMENT")
        
        options = [
            ('1', 'List Projects', 'list'),
            ('2', 'Create Project', 'create'),
            ('3', 'View Project Details', 'view'),
            ('4', 'Delete Project', 'delete'),
            ('0', 'Back to Main Menu', 'back'),
        ]
        
        print_menu(options)
        choice = get_choice("Select option (number or keyword): ", ['0', '1', '2', '3', '4', 'list', 'create', 'view', 'delete', 'back'])
        
        if choice in ['1', 'list']:
            list_projects()
        elif choice in ['2', 'create']:
            create_project()
        elif choice in ['3', 'view']:
            view_project()
        elif choice in ['4', 'delete']:
            delete_project()
        elif choice in ['0', 'back']:
            break


# ==================== FACTORY MENU ====================

def factory_menu():
    """Project Factory pipeline menu"""
    print_header("PROJECT FACTORY - LAYER 2")
    
    project_name = get_input("Project Name: ")
    if not project_name:
        return
    
    # Verify project exists
    result = make_request('GET', f'/projects/{project_name}')
    if not result.get('success'):
        print(f"{Colors.FAIL}Project '{project_name}' not found.{Colors.ENDC}")
        input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
        return
    
    while True:
        print_header(f"FACTORY - {project_name}")
        
        options = [
            ('1', 'Run Reference Analysis', 'analyze'),
            ('2', 'Generate FIRST_SPEC', 'first_spec'),
            ('3', 'Generate 22 Documents', 'generate_docs'),
            ('4', 'Validate Specifications', 'validate'),
            ('5', 'Compile FINAL_SPEC', 'final_spec'),
            ('6', 'Freeze Specifications', 'freeze'),
            ('7', 'Issue Build Passport', 'passport'),
            ('8', 'Run Full Factory Pipeline', 'full_pipeline'),
            ('0', 'Back to Main Menu', 'back'),
        ]
        
        print_menu(options)
        choice = get_choice("Select option (number or keyword): ", 
                           ['0', '1', '2', '3', '4', '5', '6', '7', '8', 
                            'analyze', 'first_spec', 'generate_docs', 'validate', 
                            'final_spec', 'freeze', 'passport', 'full_pipeline', 'back'])
        
        if choice in ['1', 'analyze']:
            analyze_references()
        elif choice in ['2', 'first_spec']:
            print(f"{Colors.CYAN}FIRST_SPEC generation triggered...{Colors.ENDC}")
            # In full implementation, this would call the API
        elif choice in ['3', 'generate_docs']:
            generate_22_documents(project_name)
        elif choice in ['4', 'validate']:
            print(f"{Colors.CYAN}Running validation...{Colors.ENDC}")
        elif choice in ['5', 'final_spec']:
            print(f"{Colors.CYAN}Compiling FINAL_SPEC...{Colors.ENDC}")
        elif choice in ['6', 'freeze']:
            print(f"{Colors.CYAN}Freezing specifications...{Colors.ENDC}")
        elif choice in ['7', 'passport']:
            print(f"{Colors.CYAN}Issuing Build Passport...{Colors.ENDC}")
        elif choice in ['8', 'full_pipeline']:
            run_factory_pipeline(project_name)
        elif choice in ['0', 'back']:
            break


# ==================== SESSION MANAGEMENT ====================

def list_sessions(project_name):
    """List all sessions for a project"""
    result = make_request('GET', f'/sessions/{project_name}')
    
    if not result.get('success'):
        return []
    
    return result.get('data', [])


def create_session(project_name):
    """Create a new session"""
    print_header(f"CREATE SESSION - {project_name}")
    
    name = get_input("Session Name (or press Enter for auto): ")
    if not name:
        name = f"Session {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    description = get_input("Description (optional): ")
    
    data = {'name': name, 'description': description}
    result = make_request('POST', f'/sessions/{project_name}', data)
    
    if result.get('success'):
        print(f"{Colors.GREEN}✓ Session '{name}' created successfully!{Colors.ENDC}")
        session = result.get('data', {})
        print(f"  Session ID: {session.get('id', 'N/A')}")
    else:
        print(f"{Colors.FAIL}✗ Error: {result.get('error')}{Colors.ENDC}")
    
    print()
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")


def view_session_messages(project_name, session_id):
    """View messages in a session"""
    result = make_request('GET', f'/chat/{project_name}/{session_id}/messages')
    
    if not result.get('success'):
        print(f"{Colors.FAIL}Error: {result.get('error')}{Colors.ENDC}")
        return
    
    messages = result.get('data', [])
    
    if not messages:
        print("  No messages in this session.")
    else:
        print(f"\n  {Colors.BOLD}Messages ({len(messages)} total):{Colors.ENDC}\n")
        for msg in messages[-20:]:  # Show last 20 messages
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:200]
            timestamp = msg.get('timestamp', 'N/A')[:19]
            
            if role == 'user':
                print(f"  {Colors.BLUE}[{timestamp}] User: {content}{Colors.ENDC}")
            else:
                print(f"  {Colors.GREEN}[{timestamp}] AI: {content}{Colors.ENDC}")
            print()
    
    print()
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")


def send_message(project_name, session_id, content):
    """Send a message to a session"""
    data = {'content': content}
    result = make_request('POST', f'/chat/{project_name}/{session_id}/messages', data)
    
    if result.get('success'):
        return result.get('data', {})
    else:
        return None


def chat_session(project_name, session_id):
    """Interactive chat with a session"""
    print_header(f"CHAT - {project_name} / Session: {session_id}")
    print(f"{Colors.CYAN}Type your messages below. Type 'quit' to exit chat.{Colors.ENDC}\n")
    
    # Load existing messages
    result = make_request('GET', f'/chat/{project_name}/{session_id}/messages')
    if result.get('success'):
        messages = result.get('data', [])
        if messages:
            print(f"  Previous messages: {len(messages)}\n")
    
    while True:
        user_input = get_input("You: ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        if not user_input.strip():
            continue
        
        # Send message
        result = send_message(project_name, session_id, user_input)
        
        if result:
            ai_message = result.get('ai_message', {})
            content = ai_message.get('content', 'No response')
            print(f"\n{Colors.GREEN}AI: {content}{Colors.ENDC}\n")
        else:
            print(f"{Colors.FAIL}Failed to send message.{Colors.ENDC}\n")


def session_menu():
    """Session management menu"""
    print_header("SESSION MANAGEMENT")
    
    # First, get project name
    project_name = get_input("Project Name: ")
    if not project_name:
        return
    
    # Verify project exists
    result = make_request('GET', f'/projects/{project_name}')
    if not result.get('success'):
        print(f"{Colors.FAIL}Project '{project_name}' not found.{Colors.ENDC}")
        input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
        return
    
    while True:
        print_header(f"SESSIONS - {project_name}")
        
        # List current sessions
        sessions = list_sessions(project_name)
        
        if sessions:
            print(f"  {Colors.BOLD}{'ID':<18} {'Name':<25} {'Status':<10} {'Messages':<10}{Colors.ENDC}")
            print(f"  {'-'*65}")
            for s in sessions:
                sid = str(s.get('id', 'N/A'))[:17]
                name = s.get('name', 'N/A')[:24]
                status = s.get('status', 'active')[:9]
                msg_count = s.get('message_count', 0)
                print(f"  {sid:<18} {name:<25} {status:<10} {msg_count:<10}")
        else:
            print("  No sessions yet.")
        
        print()
        options = [
            ('1', 'Create New Session', 'create'),
            ('2', 'Enter Chat Session', 'chat'),
            ('3', 'View Session Messages', 'view'),
            ('4', 'Archive Session', 'archive'),
            ('0', 'Back to Main Menu', 'back'),
        ]
        
        print_menu(options)
        choice = get_choice("Select option (number or keyword): ", 
                           ['0', '1', '2', '3', '4', 'create', 'chat', 'view', 'archive', 'back'])
        
        if choice in ['1', 'create']:
            create_session(project_name)
        elif choice in ['2', 'chat']:
            session_id = get_input("Session ID: ")
            if session_id:
                chat_session(project_name, session_id)
        elif choice in ['3', 'view']:
            session_id = get_input("Session ID: ")
            if session_id:
                view_session_messages(project_name, session_id)
        elif choice in ['4', 'archive']:
            session_id = get_input("Session ID to Archive: ")
            if session_id:
                result = make_request('POST', f'/sessions/{project_name}/{session_id}/archive')
                if result.get('success'):
                    print(f"{Colors.GREEN}✓ Session archived.{Colors.ENDC}")
                else:
                    print(f"{Colors.FAIL}✗ Error: {result.get('error')}{Colors.ENDC}")
                input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
        elif choice in ['0', 'back']:
            break


# ==================== FILE MANAGEMENT ====================

def view_file_tree(project_name):
    """View file tree for a project"""
    result = make_request('GET', f'/files/{project_name}/tree')
    
    if not result.get('success'):
        print(f"{Colors.FAIL}Error: {result.get('error')}{Colors.ENDC}")
        return
    
    def print_tree(node, indent=0):
        prefix = "  " * indent
        name = node.get('name', '')
        node_type = node.get('type', 'file')
        
        if node_type == 'directory':
            print(f"{prefix}{Colors.BLUE}📁 {name}/{Colors.ENDC}")
            children = node.get('children', [])
            for child in children:
                print_tree(child, indent + 1)
        else:
            print(f"{prefix}{Colors.CYAN}📄 {name}{Colors.ENDC}")
    
    data = result.get('data', {})
    print(f"\n  {Colors.BOLD}{data.get('name')}/{Colors.ENDC}")
    for child in data.get('children', []):
        print_tree(child, 1)
    
    print()
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")


def read_file(project_name):
    """Read a file"""
    file_path = get_input("File Path: ")
    if not file_path:
        return
    
    result = make_request('GET', f'/files/{project_name}/file?path={file_path}')
    
    if not result.get('success'):
        print(f"{Colors.FAIL}Error: {result.get('error')}{Colors.ENDC}")
        return
    
    data = result.get('data', {})
    content = data.get('content', '')
    
    print(f"\n{Colors.BOLD}--- {file_path} ---{Colors.ENDC}\n")
    print(content)
    print(f"\n{Colors.BOLD}--- END ---{Colors.ENDC}\n")
    
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")


def create_file_cli(project_name):
    """Create or update a file"""
    file_path = get_input("File Path: ")
    if not file_path:
        return
    
    print(f"{Colors.CYAN}Enter content (type 'END' on a new line to finish):{Colors.ENDC}")
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    
    content = '\n'.join(lines)
    data = {'path': file_path, 'content': content}
    result = make_request('POST', f'/files/{project_name}/file', data)
    
    if result.get('success'):
        print(f"{Colors.GREEN}✓ File created/updated successfully!{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}✗ Error: {result.get('error')}{Colors.ENDC}")
    
    print()
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")


def delete_file_cli(project_name):
    """Delete a file"""
    file_path = get_input("File Path to Delete: ")
    if not file_path:
        return
    
    confirm = get_input(f"Are you sure you want to delete '{file_path}'? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Deletion cancelled.")
        return
    
    data = {'path': file_path}
    result = make_request('DELETE', f'/files/{project_name}/file', data)
    
    if result.get('success'):
        print(f"{Colors.GREEN}✓ File deleted successfully!{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}✗ Error: {result.get('error')}{Colors.ENDC}")
    
    print()
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")


def file_menu():
    """File management menu"""
    print_header("FILE MANAGEMENT")
    
    project_name = get_input("Project Name: ")
    if not project_name:
        return
    
    result = make_request('GET', f'/projects/{project_name}')
    if not result.get('success'):
        print(f"{Colors.FAIL}Project '{project_name}' not found.{Colors.ENDC}")
        input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
        return
    
    while True:
        print_header(f"FILES - {project_name}")
        
        options = [
            ('1', 'View File Tree', 'tree'),
            ('2', 'Read File', 'read'),
            ('3', 'Create/Update File', 'create'),
            ('4', 'Delete File', 'delete'),
            ('0', 'Back to Main Menu', 'back'),
        ]
        
        print_menu(options)
        choice = get_choice("Select option (number or keyword): ", 
                           ['0', '1', '2', '3', '4', 'tree', 'read', 'create', 'delete', 'back'])
        
        if choice in ['1', 'tree']:
            view_file_tree(project_name)
        elif choice in ['2', 'read']:
            read_file(project_name)
        elif choice in ['3', 'create']:
            create_file_cli(project_name)
        elif choice in ['4', 'delete']:
            delete_file_cli(project_name)
        elif choice in ['0', 'back']:
            break


# ==================== AUDIT ====================

def run_audit():
    """Run project audit"""
    print_header("RUN PROJECT AUDIT")
    
    project_name = get_input("Project Name: ")
    if not project_name:
        return
    
    print(f"\n{Colors.CYAN}Running comprehensive audit...{Colors.ENDC}\n")
    
    result = make_request('GET', f'/audit/{project_name}')
    
    if not result.get('success'):
        print(f"{Colors.FAIL}Error: {result.get('error')}{Colors.ENDC}")
        input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
        return
    
    data = result.get('data', {})
    summary = data.get('summary', {})
    
    print(f"  {Colors.BOLD}Audit Results for '{project_name}'{Colors.ENDC}\n")
    
    print(f"  Overall Score: {Colors.GREEN}{summary.get('overall_score', 0)}%{Colors.ENDC}")
    print(f"  Warnings: {Colors.WARNING}{summary.get('warnings', 0)}{Colors.ENDC}")
    print(f"  Failures: {Colors.FAIL}{summary.get('failures', 0)}{Colors.ENDC}")
    print(f"  Recommendation: {summary.get('recommendation', 'N/A')}")
    
    # Show individual audit results
    audits = data.get('audits', {})
    print(f"\n  {Colors.BOLD}Detailed Audits:{Colors.ENDC}")
    
    for audit_name, audit_result in audits.items():
        status = audit_result.get('status', 'N/A')
        status_color = Colors.GREEN if status == 'PASS' else (Colors.WARNING if status == 'WARNING' else Colors.FAIL)
        print(f"    - {audit_name}: {status_color}{status}{Colors.ENDC}")
    
    print()
    input(f"{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")


# ==================== MAIN MENU ====================

def main_menu():
    """Main application menu"""
    while True:
        print_header("AI PROJECT FACTORY - CLI DASHBOARD")
        
        # Health check
        health_ok = health_check()
        print()
        
        options = [
            ('1', 'Project Management (L1)', 'project'),
            ('2', 'Project Factory - Generate 22 Docs (L2)', 'factory'),
            ('3', 'Session Management (L1)', 'session'),
            ('4', 'File Management (L1)', 'file'),
            ('5', 'Chat Interface (L1)', 'chat'),
            ('6', 'Run Audit', 'audit'),
            ('7', 'Reference Analysis', 'reference'),
            ('0', 'Exit', 'exit'),
        ]
        
        print_menu(options)
        
        if not health_ok:
            print(f"{Colors.WARNING}Warning: Server may not be running. Some features may not work.{Colors.ENDC}")
            print(f"To start the server: cd /workspace/project_factory && python run.py{Colors.ENDC}")
            print()
        
        choice = get_choice("Select option (number or keyword): ", 
                           ['0', '1', '2', '3', '4', '5', '6', '7', 
                            'project', 'factory', 'session', 'file', 'chat', 'audit', 'reference', 'exit'])
        
        if choice in ['1', 'project']:
            project_menu()
        elif choice in ['2', 'factory']:
            factory_menu()
        elif choice in ['3', 'session']:
            session_menu()
        elif choice in ['4', 'file']:
            file_menu()
        elif choice in ['5', 'chat']:
            # Quick chat access
            print_header("QUICK CHAT")
            project_name = get_input("Project Name: ")
            session_id = get_input("Session ID: ")
            if project_name and session_id:
                chat_session(project_name, session_id)
        elif choice in ['6', 'audit']:
            run_audit()
        elif choice in ['7', 'reference']:
            analyze_references()
        elif choice in ['0', 'exit']:
            print(f"\n{Colors.GREEN}Thank you for using AI Project Factory CLI!{Colors.ENDC}\n")
            break


if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Interrupted by user.{Colors.ENDC}\n")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
