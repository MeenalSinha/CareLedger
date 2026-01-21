# CareLedger Architecture Documentation

## System Overview

CareLedger is a multi-agent AI system designed to maintain lifelong medical memory for patients. The system processes multimodal medical data (text, PDFs, images) and provides intelligent retrieval, pattern recognition, and decision support.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interfaces                         │
│  ┌──────────────────┐           ┌──────────────────────────┐  │
│  │  Streamlit UI    │           │     FastAPI REST API     │  │
│  │  (Web Interface) │           │  (Programmatic Access)   │  │
│  └────────┬─────────┘           └───────────┬──────────────┘  │
└───────────┼─────────────────────────────────┼─────────────────┘
            │                                 │
            └────────────┬────────────────────┘
                         │
            ┌────────────▼─────────────┐
            │   CareLedger Orchestrator│
            │  (Main Coordinator)      │
            └────────────┬─────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌───────────────┐ ┌──────────────┐ ┌─────────────┐
│  Ingestion    │ │   Similarity │ │    Safety   │
│    Agent      │ │   Reasoning  │ │   & Ethics  │
│               │ │     Agent    │ │    Agent    │
└───────┬───────┘ └──────┬───────┘ └──────┬──────┘
        │                │                 │
        ▼                ▼                 ▼
┌───────────────┐ ┌──────────────┐ ┌──────────────┐
│ Patient Memory│ │Recommendation│ │              │
│     Agent     │ │     Agent    │ │              │
└───────┬───────┘ └──────┬───────┘ └──────────────┘
        │                │
        └────────┬───────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Qdrant  │ │ Gemini  │ │Sentence │
│ Vector  │ │   LLM   │ │Transform│
│   DB    │ │         │ │   ers   │
└─────────┘ └─────────┘ └─────────┘
```

## Component Breakdown

### 1. User Interfaces

#### Streamlit UI (app.py)
- **Purpose**: User-friendly web interface for patients
- **Features**:
  - Medical history querying
  - File upload (PDFs, images)
  - Timeline visualization
  - Memory health dashboard
  - Privacy & consent information

#### FastAPI Backend (api.py)
- **Purpose**: REST API for programmatic access
- **Endpoints**:
  - `/query` - Query medical history
  - `/ingest/text` - Ingest text records
  - `/ingest/file` - Upload files
  - `/patient/{id}/timeline` - Get timeline
  - `/patient/{id}/memory-summary` - Get memory stats

### 2. Orchestrator (orchestrator.py)

**Central coordinator** that manages the entire workflow:

```python
def process_query(query: PatientQuery) -> RetrievalResult:
    # Step 1: Safety validation
    validated_input = safety_agent.validate(query)
    
    # Step 2: Find similar cases
    similar_cases = similarity_agent.find(query)
    
    # Step 3: Get temporal context
    timeline = memory_agent.get_timeline(patient_id)
    
    # Step 4: Generate explanation
    explanation = gemini_llm.explain(similar_cases)
    
    # Step 5: Generate recommendations
    recommendations = recommendation_agent.generate(query, similar_cases)
    
    # Step 6: Safety validation of output
    return safety_agent.validate_output(result)
```

### 3. Multi-Agent System

#### Ingestion Agent (agents/ingestion_agent.py)

**Responsibility**: Convert raw medical data into embeddings

**Flow**:
1. Accept multimodal input (text, PDF, image)
2. Extract content:
   - PDF → PyPDF2 text extraction
   - Image → Feature extraction
   - Text → Direct processing
3. Generate embeddings with context
4. Store in Qdrant with metadata

**Key Methods**:
```python
def ingest_record(request: IngestionRequest) -> Dict:
    # Process based on modality
    content, embedding = self._process_modality(request)
    
    # Store in vector DB
    qdrant_manager.store_record(
        patient_id=request.patient_id,
        embedding=embedding,
        content=content,
        metadata=request.metadata
    )
```

#### Patient Memory Agent (agents/memory_agent.py)

**Responsibility**: Maintain long-term memory quality

**Features**:
- **Memory Health Assessment**: Scores based on recency, diversity, continuity
- **Temporal Decay**: Old records lose relevance over time
- **Memory Consolidation**: Identifies patterns in time windows
- **Maintenance Operations**: Regular cleanup and optimization

**Temporal Decay Formula**:
```python
decay_factor = max(0.3, 1.0 - ((age_days - DECAY_THRESHOLD) / 1000))
relevance_score *= decay_factor
```

#### Similarity Reasoning Agent (agents/similarity_agent.py)

**Responsibility**: Find similar past medical states

**Process**:
1. Generate query embedding
2. Semantic search in Qdrant
3. Separate recent vs. old cases
4. Identify forgotten patterns
5. Build temporal context

**Pattern Recognition**:
- Recurring symptoms
- Seasonal patterns
- Treatment efficacy
- Unfollowed recommendations

**Key Algorithm**:
```python
def find_similar_cases(patient_id, query):
    # Embed query
    embedding = embed_text(query)
    
    # Search Qdrant
    results = qdrant.search(
        embedding=embedding,
        patient_id=patient_id,
        limit=10,
        threshold=0.5
    )
    
    # Separate by time
    recent = [r for r in results if age(r) < 180_days]
    old = [r for r in results if age(r) >= 180_days]
    
    # Find forgotten insights
    insights = identify_forgotten(old, recent)
    
    return recent, old, insights
```

#### Safety & Ethics Agent (agents/safety_agent.py)

**Responsibility**: Ensure ethical and safe operation

**Validations**:
1. **Input Sanitization**:
   - XSS prevention
   - Length limits
   - Patient ID format validation

2. **Emergency Detection**:
   - Keyword scanning for emergencies
   - Immediate alert generation

3. **Output Validation**:
   - No diagnostic language
   - Proper disclaimers
   - Source attribution

4. **Ethics Enforcement**:
   - Informed consent
   - Data usage transparency
   - Privacy guarantees

**Diagnostic Language Detection**:
```python
diagnostic_keywords = [
    "you have", "diagnosed with", "treatment for",
    "prescribe", "medical advice"
]

for keyword in diagnostic_keywords:
    if keyword in output.lower():
        flag_warning(f"Potentially diagnostic: {keyword}")
```

#### Recommendation Agent (agents/recommendation_agent.py)

**Responsibility**: Generate actionable, non-diagnostic suggestions

**Types of Recommendations**:
1. **Doctor Questions**: Specific questions to ask healthcare provider
2. **Self-Monitoring**: Tracking and journaling suggestions
3. **Reminders**: Follow-up and appointment reminders
4. **Information Gathering**: What data to collect

**Generation Process**:
```python
def generate_recommendations(query, similar_cases, timeline):
    recommendations = []
    
    # Doctor questions based on patterns
    if has_recurring_pattern(similar_cases):
        recommendations.append(
            "Should we discuss the pattern of recurring symptoms?"
        )
    
    # Monitoring based on symptom type
    if "pain" in query:
        recommendations.append(
            "Rate pain on 1-10 scale and track triggers"
        )
    
    # Use LLM for context-aware suggestions
    llm_recs = gemini.generate_recommendations(query, timeline)
    
    return prioritize(recommendations + llm_recs)
```

### 4. Core Technologies

#### Qdrant Vector Database (utils/vector_store.py)

**Why Qdrant?**
- Native multimodal support (multiple vector spaces)
- Efficient similarity search (HNSW algorithm)
- Rich filtering (temporal, metadata)
- In-memory mode for demos
- Production-ready scalability

**Data Model**:
```python
Point {
    id: UUID,
    vectors: {
        "text": [384-dim embedding],
        "image": [512-dim embedding]
    },
    payload: {
        "patient_id": str,
        "record_type": str,
        "content": str,
        "date": ISO timestamp,
        "metadata": dict,
        "access_count": int,
        "relevance_score": float
    }
}
```

**Key Operations**:
```python
# Store
qdrant.upsert(
    collection="patient_memory",
    points=[point]
)

# Search with filters
results = qdrant.search(
    vector=query_embedding,
    filter=Filter(
        must=[
            FieldCondition(key="patient_id", match=patient_id),
            FieldCondition(key="date", range={"gte": cutoff_date})
        ]
    ),
    limit=10
)
```

#### Sentence Transformers (utils/embeddings.py)

**Model**: all-MiniLM-L6-v2
- **Dimensions**: 384
- **Performance**: Fast inference (~100ms per doc)
- **Quality**: Good for medical text similarity

**Medical Context Enhancement**:
```python
def embed_medical_text(text, context):
    # Enhance with medical context
    enhanced = text
    if context.get('symptoms'):
        enhanced += f" Symptoms: {', '.join(context['symptoms'])}"
    if context.get('diagnosis'):
        enhanced += f" Diagnosis: {context['diagnosis']}"
    
    return model.encode(enhanced)
```

#### Google Gemini LLM (utils/llm.py)

**Model**: gemini-pro

**Usage**:
1. **Explanation Generation**: Explain similarity results
2. **Recommendation Generation**: Context-aware suggestions
3. **Forgotten Insight Identification**: Analyze old records

**Prompt Engineering**:
```python
prompt = f"""You are a medical information assistant for CareLedger.

IMPORTANT: You provide decision support, NOT diagnosis.

Patient Query: {query}

Similar Past Records:
{format_records(similar_cases)}

Please provide:
1. How these records relate to current query
2. Important patterns noticed
3. 2-3 questions for the doctor

Remember: Focus on information, not diagnosis."""
```

## Data Flow

### Ingestion Flow

```
User uploads PDF report
    ↓
FastAPI/Streamlit receives file
    ↓
Save to data/uploads/
    ↓
Ingestion Agent processes:
    - Extract text from PDF (PyPDF2)
    - Generate text embedding (384-dim)
    - Extract metadata
    ↓
Store in Qdrant:
    - Vector: embedding
    - Payload: content + metadata
    ↓
Return success/record_id
```

### Query Flow

```
User enters query: "What helped my headaches?"
    ↓
Safety Agent validates input
    ↓
Generate query embedding (384-dim)
    ↓
Similarity Agent searches Qdrant:
    - Filter by patient_id
    - Cosine similarity search
    - Return top 10 results
    ↓
Separate recent (< 6mo) vs old (> 6mo) cases
    ↓
Memory Agent provides timeline context
    ↓
Gemini LLM generates explanation:
    - Analyze similar cases
    - Identify patterns
    - Generate human-readable text
    ↓
Recommendation Agent suggests:
    - Doctor questions
    - Self-monitoring actions
    - Follow-up reminders
    ↓
Safety Agent validates output:
    - Check for diagnostic language
    - Add disclaimers
    - Ensure source attribution
    ↓
Return comprehensive result to user
```

## Scaling Considerations

### Current (Demo) Scale
- **Storage**: In-memory Qdrant
- **Patients**: 1-100
- **Records per patient**: 10-1000
- **Concurrent users**: 1-10

### Production Scale
- **Storage**: Qdrant cluster (persistent)
- **Patients**: 100,000+
- **Records per patient**: 1,000-10,000
- **Concurrent users**: 1,000+

### Optimization Strategies

1. **Vector Database**:
   - Shard by patient_id
   - Use HNSW index (already default)
   - Implement quantization for large scale

2. **Embeddings**:
   - Batch processing
   - GPU acceleration
   - Cache frequent queries

3. **LLM**:
   - Response caching
   - Rate limiting
   - Batch similar queries

4. **API**:
   - Add rate limiting
   - Implement caching (Redis)
   - Use load balancer

## Security Considerations

### Data Privacy
- ✅ Patient-level isolation in Qdrant
- ✅ No cross-patient data leakage
- ✅ Local deployment option
- ⚠️ TODO: Encryption at rest
- ⚠️ TODO: Encryption in transit (HTTPS)

### Authentication (Future)
- Patient authentication
- Doctor access controls
- Audit logging
- HIPAA compliance measures

### Input Validation
- XSS prevention
- SQL injection prevention (N/A - no SQL)
- File upload validation
- Size limits

## Performance Metrics

### Latency Targets
- Query processing: < 2 seconds
- File ingestion: < 5 seconds
- Timeline retrieval: < 1 second
- Memory summary: < 1 second

### Throughput Targets
- Queries: 100 req/sec
- Ingestions: 10 req/sec

### Current Performance (Demo)
- Query: ~1-3 seconds
- Ingestion: ~0.5-2 seconds
- Timeline: ~0.2 seconds

## Future Enhancements

### Technical
1. Advanced medical image analysis (MedCLIP/Bio-CLIP)
2. Audio transcription (Whisper integration)
3. Multi-patient family accounts
4. EHR system integration
5. Mobile app

### Features
1. Medication interaction warnings
2. Lab result trend analysis
3. Genetic data integration
4. Doctor collaboration tools
5. Appointment scheduling

### Scale
1. Multi-tenancy architecture
2. Distributed vector database
3. Real-time sync
4. Cloud deployment
5. HIPAA-compliant infrastructure

## Monitoring & Observability

### Metrics to Track
- Query latency
- Ingestion success rate
- Vector search performance
- LLM API errors
- User engagement

### Logging
- All agent interactions
- Error traces
- User actions (privacy-aware)
- System performance

### Alerts
- High error rates
- Slow queries
- Storage limits
- API quota exceeded

---

**Last Updated**: January 2026
**Version**: 1.0.0
