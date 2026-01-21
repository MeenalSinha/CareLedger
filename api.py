"""
FastAPI Backend for CareLedger
Provides REST API for all CareLedger operations
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import shutil
import os
from datetime import datetime

from orchestrator import orchestrator
from models.schemas import (
    PatientQuery, IngestionRequest, RecordType, Modality
)

# Initialize FastAPI app
app = FastAPI(
    title="CareLedger API",
    description="AI-powered lifelong medical memory system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class QueryRequest(BaseModel):
    patient_id: str
    query_text: str
    current_symptoms: Optional[List[str]] = None

class IngestTextRequest(BaseModel):
    patient_id: str
    record_type: str
    content: str
    metadata: Optional[dict] = {}

class SymptomAnalysisRequest(BaseModel):
    patient_id: str
    symptom: str
    time_window_days: int = 365

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize CareLedger on startup"""
    orchestrator.initialize()
    print("CareLedger API started successfully!")

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "CareLedger API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# Query endpoint
@app.post("/query")
async def query_medical_history(request: QueryRequest):
    """
    Query patient's medical history
    Returns similar cases, recommendations, and insights
    """
    try:
        # Create query object
        query = PatientQuery(
            patient_id=request.patient_id,
            query_text=request.query_text,
            current_symptoms=request.current_symptoms
        )
        
        # Process query through orchestrator
        result = orchestrator.process_query(query)
        
        return {
            "success": True,
            "result": result.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ingest text record
@app.post("/ingest/text")
async def ingest_text_record(request: IngestTextRequest):
    """Ingest a text-based medical record"""
    try:
        # Validate record type
        try:
            record_type = RecordType(request.record_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid record type. Must be one of: {[t.value for t in RecordType]}"
            )
        
        # Create ingestion request
        ingestion_request = IngestionRequest(
            patient_id=request.patient_id,
            record_type=record_type,
            modality=Modality.TEXT,
            content=request.content,
            metadata=request.metadata or {}
        )
        
        # Add date if not provided
        if "date" not in ingestion_request.metadata:
            ingestion_request.metadata["date"] = datetime.now()
        
        # Ingest through orchestrator
        result = orchestrator.ingest_record(ingestion_request)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ingest file (PDF or image)
@app.post("/ingest/file")
async def ingest_file(
    patient_id: str = Form(...),
    record_type: str = Form(...),
    file: UploadFile = File(...),
    metadata: Optional[str] = Form("{}")
):
    """Ingest a file-based medical record (PDF or image)"""
    try:
        # Validate record type
        try:
            record_type_enum = RecordType(record_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid record type. Must be one of: {[t.value for t in RecordType]}"
            )
        
        # Save uploaded file
        upload_dir = "data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"{patient_id}_{datetime.now().timestamp()}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Determine modality
        file_extension = file.filename.lower().split(".")[-1]
        if file_extension == "pdf":
            modality = Modality.TEXT
        elif file_extension in ["jpg", "jpeg", "png", "gif", "bmp"]:
            modality = Modality.IMAGE
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Use PDF or image files."
            )
        
        # Parse metadata
        import json
        try:
            metadata_dict = json.loads(metadata)
        except:
            metadata_dict = {}
        
        # Create ingestion request
        ingestion_request = IngestionRequest(
            patient_id=patient_id,
            record_type=record_type_enum,
            modality=modality,
            file_path=file_path,
            metadata=metadata_dict
        )
        
        # Add date if not provided
        if "date" not in ingestion_request.metadata:
            ingestion_request.metadata["date"] = datetime.now()
        
        # Ingest through orchestrator
        result = orchestrator.ingest_record(ingestion_request)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get patient timeline
@app.get("/patient/{patient_id}/timeline")
async def get_patient_timeline(patient_id: str):
    """Get patient's complete medical timeline"""
    try:
        timeline = orchestrator.get_patient_timeline(patient_id)
        return {
            "success": True,
            "timeline": timeline.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get memory summary
@app.get("/patient/{patient_id}/memory-summary")
async def get_memory_summary(patient_id: str):
    """Get patient's memory summary and health"""
    try:
        summary = orchestrator.get_memory_summary(patient_id)
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analyze symptom progression
@app.post("/patient/{patient_id}/analyze-symptom")
async def analyze_symptom(patient_id: str, request: SymptomAnalysisRequest):
    """Analyze how a symptom has progressed over time"""
    try:
        result = orchestrator.analyze_symptom_progression(
            patient_id=request.patient_id,
            symptom=request.symptom,
            time_window_days=request.time_window_days
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Apply memory maintenance
@app.post("/patient/{patient_id}/maintenance")
async def apply_maintenance(patient_id: str):
    """Apply memory maintenance (temporal decay, etc.)"""
    try:
        result = orchestrator.apply_memory_maintenance(patient_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get consent notice
@app.get("/consent")
async def get_consent():
    """Get informed consent notice"""
    return {
        "consent_notice": orchestrator.get_consent_notice()
    }

# Get data usage policy
@app.get("/data-policy")
async def get_data_policy():
    """Get data usage policy"""
    return {
        "data_policy": orchestrator.get_data_usage_policy()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
