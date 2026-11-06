# Setting Up medevalTests Repository

## Quick Setup (Before PyPI Publication)

Since `medeval-framework` and `medeval-helpers` are not yet published to PyPI, you need to install them locally:

### Option 1: Install Local Editable Packages (Recommended)

```bash
cd C:\Users\Tay\Documents\GitHub\medevalTests

# Initialize environment
poetry install

# Install local framework and helpers
poetry run pip install -e ..\medeval
poetry run pip install -e ..\medevalHelpers

# Run tests
poetry run pytest
```

### Option 2: Set PYTHONPATH

```bash
cd C:\Users\Tay\Documents\GitHub\medevalTests

# Add framework to Python path
$env:PYTHONPATH = "C:\Users\Tay\Documents\GitHub\medeval\src"

# Run tests directly with pytest
pytest
```

### Option 3: Use Framework's venv

```bash
# Use the virtual environment from the framework repo
cd C:\Users\Tay\Documents\GitHub\medeval

# Activate framework's venv
.venv\Scripts\Activate.ps1

# Run tests from medevalTests directory
cd ..\medevalTests
pytest tests/integration/
```

## After PyPI Publication

Once packages are published, simply:

```bash
cd C:\Users\Tay\Documents\GitHub\medevalTests
poetry install
poetry run pytest
```

The `pyproject.toml` will be updated to depend on published packages.

## Current Workflow (Local Development)

**For now, use Option 1:**

```powershell
cd C:\Users\Tay\Documents\GitHub\medevalTests

# One-time setup
poetry install
poetry run pip install -e ..\medeval
# Optional: poetry run pip install -e ..\medevalHelpers

# Run tests anytime
poetry run pytest -v

# Run examples
poetry run python examples/custom_evaluator_example.py
```

## File Structure

```
C:\Users\Tay\Documents\GitHub\
├── medeval/              # Framework repo
│   └── .venv/            # Framework's virtual environment
├── medevalHelpers/       # Helpers repo
├── medevalTests/         # This repo
    └── .venv/            # This repo's virtual environment (will have editable installs)
```

## Notes

- **Development mode**: Until published to PyPI, use editable installs (`pip install -e`)
- **Independent testing**: Each repo has its own tests and venv
- **Shared code**: Framework and helpers are imported from local editable installs
