# MedEval Tests - Quick Start

## Running Tests

### Setup
```bash
cd C:\Users\Tay\Documents\GitHub\medevalTests

# Install dependencies (including medeval-framework)
poetry install

# Or install with helpers for CLI testing
poetry install --extras helpers
```

### Run Integration Tests
```bash
# From medevalTests directory
poetry run pytest

# With verbose output
poetry run pytest -v

# With coverage
poetry run pytest --cov=. --cov-report=html

# Run specific test file
poetry run pytest tests/integration/test_end_to_end_example.py
```

### Run Examples
```bash
# Run custom evaluator example
poetry run python examples/custom_evaluator_example.py
```

## Using Your Test Cases

### With Python API
```python
from medeval.dataset import load_dataset
from medeval.evaluation.runner import EvaluationRunner
from medeval.evaluators import MedicationF1Evaluator

# Load your test cases
cases = load_dataset("datasets/clinical_cases.jsonl")

# Create predictions (your model here)
predictions = [...]

# Evaluate
runner = EvaluationRunner(evaluators=[MedicationF1Evaluator()])
results = runner.run(cases, predictions)
```

### With CLI (if helpers installed)
```bash
# From medevalTests directory
poetry run medeval run --dataset datasets/clinical_cases.jsonl
```

## Adding Your Team's Test Cases

1. **Create your dataset:**
   ```bash
   cp datasets/clinical_cases.jsonl datasets/my_team_cases.jsonl
   ```

2. **Edit with your cases** (see README.md for format)

3. **Run tests:**
   ```bash
   poetry run pytest  # Integration tests
   ```

4. **Or evaluate directly:**
   ```bash
   poetry run medeval run --dataset datasets/my_team_cases.jsonl
   ```

## Directory Structure

```
medevalTests/
├── datasets/           # Your test cases here
├── baselines/          # Baseline predictions
├── examples/           # Example code
├── tests/integration/  # Integration tests
├── pyproject.toml      # Poetry config (this enables `poetry run`)
└── README.md           # Full documentation
```

## Notes

- **This repo should be forked by your team** - add your proprietary test data
- **Keep it private** if your test cases contain sensitive information
- **Use poetry** for dependency management (consistent with framework)
- **Tests run independently** - no need to set up medeval repo

## Questions?

See full README.md for:
- Test case format
- Custom evaluator examples
- Baseline management
- Team workflow best practices
