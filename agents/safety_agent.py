"""
Safety & Ethics Agent
Ensures all outputs are safe, explainable, and non-diagnostic
Critical for healthcare applications
"""
from typing import Dict, Any, List, Optional
import re

class SafetyEthicsAgent:
    """
    Agent responsible for ensuring ethical and safe operation
    - Validates outputs are non-diagnostic
    - Ensures explainability
    - Adds appropriate disclaimers
    - Flags potential safety issues
    """
    
    def __init__(self):
        self.name = "Safety & Ethics Agent"
        
        # Keywords that might indicate diagnosis (to flag/warn)
        self.diagnostic_keywords = [
            "you have", "you are diagnosed", "this is definitely",
            "you suffer from", "you are experiencing", "treatment for",
            "take this medication", "prescribe", "medical advice"
        ]
        
        # Standard disclaimer
        self.standard_disclaimer = (
            "⚕️ IMPORTANT: This is a decision support tool, not medical diagnosis. "
            "All information should be discussed with your healthcare provider. "
            "In case of emergency, contact emergency services immediately."
        )
    
    def validate_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate output for safety and ethical compliance
        Returns validated output with added safety measures
        """
        validated = output.copy()
        
        # Add disclaimer
        validated["safety_disclaimer"] = self.standard_disclaimer
        
        # Check for diagnostic language
        safety_flags = self._check_for_diagnostic_language(validated)
        
        if safety_flags:
            validated["safety_flags"] = safety_flags
            validated["flagged"] = True
        else:
            validated["flagged"] = False
        
        # Ensure explainability
        validated = self._ensure_explainability(validated)
        
        # Add privacy notice
        validated["privacy_notice"] = self._get_privacy_notice()
        
        return validated
    
    def _check_for_diagnostic_language(self, output: Dict[str, Any]) -> List[str]:
        """Check for potentially diagnostic language"""
        flags = []
        
        # Check various fields for diagnostic keywords
        fields_to_check = []
        
        if "explanation" in output:
            fields_to_check.append(("explanation", output["explanation"]))
        
        if "recommendations" in output:
            for rec in output.get("recommendations", []):
                if isinstance(rec, str):
                    fields_to_check.append(("recommendation", rec))
        
        if "forgotten_insights" in output:
            for insight in output.get("forgotten_insights", []):
                if isinstance(insight, str):
                    fields_to_check.append(("insight", insight))
        
        # Check each field
        for field_name, text in fields_to_check:
            if not isinstance(text, str):
                continue
                
            text_lower = text.lower()
            
            for keyword in self.diagnostic_keywords:
                if keyword in text_lower:
                    flags.append({
                        "field": field_name,
                        "issue": f"Potentially diagnostic language detected: '{keyword}'",
                        "severity": "warning",
                        "recommendation": "Rephrase to focus on information and questions for healthcare provider"
                    })
        
        return flags
    
    def _ensure_explainability(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure output includes explainable reasoning"""
        # Add source tracking if similar cases are present
        if "similar_cases" in output and output["similar_cases"]:
            if "explanation_sources" not in output:
                sources = []
                for case in output["similar_cases"][:5]:
                    if isinstance(case, dict):
                        sources.append({
                            "record_id": case.get("record_id", "unknown"),
                            "date": case.get("date", "unknown"),
                            "similarity": case.get("similarity_score", 0),
                            "record_type": case.get("record_type", "unknown")
                        })
                output["explanation_sources"] = sources
                output["explainability_note"] = (
                    f"This response is based on {len(sources)} similar records "
                    "from your medical history. Each source is traceable."
                )
        
        return output
    
    def _get_privacy_notice(self) -> str:
        """Get privacy notice"""
        return (
            "Your medical data is stored securely and isolated to your patient ID. "
            "This system can be deployed locally for complete privacy control."
        )
    
    def sanitize_user_input(self, user_input: str) -> Dict[str, Any]:
        """Sanitize and validate user input"""
        # Remove potential injection attempts
        sanitized = user_input.strip()
        
        # Check for suspiciously long input
        if len(sanitized) > 5000:
            return {
                "valid": False,
                "error": "Input too long. Please limit to 5000 characters.",
                "sanitized": None
            }
        
        # Check for empty input
        if not sanitized:
            return {
                "valid": False,
                "error": "Input cannot be empty",
                "sanitized": None
            }
        
        # Basic XSS prevention (for web interface)
        dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onload=']
        for pattern in dangerous_patterns:
            if pattern.lower() in sanitized.lower():
                return {
                    "valid": False,
                    "error": "Invalid characters detected in input",
                    "sanitized": None
                }
        
        return {
            "valid": True,
            "sanitized": sanitized,
            "length": len(sanitized)
        }
    
    def validate_patient_id(self, patient_id: str) -> Dict[str, Any]:
        """Validate patient ID format"""
        # Patient ID should be alphanumeric with hyphens/underscores
        pattern = r'^[a-zA-Z0-9_-]+$'
        
        if not patient_id:
            return {
                "valid": False,
                "error": "Patient ID is required"
            }
        
        if len(patient_id) > 100:
            return {
                "valid": False,
                "error": "Patient ID too long"
            }
        
        if not re.match(pattern, patient_id):
            return {
                "valid": False,
                "error": "Patient ID contains invalid characters"
            }
        
        return {
            "valid": True,
            "patient_id": patient_id
        }
    
    def check_emergency_indicators(self, text: str) -> Dict[str, Any]:
        """Check if text indicates a medical emergency"""
        emergency_keywords = [
            "chest pain", "can't breathe", "suicide", "severe bleeding",
            "unconscious", "stroke", "heart attack", "overdose",
            "severe pain", "can't move", "seizure"
        ]
        
        text_lower = text.lower()
        detected = []
        
        for keyword in emergency_keywords:
            if keyword in text_lower:
                detected.append(keyword)
        
        if detected:
            return {
                "emergency_detected": True,
                "keywords": detected,
                "message": (
                    "🚨 EMERGENCY ALERT: Your message indicates a potential emergency. "
                    "Please contact emergency services (911 in US) immediately or go to "
                    "the nearest emergency room. Do not rely on this system for emergency care."
                )
            }
        
        return {
            "emergency_detected": False
        }
    
    def generate_consent_notice(self) -> str:
        """Generate informed consent notice"""
        return """
INFORMED CONSENT & DISCLAIMER

By using CareLedger, you acknowledge that:

1. This system provides DECISION SUPPORT ONLY, not medical diagnosis or treatment
2. All information should be reviewed with qualified healthcare providers
3. This system does not replace professional medical advice
4. In emergencies, contact emergency services immediately
5. Your medical data is stored securely but you should maintain original records
6. The AI may make errors - always verify important information with your doctor

This system is designed to help you and your healthcare providers make better-informed 
decisions by maintaining a comprehensive medical history, but it is not a substitute 
for professional medical judgment.
"""
    
    def get_data_usage_policy(self) -> str:
        """Get data usage policy"""
        return """
DATA USAGE POLICY

- Your medical records are isolated to your patient ID
- No data is shared with third parties
- Embeddings are derived from your records but cannot reconstruct original data
- You can request deletion of all your data at any time
- System can be deployed locally for complete privacy control
- AI processing uses your data only for your own medical memory
"""

# Global instance
safety_agent = SafetyEthicsAgent()
