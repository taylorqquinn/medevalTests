"""Demo script showing logging system in action.

Run with: poetry run python demo_logging.py

This will create logs in .logs/medeval_TIMESTAMP/
"""

from pathlib import Path
import yaml

# Import helpers
from medeval_helpers import setup_logging, get_log_dir, get_artifacts_dir, SetupTeardownManager

# Import framework
from medeval.models import ClinicalCase, Prediction
from medeval.evaluators import MedicationF1Evaluator
from medeval.evaluation.runner import EvaluationRunner

import logging

def main():
    print("=" * 60)
    print("MedEval Logging Demo")
    print("=" * 60)
    
    # Load config
    config_path = Path("medeval_config.yaml")
    if not config_path.exists():
        config_path = Path("test_config.yaml")
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Set up logging
    print("\n1. Setting up logging...")
    run_id = setup_logging(str(config_path))
    log_dir = get_log_dir()
    artifacts_dir = get_artifacts_dir()
    
    print(f"   [OK] Run ID: {run_id}")
    print(f"   [OK] Log Dir: {log_dir}")
    print(f"   [OK] Artifacts Dir: {artifacts_dir}")
    
    # Set up environment
    print("\n2. Running setup phase...")
    manager = SetupTeardownManager(config)
    manager.setup(log_dir, artifacts_dir)
    
    # Get logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Demo script started")
    
    # Create sample test data
    print("\n3. Creating sample test data...")
    case = ClinicalCase(
        id="demo-001",
        text="Patient on aspirin and atorvastatin.",
        symptoms=["chest pain"],
        medications=["aspirin", "atorvastatin"],
        required_facts=["aspirin", "atorvastatin"],
        forbidden_facts=[],
        gold_summary={
            "medications": ["aspirin", "atorvastatin"],
            "symptoms": ["chest pain"],
        }
    )
    
    prediction = Prediction(
        case_id="demo-001",
        summary_text="Patient taking aspirin and atorvastatin for cardiac health.",
        medications=["aspirin", "atorvastatin"]
    )
    
    logger.info(f"Created test case: {case.id}")
    logger.info(f"Created prediction for: {prediction.case_id}")
    
    # Run evaluation
    print("\n4. Running evaluation...")
    evaluator = MedicationF1Evaluator()
    runner = EvaluationRunner([evaluator])
    
    results = runner.run([case], [prediction])
    
    logger.info(f"Evaluation complete. Cases evaluated: {len(results.case_results)}")
    logger.info(f"Aggregated metrics: {results.aggregated_metrics}")
    
    print(f"   [OK] Evaluated {len(results.case_results)} case(s)")
    print(f"   [OK] Metrics: {results.aggregated_metrics}")
    
    # Save results to artifacts
    print("\n5. Saving results to artifacts...")
    import json
    results_file = artifacts_dir / "demo_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "case_id": case.id,
            "metrics": results.aggregated_metrics,
            "case_results": [
                {
                    "case_id": cr.case_id,
                    "metrics": cr.metrics
                }
                for cr in results.case_results
            ]
        }, f, indent=2)
    
    logger.info(f"Saved results to: {results_file}")
    print(f"   [OK] Saved to: {results_file}")
    
    # Teardown
    print("\n6. Running teardown phase...")
    manager.teardown(log_dir, artifacts_dir)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] DEMO COMPLETE!")
    print("=" * 60)
    print(f"\nCheck logs at: {log_dir}")
    print(f"Check artifacts at: {artifacts_dir}")
    print()

if __name__ == "__main__":
    main()
