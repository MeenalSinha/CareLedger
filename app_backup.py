"""
CareLedger Streamlit Frontend
User-friendly interface for interacting with CareLedger
"""
import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import orchestrator
from models.schemas import (
    PatientQuery, IngestionRequest, RecordType, Modality
)

# Page configuration
st.set_page_config(
    page_title="CareLedger - Your Medical Memory",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .disclaimer-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .insight-box {
        background-color: #d1ecf1;
        border-left: 5px solid #0c5460;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .recommendation-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .timeline-event {
        border-left: 3px solid #1f77b4;
        padding-left: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.patient_id = "demo_patient_001"
    st.session_state.query_history = []

# Initialize orchestrator
if not st.session_state.initialized:
    with st.spinner("Initializing CareLedger..."):
        orchestrator.initialize()
        st.session_state.initialized = True

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=CareLedger", use_container_width=True)
    
    st.markdown("### Patient Information")
    patient_id = st.text_input(
        "Patient ID",
        value=st.session_state.patient_id,
        help="Enter your unique patient identifier"
    )
    st.session_state.patient_id = patient_id
    
    st.markdown("---")
    
    st.markdown("### Navigation")
    page = st.radio(
        "Select a page:",
        ["🏠 Home", "🔍 Query History", "📊 Timeline", "📁 Upload Records", "⚙️ Settings"]
    )
    
    st.markdown("---")
    
    # Memory summary in sidebar
    if st.button("View Memory Summary"):
        with st.spinner("Loading memory summary..."):
            summary = orchestrator.get_memory_summary(patient_id)
            st.session_state.show_summary = True
            st.session_state.memory_summary = summary

# Main content area
if page == "🏠 Home":
    # Header
    st.markdown('<h1 class="main-header">🏥 CareLedger</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your AI-Powered Lifelong Medical Memory</p>', unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
    <div class="disclaimer-box">
        <strong>⚕️ IMPORTANT DISCLAIMER:</strong> CareLedger provides decision support only, not medical diagnosis. 
        All information should be discussed with your healthcare provider. In case of emergency, contact emergency services immediately.
    </div>
    """, unsafe_allow_html=True)
    
    # Query interface
    st.markdown("### 💬 Ask About Your Medical History")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query_text = st.text_area(
            "Enter your question or describe your symptoms:",
            placeholder="Example: I'm experiencing headaches similar to what I had last year. What did the doctor recommend back then?",
            height=100
        )
    
    with col2:
        st.markdown("##### Quick Examples")
        if st.button("Recurring symptoms"):
            query_text = "I'm experiencing symptoms similar to 6 months ago. What happened then?"
        if st.button("Past treatments"):
            query_text = "What treatments have I tried for similar conditions?"
        if st.button("Doctor questions"):
            query_text = "What should I ask my doctor about this recurring issue?"
    
    if st.button("🔍 Search Medical History", type="primary", use_container_width=True):
        if query_text:
            with st.spinner("Analyzing your medical history..."):
                # Process query
                query = PatientQuery(
                    patient_id=patient_id,
                    query_text=query_text
                )
                
                result = orchestrator.process_query(query)
                
                # Store in history
                st.session_state.query_history.append({
                    "timestamp": datetime.now(),
                    "query": query_text,
                    "result": result
                })
                
                # Display results
                st.markdown("---")
                st.markdown("### 📋 Results")
                
                # Similar cases
                if result.similar_cases:
                    st.markdown("#### 🔄 Similar Past Cases")
                    for i, case in enumerate(result.similar_cases[:5], 1):
                        with st.expander(f"{i}. {case.record_type} - {case.date.strftime('%B %d, %Y')} (Similarity: {case.similarity_score:.0%})"):
                            st.markdown(f"**Content:** {case.content[:300]}...")
                            st.markdown(f"**Relevance:** {case.relevance_explanation}")
                else:
                    st.info("No similar cases found in your medical history.")
                
                # Forgotten insights
                if result.forgotten_insights:
                    st.markdown("#### 💡 Forgotten Insights")
                    for insight in result.forgotten_insights:
                        st.markdown(f"""
                        <div class="insight-box">
                            🔍 {insight}
                        </div>
                        """, unsafe_allow_html=True)
                
                # Recommendations
                if result.recommendations:
                    st.markdown("#### ✅ Recommendations")
                    for i, rec in enumerate(result.recommendations, 1):
                        st.markdown(f"""
                        <div class="recommendation-box">
                            {i}. {rec}
                        </div>
                        """, unsafe_allow_html=True)
                
                # Safety disclaimer
                st.markdown("---")
                st.info(result.safety_disclaimer)
        else:
            st.warning("Please enter a question or describe your symptoms.")

elif page == "🔍 Query History":
    st.markdown("## 🔍 Query History")
    
    if st.session_state.query_history:
        for i, entry in enumerate(reversed(st.session_state.query_history), 1):
            with st.expander(f"Query {len(st.session_state.query_history) - i + 1}: {entry['query'][:50]}... ({entry['timestamp'].strftime('%Y-%m-%d %H:%M')})"):
                st.markdown(f"**Query:** {entry['query']}")
                st.markdown(f"**Time:** {entry['timestamp'].strftime('%B %d, %Y at %I:%M %p')}")
                
                result = entry['result']
                
                st.markdown(f"**Similar Cases Found:** {len(result.similar_cases)}")
                st.markdown(f"**Recommendations:** {len(result.recommendations)}")
                
                if st.button(f"View Details {i}", key=f"view_{i}"):
                    st.json(result.dict())
    else:
        st.info("No query history yet. Start by asking a question on the Home page!")

elif page == "📊 Timeline":
    st.markdown("## 📊 Medical Timeline")
    
    if st.button("Load Timeline"):
        with st.spinner("Loading your medical timeline..."):
            timeline = orchestrator.get_patient_timeline(patient_id)
            
            if timeline.events:
                st.success(f"Found {timeline.total_records} medical records")
                
                # Date range
                if timeline.date_range:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("First Record", timeline.date_range['earliest'].strftime('%B %d, %Y'))
                    with col2:
                        st.metric("Latest Record", timeline.date_range['latest'].strftime('%B %d, %Y'))
                
                st.markdown("---")
                
                # Timeline visualization
                for event in reversed(timeline.events):
                    st.markdown(f"""
                    <div class="timeline-event">
                        <strong>{event.date.strftime('%B %d, %Y')}</strong> - {event.title}<br>
                        <small>{event.description}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No medical records found. Upload some records to build your timeline!")

elif page == "📁 Upload Records":
    st.markdown("## 📁 Upload Medical Records")
    
    tab1, tab2, tab3 = st.tabs(["📝 Text/Symptoms", "📄 PDF Report", "🖼️ Medical Image"])
    
    with tab1:
        st.markdown("### Record Symptom or Text Note")
        
        record_type = st.selectbox(
            "Record Type",
            [r.value for r in RecordType],
            key="text_record_type"
        )
        
        content = st.text_area(
            "Content",
            placeholder="Describe your symptoms, copy medical report text, or paste doctor's notes...",
            height=150
        )
        
        col1, col2 = st.columns(2)
        with col1:
            symptoms = st.text_input("Symptoms (comma-separated)", "")
        with col2:
            diagnosis = st.text_input("Diagnosis (if any)", "")
        
        if st.button("💾 Save Text Record"):
            if content:
                metadata = {
                    "date": datetime.now(),
                    "symptoms": [s.strip() for s in symptoms.split(",") if s.strip()],
                    "diagnosis": diagnosis if diagnosis else None
                }
                
                request = IngestionRequest(
                    patient_id=patient_id,
                    record_type=RecordType(record_type),
                    modality=Modality.TEXT,
                    content=content,
                    metadata=metadata
                )
                
                with st.spinner("Saving record..."):
                    result = orchestrator.ingest_record(request)
                    
                    if result.get("success"):
                        st.success(f"✅ {result.get('message')}")
                    else:
                        st.error(f"❌ {result.get('error')}")
            else:
                st.warning("Please enter content")
    
    with tab2:
        st.markdown("### Upload PDF Report")
        
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
        
        if uploaded_file:
            st.info(f"File: {uploaded_file.name}")
            
            report_type = st.selectbox(
                "Report Type",
                ["report", "prescription"],
                key="pdf_record_type"
            )
            
            if st.button("📤 Upload PDF"):
                # Save file
                upload_dir = "data/uploads"
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(
                    upload_dir,
                    f"{patient_id}_{datetime.now().timestamp()}_{uploaded_file.name}"
                )
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Create ingestion request
                request = IngestionRequest(
                    patient_id=patient_id,
                    record_type=RecordType(report_type),
                    modality=Modality.TEXT,
                    file_path=file_path,
                    metadata={"date": datetime.now()}
                )
                
                with st.spinner("Processing PDF..."):
                    result = orchestrator.ingest_record(request)
                    
                    if result.get("success"):
                        st.success(f"✅ {result.get('message')}")
                    else:
                        st.error(f"❌ {result.get('error')}")
    
    with tab3:
        st.markdown("### Upload Medical Image")
        
        uploaded_image = st.file_uploader(
            "Choose an image file",
            type=["jpg", "jpeg", "png"],
            key="image_upload"
        )
        
        if uploaded_image:
            st.image(uploaded_image, caption="Preview", use_container_width=True)
            
            scan_type = st.text_input("Scan Type", placeholder="e.g., X-Ray, MRI, CT Scan")
            body_part = st.text_input("Body Part", placeholder="e.g., Chest, Knee, Head")
            
            if st.button("📤 Upload Image"):
                # Save file
                upload_dir = "data/uploads"
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(
                    upload_dir,
                    f"{patient_id}_{datetime.now().timestamp()}_{uploaded_image.name}"
                )
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_image.getbuffer())
                
                # Create ingestion request
                request = IngestionRequest(
                    patient_id=patient_id,
                    record_type=RecordType.SCAN,
                    modality=Modality.IMAGE,
                    file_path=file_path,
                    metadata={
                        "date": datetime.now(),
                        "scan_type": scan_type,
                        "body_part": body_part
                    }
                )
                
                with st.spinner("Processing image..."):
                    result = orchestrator.ingest_record(request)
                    
                    if result.get("success"):
                        st.success(f"✅ {result.get('message')}")
                    else:
                        st.error(f"❌ {result.get('error')}")

else:  # Settings page
    st.markdown("## ⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["Memory Health", "Privacy & Ethics", "Advanced"])
    
    with tab1:
        st.markdown("### Memory Health")
        
        if st.button("🔍 Analyze Memory Health"):
            with st.spinner("Analyzing..."):
                summary = orchestrator.get_memory_summary(patient_id)
                
                if summary.get("total_records", 0) > 0:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Records", summary.get("total_records", 0))
                    with col2:
                        st.metric(
                            "Memory Span (days)",
                            summary.get("date_range", {}).get("span_days", 0)
                        )
                    with col3:
                        memory_health = summary.get("memory_health", {})
                        st.metric(
                            "Health Score",
                            f"{memory_health.get('score', 0):.0%}"
                        )
                    
                    st.markdown("#### Record Types")
                    st.json(summary.get("record_types", {}))
                    
                    if memory_health.get("recommendations"):
                        st.markdown("#### Recommendations")
                        for rec in memory_health["recommendations"]:
                            st.info(rec)
                else:
                    st.info("No records found. Start uploading to build your medical memory!")
        
        if st.button("🔧 Apply Memory Maintenance"):
            with st.spinner("Applying maintenance..."):
                result = orchestrator.apply_memory_maintenance(patient_id)
                if result.get("success"):
                    st.success("✅ Memory maintenance completed")
    
    with tab2:
        st.markdown("### Privacy & Ethics")
        
        with st.expander("📜 Informed Consent"):
            st.markdown(orchestrator.get_consent_notice())
        
        with st.expander("🔒 Data Usage Policy"):
            st.markdown(orchestrator.get_data_usage_policy())
        
        st.markdown("---")
        st.markdown("#### Data Control")
        
        if st.button("🗑️ Clear All Data (Demo)", type="secondary"):
            st.warning("This would delete all your medical records (not implemented in demo)")
    
    with tab3:
        st.markdown("### Advanced Features")
        
        st.markdown("#### Symptom Progression Analysis")
        
        symptom_input = st.text_input("Enter a symptom to analyze")
        time_window = st.slider("Time window (days)", 30, 730, 365)
        
        if st.button("Analyze Symptom Progression"):
            if symptom_input:
                with st.spinner("Analyzing..."):
                    result = orchestrator.analyze_symptom_progression(
                        patient_id=patient_id,
                        symptom=symptom_input,
                        time_window_days=time_window
                    )
                    
                    if result.get("success"):
                        if result.get("occurrences", 0) > 0:
                            st.success(f"Found {result['occurrences']} occurrences")
                            st.json(result)
                        else:
                            st.info(result.get("message", "No data found"))
                    else:
                        st.error(result.get("error"))
            else:
                st.warning("Please enter a symptom")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>CareLedger v1.0 | AI-Powered Medical Memory System</p>
    <p>⚕️ This is decision support only, not medical diagnosis. Always consult healthcare professionals.</p>
</div>
""", unsafe_allow_html=True)
