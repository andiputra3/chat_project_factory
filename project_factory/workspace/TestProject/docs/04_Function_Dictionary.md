# Function Dictionary

## Project: TestProject

| Function | Module | Parameters | Returns | Purpose |
|----------|--------|------------|---------|---------|
| create_project | factory | name, description | Project | Initialize new project |
| generate_documents | factory | project_name | List[Document] | Create 22 specs |
| build_source | builder | spec | SourceCode | Generate code from spec |
