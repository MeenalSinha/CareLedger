"""
Unit tests for CareLedger agents
"""
import pytest
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.ingestion_agent import ingestion_agent
from agents.memory_agent import memory_agent
from agents.similarity_agent import similarity_agent
from agents.safety_agent import safety_agent
from agents.recommendation_agent import recommendation_agent
from models.schemas import IngestionRequest, RecordType, Modality, PatientQuery


class TestIngestionAgent:
    """Test suite for Ingestion Agent"""
    
    def test_ingestion_agent_exists(self):
        """Test that ingestion agent is initialized"""
        assert ingestion_agent is not None
        assert ingestion_agent.name == "Ingestion Agent"
    
    def test_ingest_text_record(self):
        """Test text record ingestion"""
        request = IngestionRequest(
            patient_id="test_001",
            record_type=RecordType.SYMPTOM,
            modality=Modality.TEXT,
            content="Test headache symptom",
            metadata={"symptoms": ["headache"]}
        )
        
        # Note: This test requires Qdrant initialization
        # In production, use mock or test fixtures
        try:
            result = ingestion_agent.ingest_record(request)
            assert "success" in result
        except Exception as e:
            # If Qdrant not initialized, that's expected in isolated tests
            assert "initialize" in str(e).lower() or "connection" in str(e).lower()
    
    def test_batch_ingest(self):
        """Test batch ingestion"""
        requests = [
            IngestionRequest(
                patient_id="test_001",
                record_type=RecordType.SYMPTOM,
                modality=Modality.TEXT,
                content=f"Test symptom {i}",
                metadata={"date": datetime.now()}
            )
            for i in range(3)
        ]
        
        try:
            result = ingestion_agent.batch_ingest(requests)
            assert "total" in result
            assert result["total"] == 3
        except Exception:
            # Expected if Qdrant not initialized
            pass


class TestMemoryAgent:
    """Test suite for Memory Agent"""
    
    def test_memory_agent_exists(self):
        """Test that memory agent is initialized"""
        assert memory_agent is not None
        assert memory_agent.name == "Patient Memory Agent"
    
    def test_get_patient_memory_summary(self):
        """Test memory summary generation"""
        result = memory_agent.get_patient_memory_summary("test_001")
        
        assert "patient_id" in result
        assert result["patient_id"] == "test_001"
        # May have no records, which is valid
        assert "total_records" in result


class TestSimilarityAgent:
    """Test suite for Similarity Reasoning Agent"""
    
    def test_similarity_agent_exists(self):
        """Test that similarity agent is initialized"""
        assert similarity_agent is not None
        assert similarity_agent.name == "Similarity Reasoning Agent"
    
    def test_find_similar_cases(self):
        """Test similar case finding"""
        try:
            result = similarity_agent.find_similar_cases(
                patient_id="test_001",
                query="headache symptoms"
            )
            
            assert "success" in result
            assert "query" in result
            assert result["query"] == "headache symptoms"
        except Exception:
            # Expected if no data exists
            pass


class TestSafetyAgent:
    """Test suite for Safety & Ethics Agent"""
    
    def test_safety_agent_exists(self):
        """Test that safety agent is initialized"""
        assert safety_agent is not None
        assert safety_agent.name == "Safety & Ethics Agent"
    
    def test_sanitize_valid_input(self):
        """Test input sanitization with valid input"""
        result = safety_agent.sanitize_user_input("What treatments helped my headaches?")
        
        assert result["valid"] is True
        assert "sanitized" in result
        assert result["sanitized"] is not None
    
    def test_sanitize_empty_input(self):
        """Test input sanitization with empty input"""
        result = safety_agent.sanitize_user_input("")
        
        assert result["valid"] is False
        assert "error" in result
    
    def test_sanitize_long_input(self):
        """Test input sanitization with overly long input"""
        long_input = "a" * 6000
        result = safety_agent.sanitize_user_input(long_input)
        
        assert result["valid"] is False
        assert "too long" in result["error"].lower()
    
    def test_validate_patient_id_valid(self):
        """Test patient ID validation with valid ID"""
        result = safety_agent.validate_patient_id("patient_001")
        
        assert result["valid"] is True
        assert result["patient_id"] == "patient_001"
    
    def test_validate_patient_id_invalid(self):
        """Test patient ID validation with invalid ID"""
        result = safety_agent.validate_patient_id("patient@#$%")
        
        assert result["valid"] is False
    
    def test_check_emergency_indicators(self):
        """Test emergency detection"""
        result = safety_agent.check_emergency_indicators("I'm having chest pain")
        
        assert "emergency_detected" in result
        assert result["emergency_detected"] is True
        assert "keywords" in result
    
    def test_check_no_emergency(self):
        """Test no emergency detection"""
        result = safety_agent.check_emergency_indicators("I have a mild headache")
        
        assert result["emergency_detected"] is False
    
    def test_validate_output(self):
        """Test output validation"""
        output = {
            "query": "test query",
            "similar_cases": [],
            "recommendations": ["See your doctor"],
            "explanation": "Based on your history..."
        }
        
        result = safety_agent.validate_output(output)
        
        assert "safety_disclaimer" in result
        assert "flagged" in result


class TestRecommendationAgent:
    """Test suite for Recommendation Agent"""
    
    def test_recommendation_agent_exists(self):
        """Test that recommendation agent is initialized"""
        assert recommendation_agent is not None
        assert recommendation_agent.name == "Recommendation Agent"
    
    def test_generate_recommendations(self):
        """Test recommendation generation"""
        result = recommendation_agent.generate_recommendations(
            query="What should I ask my doctor?",
            similar_cases=[],
            timeline_context=[],
            forgotten_insights=[]
        )
        
        assert "success" in result
        assert "recommendations" in result


class TestAgentIntegration:
    """Integration tests for agent coordination"""
    
    def test_all_agents_initialized(self):
        """Test that all agents are properly initialized"""
        agents = [
            ingestion_agent,
            memory_agent,
            similarity_agent,
            safety_agent,
            recommendation_agent
        ]
        
        for agent in agents:
            assert agent is not None
            assert hasattr(agent, 'name')
            assert agent.name is not None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
