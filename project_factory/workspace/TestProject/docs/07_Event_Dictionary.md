# Event Dictionary

## Project: TestProject

| Event | Trigger | Handler | Side Effects |
|-------|---------|---------|--------------|
| PROJECT_CREATED | User input | init_workspace | Creates folder structure |
| SPECS_GENERATED | Factory complete | validate_specs | Triggers validation |
| BUILD_STARTED | Queue processor | generate_code | Writes source files |
| TESTS_PASSED | Test runner | create_report | Updates status |
