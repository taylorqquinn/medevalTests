"""Example integration test for MedEval framework.

This test demonstrates how to write end-to-end integration tests that verify
the complete evaluation pipeline works correctly with your datasets.

Run with:
    pytest tests/integration/test_end_to_end_example.py
"""

import pytest
import json
from pathlib import Path

# These imports require medeval-framework and medeval-helpers to be installed
try:
    from medeval.models import ClinicalCase, Prediction
    from medeval.evaluation.runner import EvaluationRunner
    from medeval.evaluators import (
        MedicationF1Evaluator,
        RequiredFactsEvaluator,
        ForbiddenFactsEvaluator,
    )
    MEDEVAL_AVAILABLE = True
except ImportError:
    MEDEVAL_AVAILABLE = False


@pytest.mark.skipif(not MEDEVAL_AVAILABLE, reason="medeval not installed")
class TestEndToEndEvaluation:
    """Integration tests for complete evaluation pipeline."""
    
    @pytest.fixture
    def sample_case(self):
        """Create a sample clinical case for testing."""
        return ClinicalCase(
            id="test_001",
            symptoms=["chest pain", "shortness of breath"],
            medications=["aspirin", "metoprolol"],
            required_facts=["cardiac", "emergency"],
            forbidden_facts=["diabetes"],
            gold_summary="Patient with acute coronary syndrome..."
        )
    
    @pytest.fixture
    def sample_prediction(self):
        """Create a sample prediction for testing."""
        return Prediction(
            case_id="test_001",
            medications=["aspirin", "nitroglycerin"],
            summary="Suspected heart attack, started aspirin and nitro..."
        )
    
    @pytest.fixture
    def evaluators(self):
        """Create evaluators for testing."""
        return [
            MedicationF1Evaluator(),
            RequiredFactsEvaluator(),
            ForbiddenFactsEvaluator(),
        ]
    
    def test_single_case_evaluation(self, sample_case, sample_prediction, evaluators):
        """Test evaluation of a single case."""
        runner = EvaluationRunner(evaluators=evaluators)
        
        # Run evaluation
        result = runner.evaluate_case(sample_case, sample_prediction)
        
        # Verify result structure
        assert result is not None
        assert hasattr(result, 'case_id')
        assert hasattr(result, 'metrics')
        assert result.case_id == "test_001"
        
        # Verify metrics exist
        metrics = result.metrics
        assert 'med_f1' in metrics or 'med_precision' in metrics
        assert 'required_facts_recall' in metrics or 'required_facts' in metrics
    
    def test_medication_f1_evaluator(self, sample_case, sample_prediction):
        """Test MedicationF1Evaluator produces expected metrics."""
        evaluator = MedicationF1Evaluator()
        
        result = evaluator.evaluate(sample_case, sample_prediction)
        
        # Verify metric keys
        assert 'med_precision' in result
        assert 'med_recall' in result
        assert 'med_f1' in result
        
        # Verify metric ranges
        assert 0.0 <= result['med_precision'] <= 1.0
        assert 0.0 <= result['med_recall'] <= 1.0
        assert 0.0 <= result['med_f1'] <= 1.0
    
    def test_required_facts_evaluator(self, sample_case, sample_prediction):
        """Test RequiredFactsEvaluator checks for required facts."""
        evaluator = RequiredFactsEvaluator()
        
        result = evaluator.evaluate(sample_case, sample_prediction)
        
        # Verify result structure
        assert isinstance(result, dict)
        # Result might have different key names depending on evaluator implementation
        # This is a flexible check
        assert len(result) > 0
        
        # At least one metric should be present
        possible_keys = ['required_facts_recall', 'required_facts_score', 'recall']
        assert any(key in result for key in possible_keys)
    
    def test_forbidden_facts_evaluator(self, sample_case, sample_prediction):
        """Test ForbiddenFactsEvaluator checks for forbidden content."""
        evaluator = ForbiddenFactsEvaluator()
        
        result = evaluator.evaluate(sample_case, sample_prediction)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert len(result) > 0
    
    def test_multiple_cases_evaluation(self, evaluators):
        """Test evaluation of multiple cases."""
        # Create multiple cases
        cases = [
            ClinicalCase(
                id=f"test_{i:03d}",
                symptoms=["symptom1", "symptom2"],
                medications=["med1", "med2"],
                required_facts=["fact1"],
                forbidden_facts=["forbidden1"],
                gold_summary=f"Test case {i}"
            )
            for i in range(3)
        ]
        
        # Create corresponding predictions
        predictions = [
            Prediction(
                case_id=f"test_{i:03d}",
                medications=["med1", "med3"],
                summary=f"Prediction for case {i}"
            )
            for i in range(3)
        ]
        
        # Run evaluation
        runner = EvaluationRunner(evaluators=evaluators)
        results = runner.run(cases, predictions)
        
        # Verify results
        assert results is not None
        assert hasattr(results, 'case_results')
        assert len(results.case_results) == 3
        
        # Verify each result has metrics
        for result in results.case_results:
            assert hasattr(result, 'metrics')
            assert isinstance(result.metrics, dict)
            assert len(result.metrics) > 0


@pytest.mark.skipif(not MEDEVAL_AVAILABLE, reason="medeval not installed")
class TestDatasetLoading:
    """Tests for loading datasets from files."""
    
    def test_load_clinical_cases_jsonl(self, tmp_path):
        """Test loading clinical cases from JSONL file."""
        # Create temporary JSONL file
        test_data = [
            {
                "id": "case_001",
                "symptoms": ["chest pain"],
                "medications": ["aspirin"],
                "required_facts": ["cardiac"],
                "forbidden_facts": [],
                "gold_summary": "Test case 1"
            },
            {
                "id": "case_002",
                "symptoms": ["headache"],
                "medications": ["ibuprofen"],
                "required_facts": ["pain"],
                "forbidden_facts": [],
                "gold_summary": "Test case 2"
            }
        ]
        
        test_file = tmp_path / "test_cases.jsonl"
        with open(test_file, 'w') as f:
            for item in test_data:
                f.write(json.dumps(item) + '\n')
        
        # Load dataset
        from medeval.dataset import load_dataset
        cases = load_dataset(str(test_file))
        
        # Verify loading
        assert len(cases) == 2
        assert all(isinstance(case, ClinicalCase) for case in cases)
        assert cases[0].id == "case_001"
        assert cases[1].id == "case_002"


@pytest.mark.skipif(not MEDEVAL_AVAILABLE, reason="medeval not installed")
def test_evaluation_with_example_dataset():
    """Integration test using the example dataset from this repo.
    
    This test verifies that the example dataset in datasets/ can be loaded
    and evaluated successfully.
    """
    # Find the dataset
    repo_root = Path(__file__).parent.parent.parent
    dataset_path = repo_root / "datasets" / "clinical_cases.jsonl"
    
    if not dataset_path.exists():
        pytest.skip(f"Example dataset not found at {dataset_path}")
    
    # Load dataset
    from medeval.dataset import load_dataset
    cases = load_dataset(str(dataset_path))
    
    # Verify dataset loaded
    assert len(cases) > 0
    assert all(isinstance(case, ClinicalCase) for case in cases)
    
    # Create dummy predictions (just echo medications from cases)
    predictions = [
        Prediction(
            case_id=case.id,
            medications=case.medications,
            summary=case.gold_summary
        )
        for case in cases
    ]
    
    # Run evaluation
    evaluators = [MedicationF1Evaluator()]
    runner = EvaluationRunner(evaluators=evaluators)
    results = runner.run(cases, predictions)
    
    # Verify results
    assert results is not None
    assert len(results.case_results) == len(cases)
    
    # Since predictions match gold standard, F1 should be perfect
    for result in results.case_results:
        if 'med_f1' in result.metrics:
            assert result.metrics['med_f1'] == 1.0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
