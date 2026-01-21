"""
Ingestion Agent
Converts reports, images, and audio into embeddings and stores them
"""
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
import PyPDF2
import io
from PIL import Image

from models.schemas import MedicalRecord, RecordType, Modality, IngestionRequest
from utils.embeddings import embedding_manager
from utils.vector_store import qdrant_manager

class IngestionAgent:
    """
    Agent responsible for ingesting multimodal medical data
    - Processes PDFs, images, text, audio
    - Generates embeddings
    - Stores in Qdrant
    """
    
    def __init__(self):
        self.name = "Ingestion Agent"
        
    def ingest_record(self, request: IngestionRequest) -> Dict[str, Any]:
        """Ingest a medical record"""
        try:
            # Generate unique record ID
            record_id = str(uuid.uuid4())
            
            # Process based on modality
            if request.modality == Modality.TEXT:
                content, embedding = self._process_text(request)
            elif request.modality == Modality.IMAGE:
                content, embedding = self._process_image(request)
            elif request.modality == Modality.AUDIO:
                content, embedding = self._process_audio(request)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported modality: {request.modality}"
                }
            
            # Store in Qdrant
            success = qdrant_manager.store_record(
                patient_id=request.patient_id,
                record_id=record_id,
                embedding=embedding,
                modality=request.modality.value,
                record_type=request.record_type.value,
                content=content,
                date=request.metadata.get("date", datetime.now()),
                metadata=request.metadata
            )
            
            if success:
                return {
                    "success": True,
                    "record_id": record_id,
                    "message": f"Successfully ingested {request.record_type.value}"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to store in vector database"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_text(self, request: IngestionRequest) -> tuple:
        """Process text content"""
        content = request.content or ""
        
        # If file path provided, extract text from PDF
        if request.file_path and request.file_path.endswith('.pdf'):
            content = self._extract_text_from_pdf(request.file_path)
        
        # Generate embedding with medical context
        context = {
            "symptoms": request.metadata.get("symptoms", []),
            "diagnosis": request.metadata.get("diagnosis"),
            "medications": request.metadata.get("medications", [])
        }
        
        embedding = embedding_manager.embed_medical_text(content, context)
        
        return content, embedding
    
    def _process_image(self, request: IngestionRequest) -> tuple:
        """Process medical image (X-ray, scan, etc.)"""
        if not request.file_path:
            raise ValueError("Image file path required")
        
        # Extract text description if provided
        content = request.content or f"Medical image: {request.record_type.value}"
        
        # Add metadata context
        if request.metadata.get("scan_type"):
            content += f" - {request.metadata['scan_type']}"
        if request.metadata.get("body_part"):
            content += f" of {request.metadata['body_part']}"
        
        # Generate image embedding
        image_embedding = embedding_manager.embed_image(request.file_path)
        
        # Also generate text embedding for the description
        text_embedding = embedding_manager.embed_text(content)
        
        # For now, use text embedding (in production, use multimodal fusion)
        return content, text_embedding
    
    def _process_audio(self, request: IngestionRequest) -> tuple:
        """Process audio (doctor voice notes)"""
        # In production, use Whisper to transcribe
        # For demo, assume transcription is provided
        content = request.content or "Audio transcription not available"
        
        if request.metadata.get("transcription"):
            content = request.metadata["transcription"]
        
        embedding = embedding_manager.embed_text(content)
        
        return content, embedding
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def batch_ingest(self, requests: list) -> Dict[str, Any]:
        """Ingest multiple records in batch"""
        results = {
            "success": [],
            "failed": []
        }
        
        for request in requests:
            result = self.ingest_record(request)
            if result["success"]:
                results["success"].append(result)
            else:
                results["failed"].append(result)
        
        return {
            "total": len(requests),
            "success_count": len(results["success"]),
            "failed_count": len(results["failed"]),
            "results": results
        }

# Global instance
ingestion_agent = IngestionAgent()
