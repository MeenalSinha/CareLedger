"""
Embedding utilities for multimodal medical data
"""
from sentence_transformers import SentenceTransformer
from PIL import Image
import torch
import numpy as np
from typing import List, Union
import io
import base64

class EmbeddingManager:
    """Manages embeddings for different modalities"""
    
    def __init__(self):
        self.text_model = None
        self.initialized = False
        
    def initialize(self):
        """Lazy initialization of models"""
        if not self.initialized:
            print("Loading embedding models...")
            self.text_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            self.initialized = True
            print("Models loaded successfully")
    
    def embed_text(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text"""
        self.initialize()
        
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.text_model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def embed_medical_text(self, text: str, context: dict = None) -> np.ndarray:
        """
        Generate embeddings for medical text with context
        Context can include: symptoms, diagnoses, medications, etc.
        """
        self.initialize()
        
        # Enhance text with context for better similarity matching
        enhanced_text = text
        if context:
            if context.get('symptoms'):
                enhanced_text += f" Symptoms: {', '.join(context['symptoms'])}"
            if context.get('diagnosis'):
                enhanced_text += f" Diagnosis: {context['diagnosis']}"
            if context.get('medications'):
                enhanced_text += f" Medications: {', '.join(context['medications'])}"
        
        embedding = self.text_model.encode(enhanced_text, convert_to_numpy=True)
        return embedding
    
    def embed_image(self, image_path: str) -> np.ndarray:
        """
        Generate embeddings for medical images (X-rays, scans, etc.)
        Using a simple approach - in production, use Bio/MedCLIP
        """
        try:
            # For demo purposes, create a dummy embedding
            # In production, use CLIP or MedCLIP
            img = Image.open(image_path)
            
            # Simple feature extraction (placeholder)
            # Convert to grayscale and resize
            img_gray = img.convert('L').resize((224, 224))
            img_array = np.array(img_gray)
            
            # Create a simple feature vector (in production, use proper CNN)
            features = []
            features.append(img_array.mean())  # Mean intensity
            features.append(img_array.std())   # Standard deviation
            features.extend(np.histogram(img_array, bins=10)[0] / img_array.size)  # Histogram
            
            # Pad to 512 dimensions for consistency
            embedding = np.zeros(512)
            embedding[:len(features)] = features
            
            return embedding
            
        except Exception as e:
            print(f"Error embedding image: {e}")
            # Return zero vector on error
            return np.zeros(512)
    
    def get_embedding_dimension(self, modality: str) -> int:
        """Get the dimension of embeddings for a given modality"""
        if modality == "text":
            return 384  # all-MiniLM-L6-v2
        elif modality == "image":
            return 512  # CLIP/Custom
        else:
            return 384  # Default

# Global instance
embedding_manager = EmbeddingManager()
