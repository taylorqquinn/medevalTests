# MedEval Tests

**Example datasets and test cases for medeval-framework**

This repository contains example clinical test cases, baseline predictions, and integration tests. It serves as a **template for teams to fork and customize** with their own proprietary test data.

## 🎯 Purpose

This repo is designed to be **forked by your team** so you can:

- ✅ Add your own clinical test cases
- ✅ Store proprietary patient scenarios (keep repo private!)
- ✅ Define team-specific baseline expectations
- ✅ Create custom evaluators for your domain
- ✅ Run integration tests with your data

## 🚀 Quick Start

### Option 1: Fork This Repo (Recommended)

```bash
# 1. Fork this repo on GitHub to your organization
# 2. Clone your fork
git clone git@github.com:YOUR_ORG/medevalTests.git
cd medevalTests

# 3. Customize with your data
cp datasets/clinical_cases.jsonl datasets/my_team_cases.jsonl
# Edit my_team_cases.jsonl with your test cases

# 4. Run evaluation
medeval run --dataset datasets/my_team_cases.jsonl
```

### Option 2: Use as Template

```bash
# 1. Create new repo from this template
# 2. Customize structure as needed
# 3. Add your team's test data
```

## 📦 What's Included

### Datasets (`datasets/`)

Example clinical test cases in JSONL format:

```jsonl
{
  "id": "case_001",
  "symptoms": ["chest pain", "shortness of breath"],
  "medications": ["aspirin", "nitroglycerin"],
  "required_facts": ["cardiac", "emergency"],
  "forbidden_facts": ["diabetes", "pregnancy"],
  "gold_summary": "Patient presents with acute coronary syndrome..."
}
```

**Files:**
- `clinical_cases.jsonl` - 8 diverse example cases (chest pain, pneumonia, migraine, etc.)

### Baselines (`baselines/`)

Expected outputs from known models for comparison:

```jsonl
{
  "case_id": "case_001",
  "model": "gpt-4",
  "medications": ["aspirin", "metoprolol"],
  "summary": "Suspected myocardial infarction...",
  "confidence": 0.92
}
```

**Files:**
- `gpt4_baseline.jsonl` - GPT-4 predictions on example cases

### Examples (`examples/`)

Examples of custom evaluators and workflows:

- `custom_evaluator_example.py` - How to create custom evaluator plugins
- `integration_test_example.py` - How to write integration tests

### Integration Tests (`tests/integration/`)

End-to-end tests that verify the full evaluation pipeline works correctly.

## 📁 Directory Structure

```
medevalTests/
├── datasets/
│   └── clinical_cases.jsonl      # Example test cases (customize!)
├── baselines/
│   └── gpt4_baseline.jsonl       # Example baseline predictions
├── examples/
│   ├── custom_evaluator_example.py
│   └── integration_test_example.py
├── tests/
│   └── integration/
│       └── test_end_to_end.py
├── README.md                     # This file
└── .gitignore
```

## 🔧 Customization Guide

### Adding Your Test Cases

1. **Create your dataset file:**

```bash
# Start from the example
cp datasets/clinical_cases.jsonl datasets/cardiology_team_cases.jsonl
```

2. **Edit with your cases:**

```jsonl
{
  "id": "cardio_001",
  "symptoms": ["irregular heartbeat", "fatigue"],
  "medications": ["warfarin", "metoprolol"],
  "required_facts": ["atrial fibrillation", "anticoagulation"],
  "forbidden_facts": ["pregnancy", "bleeding"],
  "gold_summary": "Patient with newly diagnosed AFib..."
}
```

3. **Run evaluation:**

```bash
medeval run --dataset datasets/cardiology_team_cases.jsonl
```

### Creating Custom Evaluators

See `examples/custom_evaluator_example.py` for a complete example:

```python
from medeval.evaluators.base import Evaluator

class CardiacRiskEvaluator(Evaluator):
    """Custom evaluator for cardiac risk assessment."""
    
    def evaluate(self, case, prediction):
        risk_score = self._calculate_risk(case, prediction)
        return {
            "cardiac_risk_score": risk_score,
            "high_risk": risk_score > 0.7
        }
    
    def _calculate_risk(self, case, prediction):
        # Your custom logic
        return 0.85
```

**Register as plugin** in your `pyproject.toml`:

```toml
[tool.poetry.plugins."medeval.evaluators"]
cardiac_risk = "my_evaluators:CardiacRiskEvaluator"
```

### Adding Baselines

1. **Generate predictions** with your model
2. **Save in JSONL format:**

```python
import json

baseline = {
    "case_id": "case_001",
    "model": "my-model-v2",
    "medications": ["aspirin", "metoprolol"],
    "summary": "...",
    "confidence": 0.92
}

with open("baselines/my_model_baseline.jsonl", "a") as f:
    f.write(json.dumps(baseline) + "\n")
```

3. **Compare against baseline:**

```bash
medeval run \
    --dataset datasets/my_cases.jsonl \
    --baseline baselines/my_model_baseline.jsonl
```

## 🧪 Running Tests

```bash
# From medevalTests directory
cd C:\Users\Tay\Documents\GitHub\medevalTests

# Install dependencies with Poetry
poetry install

# Run integration tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=. --cov-report=html

# Run specific test
poetry run pytest tests/integration/test_end_to_end_example.py -v
```

**Note:** This repo has its own `pyproject.toml` so you can run tests independently!

## 🔒 Keeping Data Private

**Important**: This repo likely contains proprietary test data!

1. **Make your fork private:**
   - On GitHub: Settings → Change visibility → Make private

2. **Don't commit sensitive data:**
   - Patient identifiers (use synthetic IDs only)
   - Real PHI/PII
   - API keys or secrets

3. **Use `.gitignore`:**
   ```gitignore
   # Add to .gitignore
   datasets/*_real_patients.jsonl
   datasets/*_production.jsonl
   *_secrets.yaml
   ```

## 📊 Best Practices

### Test Case Design

✅ **DO:**
- Use diverse clinical scenarios (different specialties, age groups, severity)
- Include edge cases (rare conditions, multiple comorbidities)
- Define clear gold standards (required_facts, forbidden_facts)
- Use synthetic/de-identified data only

❌ **DON'T:**
- Use real patient data (HIPAA/GDPR violations!)
- Duplicate cases (wastes compute)
- Use vague gold standards
- Forget to version your datasets (git tag releases!)

### Baseline Management

- **Version your baselines**: Tag git commits when you update baselines
- **Document model configs**: Note hyperparameters used for baseline generation
- **Track baseline drift**: Monitor if your model improves/degrades over time
- **Multiple baselines**: Compare against multiple model versions

### Team Workflow

1. **Each team maintains their fork** of this repo
2. **Share framework/helpers** repos (common tooling)
3. **Keep datasets private** (proprietary test data)
4. **Upstream improvements**: Contribute generic evaluators back to framework

## 🤝 Contributing

Found a bug in the example code? Have a suggestion for the template?

- **For template issues**: Open issue in [this repo](https://github.com/taylorqquinn/medevalTests/issues)
- **For framework issues**: Open issue in [medeval-framework](https://github.com/taylorqquinn/medeval/issues)
- **For helper issues**: Open issue in [medeval-helpers](https://github.com/taylorqquinn/medevalHelpers/issues)

## 🔗 Related Projects

- **[medeval-framework](https://github.com/taylorqquinn/medeval)** - Core evaluation engine
- **[medeval-helpers](https://github.com/taylorqquinn/medevalHelpers)** - CLI tools and utilities

## 📄 License

MIT License - see LICENSE file for details.

---

**🚀 Ready to customize?**

1. Fork this repo to your organization
2. Replace example data with your test cases
3. Make the repo private
4. Start evaluating!

---

**Part of the MedEval clinical AI evaluation ecosystem**
