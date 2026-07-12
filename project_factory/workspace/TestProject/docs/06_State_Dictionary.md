# State Dictionary

## Project: TestProject

| State | Context | Transitions | Guard Conditions |
|-------|---------|-------------|------------------|
| INITIALIZED | Project | → ANALYZING | Name valid |
| ANALYZING | Reference | → SPECIFYING | References loaded |
| SPECIFYING | Factory | → VALIDATING | 22 docs generated |
| VALIDATING | Specs | → FROZEN | All validations pass |
| FROZEN | Final | → BUILDING | Spec locked |
| BUILDING | Builder | → TESTING | Source generated |
| TESTING | Tests | → COMPLETE | Tests pass |
