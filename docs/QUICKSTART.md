# CareLedger Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.9 or higher
- 4GB RAM minimum
- Internet connection (for Gemini API)

### Step 1: Installation

```bash
# Clone the repository
git clone <repository-url>
cd careledger

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Get your Gemini API key:
   - Visit: https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key

3. Edit `.env` and add your key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### Step 3: Create Demo Data

```bash
python demo.py
```

This will:
- Initialize the system
- Create a demo patient with realistic medical history
- Show you sample queries to try

### Step 4: Launch the App

Choose one:

**Option A: Streamlit UI (Recommended for first-time users)**
```bash
streamlit run app.py
```
Then open: http://localhost:8501

**Option B: FastAPI Backend**
```bash
python api.py
```
Then access: http://localhost:8000/docs

## 📱 Using the Streamlit Interface

### Home Page - Query Your History

1. Enter your patient ID (default: `demo_patient_001`)
2. Type a query in the text area:
   - "What treatments helped my headaches?"
   - "Do I have any allergies?"
   - "What should I ask my doctor about recurring symptoms?"
3. Click "Search Medical History"
4. View results:
   - Similar past cases
   - Forgotten insights
   - Recommendations

### Timeline Page - View Your History

1. Navigate to "📊 Timeline" from sidebar
2. Click "Load Timeline"
3. See all your medical records in chronological order

### Upload Records Page - Add New Data

Three tabs for different types:

**Text/Symptoms Tab:**
1. Select record type (symptom, doctor_note, etc.)
2. Enter content
3. Add symptoms and diagnosis (optional)
4. Click "Save Text Record"

**PDF Report Tab:**
1. Upload a PDF file
2. Select report type
3. Click "Upload PDF"

**Medical Image Tab:**
1. Upload an image (X-ray, scan, etc.)
2. Enter scan type and body part
3. Click "Upload Image"

### Settings Page - Manage Your Data

**Memory Health:**
- View memory statistics
- Check health score
- Apply maintenance

**Privacy & Ethics:**
- Read informed consent
- Review data usage policy

**Advanced:**
- Analyze symptom progression
- Track patterns over time

## 🧪 Try These Examples

### Example 1: Query Past Treatments

```
Query: "What treatments have helped my headaches in the past?"

Expected Results:
- Similar past headache episodes
- Medications that worked (Sumatriptan, Magnesium)
- Questions to ask doctor about current symptoms
```

### Example 2: Check for Allergies

```
Query: "Do I have any allergies I should be aware of?"

Expected Results:
- Allergy test results from past
- List of known allergies (grass pollen, dust mites, cat dander)
- Recommendations for managing allergies
```

### Example 3: Medication Review

```
Query: "What medications am I currently taking and why?"

Expected Results:
- Current prescriptions
- Purpose of each medication
- When they were prescribed
```

### Example 4: Pattern Analysis

```
Query: "Show me if my migraines have a pattern"

Expected Results:
- Frequency over time
- Common triggers (stress, weather)
- Effectiveness of treatments
```

## 🔧 Using the API

### Health Check

```bash
curl http://localhost:8000/health
```

### Query Medical History

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "demo_patient_001",
    "query_text": "What treatments helped my headaches?"
  }'
```

### Upload Text Record

```bash
curl -X POST http://localhost:8000/ingest/text \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "demo_patient_001",
    "record_type": "symptom",
    "content": "Experiencing mild headache today",
    "metadata": {
      "symptoms": ["headache"]
    }
  }'
```

### Get Timeline

```bash
curl http://localhost:8000/patient/demo_patient_001/timeline
```

### Get Memory Summary

```bash
curl http://localhost:8000/patient/demo_patient_001/memory-summary
```

## 🐛 Troubleshooting

### Issue: "GEMINI_API_KEY not set"

**Solution:**
1. Make sure you created the `.env` file
2. Add your API key: `GEMINI_API_KEY=your_key_here`
3. Restart the application

### Issue: "Module not found" errors

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Port already in use

**Solution:**
```bash
# For Streamlit (default port 8501)
streamlit run app.py --server.port 8502

# For FastAPI (default port 8000)
uvicorn api:app --port 8001
```

### Issue: Slow responses

**Causes:**
- First query initializes models (can take 10-30 seconds)
- Gemini API rate limits
- Large PDF processing

**Solutions:**
- Wait for initialization to complete
- Subsequent queries are faster
- Reduce PDF size or number of pages

### Issue: No similar cases found

**Causes:**
- New patient with no history
- Query not matching existing records
- Need to adjust similarity threshold

**Solutions:**
1. Add more medical records
2. Try different query phrasing
3. Check patient ID is correct

## 📚 Next Steps

### For Patients

1. **Add Your Real Data:**
   - Upload your medical reports (PDFs)
   - Record your symptoms daily
   - Add prescriptions and test results

2. **Use Before Doctor Visits:**
   - Query your history
   - Generate questions to ask
   - Bring list to appointment

3. **Track Patterns:**
   - Regular symptom logging
   - Medication effectiveness
   - Trigger identification

### For Developers

1. **Customize Agents:**
   - Modify agent logic in `agents/` directory
   - Adjust similarity thresholds
   - Add new recommendation types

2. **Extend Features:**
   - Add new record types
   - Implement family accounts
   - Integrate with EHR systems

3. **Deploy to Production:**
   - Set up Qdrant server (not in-memory)
   - Add authentication
   - Implement HTTPS
   - Configure monitoring

## 🎓 Learn More

- **Architecture**: See `docs/ARCHITECTURE.md`
- **API Reference**: Visit http://localhost:8000/docs
- **Code Examples**: Check `demo.py`

## ⚠️ Important Reminders

1. **This is NOT medical advice** - Always consult healthcare professionals
2. **For emergencies** - Call emergency services immediately
3. **Privacy** - Keep your API keys secure
4. **Backups** - Maintain copies of original medical records
5. **Demo Data** - The demo patient is fictional for testing

## 💬 Get Help

- Check documentation in `docs/` folder
- Review error logs
- Create an issue on GitHub
- Email: support@careledger.example.com

---

**Ready to improve your medical memory?** Start with the demo data and explore! 🚀
