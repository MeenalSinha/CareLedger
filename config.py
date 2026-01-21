"""
Configuration module for CareLedger
"""
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

load_dotenv()

class Settings(BaseModel):
    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Qdrant Configuration
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")
    
    # Application Configuration
    APP_NAME: str = os.getenv("APP_NAME", "CareLedger")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Collection Names
    PATIENT_COLLECTION: str = "patient_memory"
    
    # Embedding Dimensions
    TEXT_EMBEDDING_DIM: int = 384  # all-MiniLM-L6-v2
    IMAGE_EMBEDDING_DIM: int = 512  # CLIP
    
    # Model Names
    TEXT_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_VISION_MODEL: str = "gemini-pro-vision"
    
    # Memory Configuration
    MEMORY_DECAY_DAYS: int = 365  # Days after which old memories start decaying
    REINFORCEMENT_THRESHOLD: int = 3  # Number of similar queries to reinforce memory
    
    class Config:
        env_file = ".env"

settings = Settings()
