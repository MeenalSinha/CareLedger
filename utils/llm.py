"""
Gemini LLM Integration
Handles all interactions with Google's Gemini API
"""
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from config import settings
import json

class GeminiLLM:
    """Wrapper for Gemini LLM operations"""
    
    def __init__(self):
        self.model = None
        self.vision_model = None
        self.initialized = False
        
    def initialize(self):
        """Initialize Gemini API"""
        if not self.initialized:
            if not settings.GEMINI_API_KEY:
                print("WARNING: GEMINI_API_KEY not set. Using mock responses.")
                self.initialized = True
                return
            
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
                self.vision_model = genai.GenerativeModel(settings.GEMINI_VISION_MODEL)
                self.initialized = True
                print("Gemini API initialized successfully")
            except Exception as e:
                print(f"Error initializing Gemini: {e}")
                self.initialized = True  # Continue with mock responses
    
    def generate_response(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate a response from Gemini"""
        self.initialize()
        
        if not settings.GEMINI_API_KEY or not self.model:
            return self._mock_response(prompt)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=1024,
                )
            )
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._mock_response(prompt)
    
    def explain_similar_cases(
        self,
        query: str,
        similar_cases: List[Dict[str, Any]]
    ) -> str:
        """Generate explanation for similar cases"""
        prompt = f"""You are a medical information assistant for CareLedger, a patient health memory system.

IMPORTANT DISCLAIMER: You provide decision support, NOT medical diagnosis. Always remind users to consult healthcare professionals.

Patient Query: {query}

Similar Past Medical Records Found:
"""
        for i, case in enumerate(similar_cases[:5], 1):
            payload = case.get("payload", {})
            prompt += f"""
{i}. Date: {payload.get('date', 'Unknown')}
   Type: {payload.get('record_type', 'Unknown')}
   Content: {payload.get('content', '')[:200]}...
   Similarity: {case.get('score', 0):.2%}
"""
        
        prompt += """

Please provide:
1. A brief explanation of how these past records relate to the current query
2. Important patterns or connections you notice
3. What outcomes or treatments were recorded (if any)
4. 2-3 specific questions the patient should ask their doctor

Remember: 
- Be clear and patient-friendly
- Focus on information, not diagnosis
- Emphasize consulting healthcare providers
- Keep response concise and actionable
"""
        
        return self.generate_response(prompt, temperature=0.5)
    
    def generate_recommendations(
        self,
        query: str,
        timeline_context: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate patient recommendations based on history"""
        prompt = f"""You are a medical information assistant for CareLedger.

Patient Query: {query}

Recent Medical History:
"""
        for event in timeline_context[-10:]:  # Last 10 events
            payload = event.get("payload", {})
            prompt += f"- {payload.get('date', 'Unknown')}: {payload.get('record_type', 'Unknown')} - {payload.get('content', '')[:100]}\n"
        
        prompt += """

Generate 3-5 actionable recommendations for the patient. These should be:
- Information gathering actions (e.g., "Track your symptoms daily")
- Questions to ask their doctor
- Reminders for follow-ups
- Self-monitoring suggestions

Format as a JSON array of strings. Example:
["Track your symptoms daily in a journal", "Ask your doctor about X", "Schedule a follow-up in 2 weeks"]

IMPORTANT: Do NOT provide medical advice or diagnosis. Focus on information and communication.
"""
        
        response = self.generate_response(prompt, temperature=0.6)
        
        try:
            # Try to parse as JSON
            recommendations = json.loads(response)
            return recommendations[:5]  # Max 5 recommendations
        except:
            # Fallback: split by newlines
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            return [line.lstrip('- ').lstrip('• ').lstrip('* ') for line in lines[:5]]
    
    def identify_forgotten_insights(
        self,
        query: str,
        old_records: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify important information that might have been forgotten"""
        if not old_records:
            return []
        
        prompt = f"""You are analyzing medical history for CareLedger, a patient health memory system.

Current Query: {query}

OLD Medical Records (>6 months ago) that might be relevant:
"""
        for record in old_records[:5]:
            payload = record.get("payload", {})
            prompt += f"""
- {payload.get('date', 'Unknown')}: {payload.get('content', '')[:150]}
"""
        
        prompt += """

Identify 1-3 "forgotten insights" - important information from the past that:
1. Relates to the current query
2. Was not followed up on
3. Might be important context for current medical decisions

Format as a JSON array of strings. Each insight should be patient-friendly and actionable.

If no significant forgotten insights exist, return an empty array: []
"""
        
        response = self.generate_response(prompt, temperature=0.5)
        
        try:
            insights = json.loads(response)
            return insights[:3]
        except:
            return []
    
    def _mock_response(self, prompt: str) -> str:
        """Generate mock response when API is not available"""
        if "explain" in prompt.lower() or "similar" in prompt.lower():
            return """Based on your medical history, I found several similar situations:

1. The symptoms you're experiencing now are similar to what you reported 6 months ago
2. Previous treatment with [medication] showed positive results
3. Important pattern: These symptoms tend to appear in seasonal clusters

Questions to ask your doctor:
1. Should we consider a similar treatment approach as used previously?
2. Are there any new factors that might be contributing to these symptoms?
3. What preventive measures can I take based on this pattern?

**IMPORTANT**: This is decision support only. Please consult your healthcare provider for proper medical advice."""
        
        elif "recommendation" in prompt.lower():
            return '["Keep a daily symptom journal", "Schedule a follow-up appointment within 2 weeks", "Ask your doctor about the pattern of recurring symptoms", "Monitor any changes in symptom intensity"]'
        
        elif "forgotten" in prompt.lower():
            return '["A similar symptom was reported 2 years ago but was not followed up", "Previous allergy test results might be relevant to current symptoms"]'
        
        else:
            return "I'm here to help you understand your medical history better. Please consult your healthcare provider for medical advice."

# Global instance
gemini_llm = GeminiLLM()
