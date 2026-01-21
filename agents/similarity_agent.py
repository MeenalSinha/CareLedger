"""
Similarity Reasoning Agent
Finds past medical states similar to current query
Uses vector similarity and temporal reasoning
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from utils.vector_store import qdrant_manager
from utils.embeddings import embedding_manager
from models.schemas import SimilarCase

class SimilarityReasoningAgent:
    """
    Agent responsible for finding similar past medical situations
    - Semantic similarity search
    - Temporal context analysis
    - Pattern recognition
    """
    
    def __init__(self):
        self.name = "Similarity Reasoning Agent"
    
    def find_similar_cases(
        self,
        patient_id: str,
        query: str,
        limit: int = 10,
        include_old_records: bool = True,
        time_weight: float = 0.3,  # Weight for recency (0-1)
        modality_weight: bool = True  # Prefer text for symptom queries
    ) -> Dict[str, Any]:
        """
        Find similar past medical cases with INTELLIGENT WEIGHTING
        
        Args:
            time_weight: How much to favor recent records (0=ignore time, 1=only time)
            modality_weight: Whether to weight by modality appropriateness
        """
        try:
            # Generate query embedding
            query_embedding = embedding_manager.embed_text(query)
            
            # Search for similar records
            similar_records = qdrant_manager.search_similar(
                query_embedding=query_embedding,
                patient_id=patient_id,
                modality="text",
                limit=limit * 2,  # Get more candidates for re-ranking
                score_threshold=0.3
            )
            
            # === INTELLIGENT RE-RANKING ===
            now = datetime.now()
            re_ranked_records = []
            
            for record in similar_records:
                payload = record["payload"]
                base_similarity = record["score"]
                
                # TIME-WEIGHTED SIMILARITY
                # Recent records get a boost, but not too much
                record_date = datetime.fromisoformat(payload["date"])
                days_old = (now - record_date).days
                
                if time_weight > 0:
                    # Exponential decay: recent = 1.0, 1 year = 0.5, 2 years = 0.25
                    time_factor = 0.5 ** (days_old / 365)
                    time_boosted_similarity = (base_similarity * (1 - time_weight)) + (time_factor * time_weight)
                else:
                    time_boosted_similarity = base_similarity
                
                # MODALITY-WEIGHTED SIMILARITY
                # Text records are better for symptom/treatment queries
                modality = payload.get("modality", "text")
                if modality_weight:
                    if modality == "text" and any(word in query.lower() for word in ["symptom", "treatment", "medication", "pain"]):
                        time_boosted_similarity *= 1.1  # 10% boost
                    elif modality == "image" and any(word in query.lower() for word in ["scan", "x-ray", "image"]):
                        time_boosted_similarity *= 1.1
                
                # MEMORY WEIGHT (from reinforcement/decay)
                memory_weight = payload.get("memory_weight", 1.0)
                final_score = time_boosted_similarity * memory_weight
                
                record["final_score"] = final_score
                record["time_boosted_score"] = time_boosted_similarity
                record["days_old"] = days_old
                re_ranked_records.append(record)
            
            # Sort by final score
            re_ranked_records.sort(key=lambda x: x["final_score"], reverse=True)
            similar_records = re_ranked_records[:limit]
            
            print(f"[SIMILARITY] Re-ranked {len(similar_records)} records with time_weight={time_weight}")
            
            # Separate into recent and old cases
            recent_threshold = now - timedelta(days=180)  # 6 months
            old_threshold = now - timedelta(days=365)  # 1 year
            
            recent_cases = []
            old_cases = []
            
            for record in similar_records:
                payload = record["payload"]
                record_date = datetime.fromisoformat(payload["date"])
                
                case = SimilarCase(
                    record_id=payload["record_id"],
                    record_type=payload["record_type"],
                    content=payload["content"],
                    date=record_date,
                    similarity_score=record["final_score"],  # Use final weighted score
                    relevance_explanation=self._generate_relevance_explanation(
                        query, payload, record["final_score"], record.get("days_old", 0)
                    ),
                    metadata=payload.get("metadata", {})
                )
                
                if record_date >= recent_threshold:
                    recent_cases.append(case)
                elif record_date >= old_threshold:
                    old_cases.append(case)
            
            # Identify forgotten insights from old records
            forgotten_insights = []
            if include_old_records and old_cases:
                forgotten_insights = self._identify_forgotten_patterns(
                    query, old_cases, recent_cases
                )
            
            return {
                "success": True,
                "query": query,
                "total_found": len(similar_records),
                "recent_cases": [case.dict() for case in recent_cases],
                "old_cases": [case.dict() for case in old_cases],
                "forgotten_insights": forgotten_insights,
                "temporal_context": self._build_temporal_context(similar_records),
                "ranking_info": {
                    "time_weight_applied": time_weight,
                    "modality_weighted": modality_weight,
                    "memory_evolution_considered": True
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_relevance_explanation(
        self,
        query: str,
        payload: Dict[str, Any],
        similarity_score: float,
        days_old: int = 0
    ) -> str:
        """Generate human-readable explanation of relevance"""
        record_type = payload.get("record_type", "record")
        date = payload.get("date", "Unknown date")
        
        if similarity_score > 0.8:
            relevance = "Very similar"
        elif similarity_score > 0.6:
            relevance = "Moderately similar"
        else:
            relevance = "Potentially related"
        
        # Extract key terms from content (simple approach)
        content = payload.get("content", "")
        
        explanation = f"{relevance} {record_type} from {date[:10]}"
        
        # Add time context
        if days_old > 0:
            if days_old < 30:
                explanation += " (recent)"
            elif days_old < 180:
                explanation += f" ({days_old // 30} months ago)"
            else:
                explanation += f" ({days_old // 365} years ago)"
        
        # Add context if available
        metadata = payload.get("metadata", {})
        if metadata.get("symptoms"):
            explanation += f" - symptoms: {', '.join(metadata['symptoms'][:2])}"
        
        return explanation
    
    def _identify_forgotten_patterns(
        self,
        query: str,
        old_cases: List[SimilarCase],
        recent_cases: List[SimilarCase]
    ) -> List[str]:
        """
        Identify patterns in old records that might be FORGOTTEN
        This is the "WOW moment" feature
        """
        insights = []
        
        # === EXPLICIT FORGOTTEN INSIGHT DETECTION ===
        print(f"\n{'='*70}")
        print(f"💡 FORGOTTEN INSIGHT DETECTION")
        print(f"{'='*70}")
        print(f"Analyzing {len(old_cases)} old records (>6 months) vs {len(recent_cases)} recent records")
        print(f"{'='*70}\n")
        
        # Check for patterns that appeared before but not recently
        old_symptoms = set()
        recent_symptoms = set()
        
        for case in old_cases:
            if case.metadata.get("symptoms"):
                old_symptoms.update(case.metadata["symptoms"])
        
        for case in recent_cases:
            if case.metadata.get("symptoms"):
                recent_symptoms.update(case.metadata["symptoms"])
        
        # Find symptoms that appeared before but not recently
        forgotten_symptoms = old_symptoms - recent_symptoms
        
        if forgotten_symptoms:
            insight = (
                f"🔍 FORGOTTEN PATTERN: Similar symptoms ({', '.join(list(forgotten_symptoms)[:3])}) "
                f"were reported over a year ago but haven't been mentioned in recent visits. "
                f"This historical context may be important for your current situation."
            )
            insights.append(insight)
            print(f"✅ Found forgotten symptom pattern: {forgotten_symptoms}")
        
        # === CHECK FOR UNFOLLOWED RECOMMENDATIONS (Critical!) ===
        for case in old_cases:
            if case.similarity_score > 0.6:  # Only for relevant old records
                unfollowed = case.metadata.get("unfollowed_recommendation")
                if unfollowed:
                    age_months = (datetime.now() - case.date).days // 30
                    insight = (
                        f"⚠️ UNFOLLOWED RECOMMENDATION: {age_months} months ago, during a similar episode, "
                        f"your doctor recommended '{unfollowed}' but this was never followed up on. "
                        f"This may be worth discussing with your healthcare provider."
                    )
                    insights.append(insight)
                    print(f"✅ Found unfollowed recommendation from {age_months} months ago")
                    print(f"   → {unfollowed}")
        
        # Check for old records with high similarity but no recent follow-up
        highly_similar_old = [c for c in old_cases if c.similarity_score > 0.7]
        if highly_similar_old and len(recent_cases) < 2:
            oldest = highly_similar_old[0]
            months_ago = (datetime.now() - oldest.date).days // 30
            insight = (
                f"📅 HISTORICAL MATCH: A very similar situation ({oldest.record_type}) was documented "
                f"{months_ago} months ago ({oldest.date.strftime('%B %Y')}), but there's no recent follow-up "
                f"on record. The previous episode may provide valuable context."
            )
            insights.append(insight)
            print(f"✅ Found high-similarity historical match from {months_ago} months ago")
        
        # Check for recurring patterns (seasonal or cyclic)
        if len(old_cases) >= 3:
            dates = [c.date for c in old_cases]
            dates.sort()
            
            # Check if there's a seasonal pattern (same months)
            months = [d.month for d in dates]
            if len(set(months)) <= 3:  # Concentrated in few months
                month_names = [dates[0].strftime('%B'), dates[-1].strftime('%B')]
                insight = (
                    f"🔄 RECURRING PATTERN: This type of issue has appeared multiple times "
                    f"historically, often in similar months ({', '.join(month_names)}). "
                    f"This suggests a potential seasonal or cyclical pattern worth monitoring."
                )
                insights.append(insight)
                print(f"✅ Found recurring seasonal pattern: {set(months)}")
        
        if insights:
            print(f"\n{'='*70}")
            print(f"🎯 TOTAL FORGOTTEN INSIGHTS: {len(insights)}")
            print(f"{'='*70}\n")
        else:
            print(f"ℹ️ No significant forgotten insights detected\n")
        
        return insights[:3]  # Return max 3 insights
    
    def _build_temporal_context(
        self,
        similar_records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Build temporal context showing progression over time"""
        if not similar_records:
            return []
        
        # Sort by date
        sorted_records = sorted(
            similar_records,
            key=lambda x: datetime.fromisoformat(x["payload"]["date"])
        )
        
        context = []
        for i, record in enumerate(sorted_records):
            payload = record["payload"]
            date = datetime.fromisoformat(payload["date"])
            
            # Calculate time since previous similar case
            time_since_previous = None
            if i > 0:
                prev_date = datetime.fromisoformat(sorted_records[i-1]["payload"]["date"])
                days_diff = (date - prev_date).days
                time_since_previous = f"{days_diff} days"
            
            context.append({
                "date": date.isoformat(),
                "record_type": payload.get("record_type"),
                "similarity": record["score"],
                "time_since_previous": time_since_previous,
                "content_preview": payload.get("content", "")[:100]
            })
        
        return context
    
    def analyze_symptom_progression(
        self,
        patient_id: str,
        symptom: str,
        time_window_days: int = 365
    ) -> Dict[str, Any]:
        """Analyze how a specific symptom has progressed over time"""
        try:
            # Get timeline
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_window_days)
            
            timeline = qdrant_manager.get_patient_timeline(
                patient_id=patient_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Filter for records mentioning the symptom
            symptom_lower = symptom.lower()
            related_records = [
                record for record in timeline
                if symptom_lower in record["payload"].get("content", "").lower()
            ]
            
            if not related_records:
                return {
                    "success": True,
                    "symptom": symptom,
                    "occurrences": 0,
                    "message": "No records found for this symptom in the specified time window"
                }
            
            # Analyze progression
            occurrences = len(related_records)
            dates = [datetime.fromisoformat(r["payload"]["date"]) for r in related_records]
            dates.sort()
            
            # Calculate frequency
            if len(dates) > 1:
                total_span = (dates[-1] - dates[0]).days
                avg_frequency = total_span / len(dates) if total_span > 0 else 0
            else:
                avg_frequency = 0
            
            return {
                "success": True,
                "symptom": symptom,
                "occurrences": occurrences,
                "first_occurrence": dates[0].isoformat(),
                "latest_occurrence": dates[-1].isoformat(),
                "average_frequency_days": round(avg_frequency, 1),
                "trend": "recurring" if occurrences >= 3 else "isolated",
                "timeline": [
                    {
                        "date": d.isoformat(),
                        "record_type": related_records[i]["payload"].get("record_type")
                    }
                    for i, d in enumerate(dates)
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
similarity_agent = SimilarityReasoningAgent()
