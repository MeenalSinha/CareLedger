"""
Recommendation Agent
Generates patient-friendly recommendations and questions for doctors
Focus on actionable, non-diagnostic suggestions
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from utils.llm import gemini_llm

class RecommendationAgent:
    """
    Agent responsible for generating actionable recommendations
    - Questions to ask doctors
    - Self-monitoring suggestions
    - Follow-up reminders
    - Information gathering actions
    """
    
    def __init__(self):
        self.name = "Recommendation Agent"
    
    def generate_recommendations(
        self,
        query: str,
        similar_cases: List[Dict[str, Any]],
        timeline_context: List[Dict[str, Any]],
        forgotten_insights: List[str]
    ) -> Dict[str, Any]:
        """Generate comprehensive recommendations"""
        try:
            recommendations = []
            
            # Generate doctor questions
            doctor_questions = self._generate_doctor_questions(
                query, similar_cases, forgotten_insights
            )
            recommendations.extend([
                {"type": "doctor_question", "text": q}
                for q in doctor_questions
            ])
            
            # Generate monitoring suggestions
            monitoring = self._generate_monitoring_suggestions(
                query, similar_cases
            )
            recommendations.extend([
                {"type": "self_monitoring", "text": m}
                for m in monitoring
            ])
            
            # Generate follow-up reminders
            reminders = self._generate_reminders(timeline_context)
            recommendations.extend([
                {"type": "reminder", "text": r}
                for r in reminders
            ])
            
            # Generate information gathering actions
            info_actions = self._generate_info_actions(query, similar_cases)
            recommendations.extend([
                {"type": "information", "text": a}
                for a in info_actions
            ])
            
            # Use LLM for additional context-aware recommendations
            llm_recommendations = gemini_llm.generate_recommendations(
                query, timeline_context
            )
            
            # Merge LLM recommendations
            for rec in llm_recommendations:
                if rec and rec not in [r["text"] for r in recommendations]:
                    recommendations.append({
                        "type": "general",
                        "text": rec
                    })
            
            return {
                "success": True,
                "total_recommendations": len(recommendations),
                "recommendations": recommendations[:10],  # Limit to 10
                "priority_recommendations": self._prioritize_recommendations(recommendations)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "recommendations": []
            }
    
    def _generate_doctor_questions(
        self,
        query: str,
        similar_cases: List[Dict[str, Any]],
        forgotten_insights: List[str]
    ) -> List[str]:
        """Generate specific questions to ask the doctor"""
        questions = []
        
        # Questions based on similar cases
        if similar_cases:
            recent_cases = [
                c for c in similar_cases
                if isinstance(c, dict) and 
                (datetime.now() - datetime.fromisoformat(c.get("date", datetime.now().isoformat()))).days < 180
            ]
            
            if recent_cases:
                questions.append(
                    "Should we review the pattern of symptoms I've experienced over the past 6 months?"
                )
                
                # Check if previous treatments are mentioned
                has_treatment_history = any(
                    c.get("record_type") in ["prescription", "treatment"]
                    for c in recent_cases
                )
                
                if has_treatment_history:
                    questions.append(
                        "Based on my previous treatments, what approach would you recommend this time?"
                    )
        
        # Questions based on forgotten insights
        if forgotten_insights:
            questions.append(
                "There are some older medical records that might be relevant - should we review them together?"
            )
        
        # General contextual questions
        if "pain" in query.lower():
            questions.append(
                "What tests or examinations would help determine the cause of this pain?"
            )
        
        if "symptom" in query.lower():
            questions.append(
                "What warning signs should I watch for that would require immediate attention?"
            )
        
        return questions[:3]  # Max 3 doctor questions
    
    def _generate_monitoring_suggestions(
        self,
        query: str,
        similar_cases: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate self-monitoring suggestions"""
        suggestions = []
        
        # Always suggest tracking
        suggestions.append(
            "Keep a daily symptom journal noting intensity, duration, and triggers"
        )
        
        # Check for patterns in similar cases
        if len(similar_cases) >= 3:
            suggestions.append(
                "Track any patterns - note if symptoms occur at specific times or in specific situations"
            )
        
        # Specific monitoring based on query
        query_lower = query.lower()
        
        if "pain" in query_lower:
            suggestions.append(
                "Rate your pain on a scale of 1-10 and note what activities make it better or worse"
            )
        
        if any(word in query_lower for word in ["headache", "migraine"]):
            suggestions.append(
                "Keep a headache diary tracking possible triggers (food, sleep, stress, weather)"
            )
        
        if any(word in query_lower for word in ["sleep", "insomnia", "tired"]):
            suggestions.append(
                "Track your sleep patterns including hours slept, wake times, and sleep quality"
            )
        
        return suggestions[:3]  # Max 3 monitoring suggestions
    
    def _generate_reminders(
        self,
        timeline_context: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate follow-up reminders"""
        reminders = []
        
        if not timeline_context:
            return reminders
        
        # Check for recent records
        latest_record = max(
            timeline_context,
            key=lambda x: x.get("date", ""),
            default=None
        )
        
        if latest_record:
            latest_date = datetime.fromisoformat(latest_record["date"])
            days_since = (datetime.now() - latest_date).days
            
            if days_since > 90:
                reminders.append(
                    "Consider scheduling a check-up - it's been over 3 months since your last recorded visit"
                )
        
        # Check for recurring patterns
        if len(timeline_context) >= 3:
            reminders.append(
                "Schedule a follow-up appointment to discuss the pattern of recurring symptoms"
            )
        
        # General reminder
        reminders.append(
            "Keep all current medications and supplements list updated for your next doctor visit"
        )
        
        return reminders[:2]  # Max 2 reminders
    
    def _generate_info_actions(
        self,
        query: str,
        similar_cases: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate information gathering actions"""
        actions = []
        
        # Suggest uploading relevant documents
        if similar_cases:
            actions.append(
                "If you have recent test results or reports, upload them to maintain a complete record"
            )
        
        # Suggest specific information to gather
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["allergy", "allergic", "reaction"]):
            actions.append(
                "Document all known allergies and any adverse reactions to medications or foods"
            )
        
        if any(word in query_lower for word in ["family", "genetic", "hereditary"]):
            actions.append(
                "Gather family medical history, especially for conditions that run in families"
            )
        
        if any(word in query_lower for word in ["medication", "medicine", "drug"]):
            actions.append(
                "Create a complete list of all medications, dosages, and when you started taking them"
            )
        
        return actions[:2]  # Max 2 info actions
    
    def _prioritize_recommendations(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prioritize recommendations by importance"""
        # Priority order: doctor_question > reminder > self_monitoring > information > general
        priority_order = {
            "doctor_question": 1,
            "reminder": 2,
            "self_monitoring": 3,
            "information": 4,
            "general": 5
        }
        
        sorted_recs = sorted(
            recommendations,
            key=lambda x: priority_order.get(x.get("type", "general"), 10)
        )
        
        return sorted_recs[:5]  # Top 5 priority recommendations
    
    def generate_timeline_insights(
        self,
        timeline: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate insights from patient timeline"""
        if not timeline:
            return {
                "insights": [],
                "message": "No timeline data available"
            }
        
        insights = []
        
        # Analyze frequency
        if len(timeline) >= 5:
            dates = [datetime.fromisoformat(t["date"]) for t in timeline]
            dates.sort()
            
            if len(dates) > 1:
                span = (dates[-1] - dates[0]).days
                avg_frequency = span / len(dates) if span > 0 else 0
                
                if avg_frequency < 30:
                    insights.append({
                        "type": "frequency",
                        "text": "You have frequent medical interactions (average every few weeks). Consider discussing ongoing management with your doctor."
                    })
                elif avg_frequency > 180:
                    insights.append({
                        "type": "frequency",
                        "text": "You have infrequent medical records. Consider regular check-ups for preventive care."
                    })
        
        # Analyze record types
        record_types = {}
        for record in timeline:
            r_type = record.get("record_type", "unknown")
            record_types[r_type] = record_types.get(r_type, 0) + 1
        
        if record_types.get("symptom", 0) > record_types.get("report", 0):
            insights.append({
                "type": "documentation",
                "text": "You track symptoms well. Consider uploading more medical reports for complete context."
            })
        
        return {
            "success": True,
            "insights": insights,
            "timeline_summary": {
                "total_records": len(timeline),
                "record_types": record_types,
                "date_range": {
                    "start": min([t["date"] for t in timeline]),
                    "end": max([t["date"] for t in timeline])
                }
            }
        }

# Global instance
recommendation_agent = RecommendationAgent()
