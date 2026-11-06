"""Example integration test WITH logging from medeval-helpers.

This shows how to use the logging system in your integration tests if you want
structured logging with artifacts and run directories.
"""

import pytest
from pathlib import Path


# Check if helpers available
try:
    from medeval_helpers import setup_logging, SetupTeardownManager, get_log_dir, get_artifacts_dir
    HELPERS_AVAILABLE = True
except ImportError:
    HELPERS_AVAILABLE = False


@pytest.fixture(scope="session")
def test_environment_with_logging():
    """Set up test environment with logging (if helpers installed)."""
    if not HELPERS_AVAILABLE:
        pytest.skip("medeval-helpers not installed")
    
    import yaml
    
    # Use medeval_config.yaml (full config from helpers)
    config_path = Path(__file__).parent.parent.parent / "medeval_config.yaml"
    if not config_path.exists():
        # Fall back to test_config.yaml
        config_path = Path(__file__).parent.parent.parent / "test_config.yaml"
    
    if not config_path.exists():
        pytest.skip(f"Config not found: {config_path}")
    
    # Load config
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Set up logging first
    run_id = setup_logging(str(config_path))
    log_dir = get_log_dir()
    artifacts_dir = get_artifacts_dir()
    
    # Then set up environment with the directories
    manager = SetupTeardownManager(config)
    manager.setup(log_dir, artifacts_dir)
    
    yield {
        "run_id": run_id,
        "log_dir": log_dir,
        "artifact_dir": artifacts_dir,
    }
    
    # Teardown with directories
    manager.teardown(log_dir, artifacts_dir)


@pytest.mark.skipif(not HELPERS_AVAILABLE, reason="medeval-helpers not installed")
def test_evaluation_with_logging(test_environment_with_logging):
    """Test that evaluation creates logs in the expected directory."""
    from medeval.models import ClinicalCase, Prediction
    from medeval.evaluators import MedicationF1Evaluator
    from medeval.evaluation.runner import EvaluationRunner
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info("Starting test with logging")
    
    # Create test case
    case = ClinicalCase(
        id="test_logged_001",
        text="Test case with logging",
        symptoms=["test"],
        medications=["aspirin"],
        required_facts=["test"],
        forbidden_facts=[],
        gold_summary={"summary_text": "Test summary"}
    )
    
    prediction = Prediction(
        case_id="test_logged_001",
        summary_text="Test prediction",
        medications=["aspirin"]
    )
    
    # Run evaluation
    runner = EvaluationRunner(evaluators=[MedicationF1Evaluator()])
    result = runner.evaluate_case(case, prediction)
    
    # Verify logging worked
    log_dir = Path(test_environment_with_logging["log_dir"])
    assert log_dir.exists(), f"Log directory should exist: {log_dir}"
    
    artifact_dir = Path(test_environment_with_logging["artifact_dir"])
    assert artifact_dir.exists(), f"Artifact directory should exist: {artifact_dir}"
    
    logger.info(f"Test completed. Logs in: {log_dir}")
    logger.info(f"Artifacts in: {artifact_dir}")
    
    # Verify results
    assert "med_f1" in result.metrics or "med_precision" in result.metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
