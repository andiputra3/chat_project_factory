# Pipeline Dictionary

## Project: TestProject

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
