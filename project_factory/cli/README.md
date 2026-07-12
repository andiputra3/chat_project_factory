# AI Project Factory - CLI Dashboard

## Complete CLI Interface for Project Factory

This CLI dashboard provides full control over the AI Project Factory system through a text-based interface with both numeric and keyword navigation.

## Features

### Layer 1 - AI Project Manager OS
- **Project Management**: Create, view, list, delete projects
- **Session Management**: Isolated chat sessions per project
- **File Management**: Browse, read, create, edit files
- **Chat Interface**: Interactive AI chat with session persistence
- **Audit System**: Comprehensive project auditing

### Layer 2 - Project Factory
- **Reference Analysis**: Analyze 3 reference files (chat_project_factory.txt, project_factory.md, lanjutan_project_factory.md)
- **Generate 22 Documents**: Complete specification document generation
  - Constitution
  - Object Dictionary
  - Variable Dictionary
  - Function Dictionary
  - Pipeline Dictionary
  - State Dictionary
  - Event Dictionary
  - Pattern Dictionary
  - Business Rule Registry
  - Dependency Matrix
  - Interaction Matrix
  - AI Build Guard
  - Forbidden Rules
  - Feature Registry
  - Build Manifest
  - Project Blueprint
  - Build Checklist
  - Test Registry
  - Requirements
  - RTM (Traceability Matrix)
  - Operational Orientation
  - Build Passport
- **Factory Pipeline**: Full pipeline execution from input to build queue

## Usage

### Starting the CLI

```bash
cd /workspace/project_factory
python cli/dashboard.py
```

### Navigation

The CLI supports two types of input:
1. **Numbers**: Type `1`, `2`, `3`, etc. to select menu options
2. **Keywords**: Type `project`, `factory`, `session`, etc. for quick access

### Main Menu Options

| Option | Keyword | Description |
|--------|---------|-------------|
| [1] | project | Project Management |
| [2] | factory | Project Factory (Generate 22 Docs) |
| [3] | session | Session Management |
| [4] | file | File Management |
| [5] | chat | Quick Chat Access |
| [6] | audit | Run Project Audit |
| [7] | reference | Reference Analysis |
| [0] | exit | Exit Application |

## Factory Pipeline Flow

```
Input → Reference Analysis → FIRST_SPEC → Review → 
Generate 22 Documents → Validation → FINAL_SPEC → 
Freeze → Build Passport → Queue
```

## Testing

Run all CLI tests:
```bash
python -m pytest cli/tests/test_cli.py -v
```

## Requirements

- Python 3.8+
- requests library
- Flask server running (for API connectivity)

## Project Structure

```
cli/
├── dashboard.py      # Main CLI application
├── tests/
│   └── test_cli.py   # Unit tests
└── README.md         # This file
```

## License

Part of AI Project Factory system.
