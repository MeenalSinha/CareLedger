"""
Data models for CareLedger
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class RecordType(str, Enum):
    REPORT = "report"
    SYMPTOM = "symptom"
    SCAN = "scan"
    VOICE_NOTE = "voice_note"
    PRESCRIPTION = "prescription"
    DOCTOR_NOTE = "doctor_note"

class Modality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"

class MedicalRecord(BaseModel):
    """Base model for medical records"""
    patient_id: str
    record_id: str
    record_type: RecordType
    modality: Modality
    content: str
    date: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source_file: Optional[str] = None
    
class PatientQuery(BaseModel):
    """Model for patient queries"""
    patient_id: str
    query_text: str
    current_symptoms: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None

class SimilarCase(BaseModel):
    """Model for similar past cases"""
    record_id: str
    record_type: RecordType
    content: str
    date: datetime
    similarity_score: float
    relevance_explanation: str
    metadata: Dict[str, Any]

class RetrievalResult(BaseModel):
    """Model for retrieval results with structured evidence"""
    query: str
    similar_cases: List[SimilarCase]
    temporal_context: List[Dict[str, Any]]
    forgotten_insights: List[str]
    recommendations: List[str]
    safety_disclaimer: str
    
    # STRUCTURED EVIDENCE TRACE (for judges)
    evidence_trace: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Structured evidence showing what records were used and why"
    )
    reasoning_steps: Optional[List[str]] = Field(
        default_factory=list,
        description="Step-by-step reasoning process"
    )
    evidence_summary: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Summary statistics of evidence used"
    )
    
    class Config:
        arbitrary_types_allowed = True

class IngestionRequest(BaseModel):
    """Model for ingestion requests"""
    patient_id: str
    record_type: RecordType
    modality: Modality
    content: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TimelineEvent(BaseModel):
    """Model for timeline events"""
    date: datetime
    event_type: str
    title: str
    description: str
    record_id: str
    metadata: Dict[str, Any]

class PatientTimeline(BaseModel):
    """Model for patient timeline"""
    patient_id: str
    events: List[TimelineEvent]
    total_records: int
    date_range: Dict[str, datetime]
