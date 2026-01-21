"""
Demo Script for CareLedger
Populates the system with sample medical data for demonstration
"""
from orchestrator import orchestrator
from models.schemas import IngestionRequest, RecordType, Modality
from datetime import datetime, timedelta
import random

def create_sample_patient_data(patient_id: str = "demo_patient_001"):
    """Create sample medical history for demonstration"""
    
    print(f"🏥 Creating sample data for patient: {patient_id}")
    print("=" * 60)
    
    orchestrator.initialize()
    
    # Sample data timeline
    sample_records = []
    
    # 2 years ago - Initial consultation
    date_2y = datetime.now() - timedelta(days=730)
    sample_records.append({
        "record_type": RecordType.DOCTOR_NOTE,
        "content": "Patient presented with recurring migraine headaches, approximately 2-3 times per month. Reports sensitivity to light and nausea during episodes. Family history of migraines (mother). Recommended keeping headache diary and prescribed Sumatriptan 50mg as needed. IMPORTANT: Patient mentioned occasional neck stiffness - suggested physical therapy evaluation but patient declined at the time due to schedule constraints.",
        "metadata": {
            "date": date_2y,
            "diagnosis": "Migraine headaches",
            "symptoms": ["headache", "nausea", "photophobia", "neck stiffness"],
            "medications": ["Sumatriptan 50mg"],
            "unfollowed_recommendation": "physical therapy for neck stiffness"
        }
    })
    
    # 18 months ago - Follow-up
    date_18m = datetime.now() - timedelta(days=547)
    sample_records.append({
        "record_type": RecordType.SYMPTOM,
        "content": "Severe migraine attack lasting 6 hours. Triggered by stress and lack of sleep. Took Sumatriptan which provided relief within 2 hours. Also experienced visual aura before onset.",
        "metadata": {
            "date": date_18m,
            "symptoms": ["migraine", "aura", "nausea"],
            "triggers": ["stress", "sleep deprivation"]
        }
    })
    
    # 1 year ago - Blood test
    date_1y = datetime.now() - timedelta(days=365)
    sample_records.append({
        "record_type": RecordType.REPORT,
        "content": "Complete Blood Count (CBC) - All values within normal range. Hemoglobin: 14.2 g/dL, WBC: 7,500/μL, Platelets: 250,000/μL. Vitamin D: 18 ng/mL (low - recommend supplementation). Thyroid function (TSH): 2.1 mIU/L (normal).",
        "metadata": {
            "date": date_1y,
            "test_type": "blood_test",
            "findings": ["low vitamin D"],
            "recommendations": ["vitamin D supplementation"]
        }
    })
    
    # 9 months ago - Prescription update
    date_9m = datetime.now() - timedelta(days=274)
    sample_records.append({
        "record_type": RecordType.PRESCRIPTION,
        "content": "Updated prescription: Sumatriptan 100mg (increased dose) as needed for migraine attacks. Added Vitamin D3 2000 IU daily supplement. Recommended magnesium supplementation as migraine prevention (400mg daily).",
        "metadata": {
            "date": date_9m,
            "medications": ["Sumatriptan 100mg", "Vitamin D3 2000 IU", "Magnesium 400mg"],
            "purpose": "migraine management and vitamin D deficiency"
        }
    })
    
    # 6 months ago - Symptom report
    date_6m = datetime.now() - timedelta(days=183)
    sample_records.append({
        "record_type": RecordType.SYMPTOM,
        "content": "Migraine frequency reduced to 1-2 per month since starting magnesium supplement. Episodes seem less severe. Still triggered by stress and weather changes. Vitamin D levels being monitored.",
        "metadata": {
            "date": date_6m,
            "symptoms": ["migraine"],
            "improvement": "frequency reduced",
            "triggers": ["stress", "weather"]
        }
    })
    
    # 3 months ago - Allergy test
    date_3m = datetime.now() - timedelta(days=91)
    sample_records.append({
        "record_type": RecordType.REPORT,
        "content": "Allergy panel testing results: Positive reactions to grass pollen (moderate), dust mites (mild), cat dander (mild). No food allergies detected. Recommend antihistamines during high pollen season and environmental controls for dust/dander.",
        "metadata": {
            "date": date_3m,
            "test_type": "allergy_panel",
            "allergies": ["grass pollen", "dust mites", "cat dander"],
            "severity": {"grass pollen": "moderate", "dust mites": "mild", "cat dander": "mild"}
        }
    })
    
    # 1 month ago - Recent symptom
    date_1m = datetime.now() - timedelta(days=30)
    sample_records.append({
        "record_type": RecordType.SYMPTOM,
        "content": "Experiencing seasonal allergy symptoms - sneezing, runny nose, itchy eyes. Seems to coincide with high pollen count days. Taking over-the-counter antihistamine (Cetirizine 10mg) with good relief.",
        "metadata": {
            "date": date_1m,
            "symptoms": ["sneezing", "runny nose", "itchy eyes"],
            "condition": "seasonal allergies",
            "medications": ["Cetirizine 10mg"]
        }
    })
    
    # 1 week ago - Current issue
    date_1w = datetime.now() - timedelta(days=7)
    sample_records.append({
        "record_type": RecordType.SYMPTOM,
        "content": "Mild headache for the past 3 days. Different from usual migraines - more tension-type, located at back of head and neck. Possibly related to increased screen time while working from home. No nausea or light sensitivity.",
        "metadata": {
            "date": date_1w,
            "symptoms": ["tension headache", "neck pain"],
            "triggers": ["screen time", "posture"],
            "different_from": "usual migraines"
        }
    })
    
    # Ingest all records
    success_count = 0
    failed_count = 0
    
    for record_data in sample_records:
        request = IngestionRequest(
            patient_id=patient_id,
            record_type=record_data["record_type"],
            modality=Modality.TEXT,
            content=record_data["content"],
            metadata=record_data["metadata"]
        )
        
        result = orchestrator.ingest_record(request)
        
        if result.get("success"):
            success_count += 1
            print(f"✅ Ingested: {record_data['record_type'].value} from {record_data['metadata']['date'].strftime('%Y-%m-%d')}")
        else:
            failed_count += 1
            print(f"❌ Failed: {record_data['record_type'].value} - {result.get('error')}")
    
    print("=" * 60)
    print(f"✨ Demo data creation complete!")
    print(f"   Success: {success_count}")
    print(f"   Failed: {failed_count}")
    print(f"   Total: {len(sample_records)}")
    print()
    print("="*70)
    print("🧠 MEMORY EVOLUTION DEMONSTRATION")
    print("="*70)
    print()
    print("Watch as memories strengthen through repeated access!")
    print("Try querying the same thing multiple times to see memory weights increase.")
    print()
    print("🎯 Try these sample queries to see CareLedger in action:")
    print()
    print("   1. 'What treatments have helped my headaches in the past?'")
    print("      → Will find multiple similar episodes and show progression")
    print()
    print("   2. 'I'm having neck pain with my headaches. Has this happened before?'")
    print("      → 🌟 WOW MOMENT: Will surface the FORGOTTEN INSIGHT from 2 years ago!")
    print("      → Shows neck stiffness was mentioned but physical therapy was never followed up")
    print("      → ⚠️ EXPLICIT MESSAGE: 'Neck stiffness reported 24 months ago with")
    print("         recommendation for physical therapy that was declined'")
    print()
    print("   3. Run the SAME query TWICE to see memory reinforcement:")
    print("      → First query: memory_weight = 1.000")
    print("      → Second query: memory_weight = 1.050 → 1.100")
    print("      → Third query: memory_weight = 1.100 → 1.300 (LEVEL UP to reinforcement_level 1)")
    print("      → 💡 This is EXPLICIT MEMORY EVOLUTION - visible in real-time!")
    print()
    print("   4. 'Do I have any allergies I should be aware of?'")
    print("      → Retrieves allergy panel results and provides specific recommendations")
    print()
    print("   5. 'What medications am I currently taking?'")
    print("      → Finds most recent prescription records")
    print()
    print("   6. 'Show me my headache pattern over the last year'")
    print("      → Demonstrates temporal analysis and pattern recognition")
    print()
    print("="*70)
    print("📊 MEMORY EVOLUTION METRICS TO WATCH FOR:")
    print("="*70)
    print()
    print("Look for these in the console output:")
    print("  • 'Memory weight: 1.000 → 1.050 (+0.050)' - Small reinforcement")
    print("  • 'Memory weight: 1.100 → 1.300 (+0.200)' - Large reinforcement")
    print("  • '✨ LEVEL UP: None → Low' - Reinforcement threshold reached")
    print("  • 'Access count: 2 → 3 (+1)' - How many times retrieved")
    print("  • 'Reinforcement level: 0 → 1' - Importance level increased")
    print()
    print("This is the KEY DIFFERENTIATOR - memories that adapt over time!")
    print()

def test_sample_queries(patient_id: str = "demo_patient_001"):
    """Test the system with sample queries"""
    
    from models.schemas import PatientQuery
    
    print("🔍 Testing sample queries...")
    print("=" * 60)
    
    queries = [
        "What treatments have helped my headaches in the past?",
        "Do I have any allergies?",
        "What medications am I currently taking?"
    ]
    
    for i, query_text in enumerate(queries, 1):
        print(f"\nQuery {i}: {query_text}")
        print("-" * 60)
        
        query = PatientQuery(
            patient_id=patient_id,
            query_text=query_text
        )
        
        result = orchestrator.process_query(query)
        
        print(f"Similar cases found: {len(result.similar_cases)}")
        
        if result.similar_cases:
            print("\nTop similar case:")
            top_case = result.similar_cases[0]
            print(f"  Date: {top_case.date.strftime('%Y-%m-%d')}")
            print(f"  Type: {top_case.record_type}")
            print(f"  Similarity: {top_case.similarity_score:.0%}")
            print(f"  Content: {top_case.content[:100]}...")
        
        if result.recommendations:
            print(f"\nRecommendations ({len(result.recommendations)}):")
            for rec in result.recommendations[:3]:
                print(f"  • {rec}")
        
        print()
    
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    # Allow custom patient ID
    patient_id = sys.argv[1] if len(sys.argv) > 1 else "demo_patient_001"
    
    # Create sample data
    create_sample_patient_data(patient_id)
    
    # Test queries
    response = input("\nWould you like to test sample queries? (y/n): ")
    if response.lower() == 'y':
        test_sample_queries(patient_id)
    
    print("\n✅ Demo complete! You can now:")
    print("   • Run the Streamlit app: streamlit run app.py")
    print("   • Start the API: python api.py")
    print(f"   • Use patient ID: {patient_id}")
