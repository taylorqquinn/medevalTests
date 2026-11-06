"""Example custom evaluator for MedEval framework.

This example shows how to create a custom evaluator and register it as a plugin
so it can be discovered and used by the medeval framework.

To use this evaluator:

1. Create a package with your custom evaluators
2. Add this to your pyproject.toml:

    [tool.poetry.plugins."medeval.evaluators"]
    cardiac_risk = "my_evaluators.cardiac_risk:CardiacRiskEvaluator"

3. Install your package:

    pip install -e .

4. Use in evaluation:

    from medeval.evaluators.base import discover_evaluators
    
    evaluators = discover_evaluators()
    cardiac_eval = evaluators['cardiac_risk']()
"""

from medeval.evaluators.base import Evaluator
from medeval.models import ClinicalCase, Prediction
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class CardiacRiskEvaluator(Evaluator):
    """Custom evaluator that assesses cardiac risk based on symptoms and medications.
    
    This evaluator demonstrates how to:
    - Inherit from the base Evaluator class
    - Implement custom evaluation logic
    - Return multiple metrics
    - Use logging for debugging
    - Handle edge cases
    
    Attributes:
        high_risk_symptoms: List of symptoms indicating high cardiac risk
        protective_medications: Medications that reduce risk
        risk_threshold: Threshold for classifying as high risk
    """
    
    def __init__(self, risk_threshold: float = 0.7):
        """Initialize the cardiac risk evaluator.
        
        Args:
            risk_threshold: Threshold above which cases are classified as high risk
        """
        super().__init__(name="CardiacRiskEvaluator")
        self.risk_threshold = risk_threshold
        
        # Domain knowledge encoded as constants
        self.high_risk_symptoms = {
            "chest pain", "shortness of breath", "irregular heartbeat",
            "syncope", "palpitations", "diaphoresis"
        }
        
        self.protective_medications = {
            "aspirin", "metoprolol", "lisinopril", "atorvastatin",
            "warfarin", "clopidogrel"
        }
        
        logger.info(f"Initialized {self.name} with threshold={risk_threshold}")
    
    def evaluate(self, case: ClinicalCase, prediction: Prediction) -> Dict[str, Any]:
        """Evaluate cardiac risk based on case symptoms and predicted medications.
        
        The risk score is calculated as:
        1. Start with base risk from symptom analysis
        2. Adjust for protective medications in prediction
        3. Normalize to [0, 1] range
        
        Args:
            case: Clinical case with symptoms and expected medications
            prediction: Model prediction with suggested medications
            
        Returns:
            Dictionary with metrics:
            - cardiac_risk_score: Float in [0, 1] indicating risk level
            - high_risk: Boolean indicating if risk exceeds threshold
            - risk_factors_identified: Number of high-risk symptoms present
            - protective_meds_prescribed: Number of protective meds in prediction
        """
        logger.debug(f"Evaluating cardiac risk for case {case.id}")
        
        # Analyze symptoms
        symptoms = {s.lower().strip() for s in (case.symptoms or [])}
        risk_factors = symptoms & self.high_risk_symptoms
        num_risk_factors = len(risk_factors)
        
        logger.debug(f"Found {num_risk_factors} cardiac risk factors: {risk_factors}")
        
        # Analyze predicted medications
        predicted_meds = {m.lower().strip() for m in (prediction.medications or [])}
        protective_prescribed = predicted_meds & self.protective_medications
        num_protective = len(protective_prescribed)
        
        logger.debug(f"Found {num_protective} protective medications: {protective_prescribed}")
        
        # Calculate risk score
        # Base risk from symptoms (0.0 to 1.0)
        base_risk = min(num_risk_factors / 3.0, 1.0)  # 3+ symptoms = maximum risk
        
        # Risk reduction from protective medications
        risk_reduction = min(num_protective / 2.0, 0.5)  # Max 50% reduction
        
        # Final risk score
        risk_score = max(base_risk - risk_reduction, 0.0)
        
        high_risk = risk_score >= self.risk_threshold
        
        logger.info(
            f"Case {case.id}: base_risk={base_risk:.2f}, "
            f"reduction={risk_reduction:.2f}, final_risk={risk_score:.2f}, "
            f"high_risk={high_risk}"
        )
        
        return {
            "cardiac_risk_score": risk_score,
            "high_risk": high_risk,
            "risk_factors_identified": num_risk_factors,
            "protective_meds_prescribed": num_protective,
        }


class PediatricSafetyEvaluator(Evaluator):
    """Example evaluator for checking pediatric medication safety.
    
    Demonstrates checking for contraindicated medications in pediatric cases.
    """
    
    def __init__(self):
        super().__init__(name="PediatricSafetyEvaluator")
        
        # Medications contraindicated in pediatrics
        self.contraindicated_meds = {
            "aspirin",  # Reye's syndrome risk
            "codeine",  # Respiratory depression
            "ciprofloxacin",  # Cartilage damage
        }
    
    def evaluate(self, case: ClinicalCase, prediction: Prediction) -> Dict[str, Any]:
        """Check if prediction includes medications unsafe for pediatric use.
        
        Args:
            case: Clinical case (should have pediatric flag or age)
            prediction: Model prediction with medications
            
        Returns:
            Dictionary with:
            - is_pediatric_safe: Boolean, True if no contraindications
            - contraindications_found: List of unsafe meds prescribed
            - num_contraindications: Count of unsafe meds
        """
        predicted_meds = {m.lower().strip() for m in (prediction.medications or [])}
        contraindications = predicted_meds & self.contraindicated_meds
        
        return {
            "is_pediatric_safe": len(contraindications) == 0,
            "contraindications_found": sorted(list(contraindications)),
            "num_contraindications": len(contraindications),
        }


# Example usage
if __name__ == "__main__":
    # Create example case
    case = ClinicalCase(
        id="example_001",
        text="Patient presents with chest pain, shortness of breath, and diaphoresis.",
        symptoms=["chest pain", "shortness of breath", "diaphoresis"],
        medications=["aspirin", "metoprolol"],  # Ground truth
        required_facts=["acute coronary syndrome"],
        forbidden_facts=[],
        gold_summary={"summary_text": "Patient with suspected ACS..."}
    )
    
    # Create example prediction
    prediction = Prediction(
        case_id="example_001",
        summary_text="Likely myocardial infarction, initiated MONA protocol...",
        medications=["aspirin", "nitroglycerin", "metoprolol"]
    )
    
    # Evaluate
    evaluator = CardiacRiskEvaluator(risk_threshold=0.7)
    result = evaluator.evaluate(case, prediction)
    
    print("Cardiac Risk Evaluation Results:")
    print(f"  Risk Score: {result['cardiac_risk_score']:.2f}")
    print(f"  High Risk: {result['high_risk']}")
    print(f"  Risk Factors: {result['risk_factors_identified']}")
    print(f"  Protective Meds: {result['protective_meds_prescribed']}")
