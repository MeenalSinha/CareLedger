"""
Patient Memory Agent
Manages and maintains long-term patient medical memory
- Temporal decay of old memories
- Reinforcement of frequently accessed memories
- Memory consolidation
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from utils.vector_store import qdrant_manager

class PatientMemoryAgent:
    """
    Agent responsible for managing patient memory over time
    - Applies temporal decay to old records
    - Reinforces frequently accessed memories
    - Maintains memory quality
    """
    
    def __init__(self):
        self.name = "Patient Memory Agent"
    
    def get_patient_memory_summary(self, patient_id: str) -> Dict[str, Any]:
        """Get a summary of patient's medical memory"""
        try:
            # Get all timeline records
            timeline = qdrant_manager.get_patient_timeline(patient_id)
            
            if not timeline:
                return {
                    "patient_id": patient_id,
                    "total_records": 0,
                    "message": "No medical history found"
                }
            
            # Analyze records
            record_types = {}
            date_range = {
                "earliest": None,
                "latest": None
            }
            
            for record in timeline:
                payload = record["payload"]
                
                # Count by type
                record_type = payload.get("record_type", "unknown")
                record_types[record_type] = record_types.get(record_type, 0) + 1
                
                # Track date range
                record_date = datetime.fromisoformat(payload["date"])
                if date_range["earliest"] is None or record_date < date_range["earliest"]:
                    date_range["earliest"] = record_date
                if date_range["latest"] is None or record_date > date_range["latest"]:
                    date_range["latest"] = record_date
            
            return {
                "patient_id": patient_id,
                "total_records": len(timeline),
                "record_types": record_types,
                "date_range": {
                    "earliest": date_range["earliest"].isoformat() if date_range["earliest"] else None,
                    "latest": date_range["latest"].isoformat() if date_range["latest"] else None,
                    "span_days": (date_range["latest"] - date_range["earliest"]).days if date_range["earliest"] and date_range["latest"] else 0
                },
                "memory_health": self._assess_memory_health(timeline)
            }
            
        except Exception as e:
            return {
                "patient_id": patient_id,
                "error": str(e)
            }
    
    def _assess_memory_health(self, timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess the health and quality of patient memory"""
        if not timeline:
            return {"status": "empty", "score": 0}
        
        # Calculate various health metrics
        total_records = len(timeline)
        
        # Recency score (more recent records = better)
        now = datetime.now()
        recent_count = sum(
            1 for record in timeline
            if (now - datetime.fromisoformat(record["payload"]["date"])).days <= 90
        )
        recency_score = min(1.0, recent_count / max(1, total_records * 0.3))
        
        # Diversity score (different types of records = better)
        record_types = set(record["payload"].get("record_type") for record in timeline)
        diversity_score = min(1.0, len(record_types) / 5.0)  # 5 different types is ideal
        
        # Continuity score (regular updates = better)
        if len(timeline) > 1:
            dates = sorted([datetime.fromisoformat(r["payload"]["date"]) for r in timeline])
            avg_gap = sum(
                (dates[i+1] - dates[i]).days for i in range(len(dates)-1)
            ) / (len(dates) - 1)
            continuity_score = max(0, 1.0 - (avg_gap / 180))  # Ideal: updates every 6 months
        else:
            continuity_score = 0.5
        
        # Overall health score
        health_score = (recency_score * 0.4 + diversity_score * 0.3 + continuity_score * 0.3)
        
        return {
            "status": "excellent" if health_score > 0.8 else "good" if health_score > 0.6 else "fair" if health_score > 0.4 else "needs_improvement",
            "score": round(health_score, 2),
            "recency_score": round(recency_score, 2),
            "diversity_score": round(diversity_score, 2),
            "continuity_score": round(continuity_score, 2),
            "recommendations": self._get_memory_recommendations(recency_score, diversity_score, continuity_score)
        }
    
    def _get_memory_recommendations(self, recency: float, diversity: float, continuity: float) -> List[str]:
        """Generate recommendations for improving memory quality"""
        recommendations = []
        
        if recency < 0.5:
            recommendations.append("Consider uploading recent medical records to improve memory accuracy")
        
        if diversity < 0.4:
            recommendations.append("Adding different types of records (symptoms, scans, reports) would provide better context")
        
        if continuity < 0.4:
            recommendations.append("Regular updates to your medical history help identify patterns over time")
        
        return recommendations
    
    def apply_memory_maintenance(self, patient_id: str) -> Dict[str, Any]:
        """Apply memory maintenance operations"""
        try:
            # Apply temporal decay
            qdrant_manager.apply_temporal_decay(patient_id)
            
            return {
                "success": True,
                "message": "Memory maintenance completed",
                "patient_id": patient_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def consolidate_memories(self, patient_id: str, time_window_days: int = 30) -> Dict[str, Any]:
        """
        Consolidate similar memories from a time window
        This helps identify patterns and reduce noise
        """
        try:
            # Get recent records
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_window_days)
            
            records = qdrant_manager.get_patient_timeline(
                patient_id=patient_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Group by record type
            grouped = {}
            for record in records:
                record_type = record["payload"].get("record_type", "unknown")
                if record_type not in grouped:
                    grouped[record_type] = []
                grouped[record_type].append(record)
            
            # Find patterns
            patterns = []
            for record_type, type_records in grouped.items():
                if len(type_records) >= 3:  # Pattern threshold
                    patterns.append({
                        "type": record_type,
                        "count": len(type_records),
                        "pattern": f"Recurring {record_type} records ({len(type_records)} occurrences in {time_window_days} days)"
                    })
            
            return {
                "success": True,
                "time_window_days": time_window_days,
                "total_records": len(records),
                "patterns_found": len(patterns),
                "patterns": patterns
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
memory_agent = PatientMemoryAgent()
