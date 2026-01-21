# CareLedger Deployment Guide

## Overview

This guide covers deploying CareLedger in various environments, from local development to production.

## Deployment Options

### Option 1: Local Development

**Best for**: Testing, development, demos

**Setup:**
```bash
# 1. Clone and install
git clone <repo>
cd careledger
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your GEMINI_API_KEY

# 3. Create demo data
python demo.py

# 4. Run
streamlit run app.py
```

**Pros:**
- Quick setup
- No infrastructure needed
- Easy debugging

**Cons:**
- Data stored in-memory only
- Single user
- No persistence across restarts

---

### Option 2: Docker Local

**Best for**: Consistent environment, easy sharing

**Setup:**
```bash
# 1. Build image
docker build -t careledger:latest .

# 2. Run Streamlit UI
docker run -p 8501:8501 \
  -e GEMINI_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  careledger:latest

# 3. Or run API
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  careledger:latest \
  uvicorn api:app --host 0.0.0.0 --port 8000
```

**Docker Compose:**
```bash
# Set environment variable
export GEMINI_API_KEY=your_key

# Start all services
docker-compose up -d

# Access:
# - Streamlit: http://localhost:8501
# - API: http://localhost:8000
```

**Pros:**
- Consistent environment
- Easy deployment
- Can run both UI and API

**Cons:**
- Still in-memory storage
- Need Docker knowledge

---

### Option 3: Production with Qdrant Server

**Best for**: Real usage, multiple patients, persistence

**Architecture:**
```
┌─────────────┐     ┌─────────────┐
│  Streamlit  │────▶│  FastAPI    │
│     UI      │     │   Backend   │
└─────────────┘     └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Qdrant    │
                    │   Server    │
                    └─────────────┘
```

**Step 1: Deploy Qdrant Server**

```bash
# Using Docker
docker run -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Or using docker-compose
cat > docker-compose.qdrant.yml << EOF
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage
volumes:
  qdrant_storage:
EOF

docker-compose -f docker-compose.qdrant.yml up -d
```

**Step 2: Update Configuration**

Edit `config.py`:
```python
# Change from in-memory to server
self.client = QdrantClient(
    host=settings.QDRANT_HOST,  # e.g., "localhost" or "qdrant.example.com"
    port=settings.QDRANT_PORT,  # 6333
    api_key=settings.QDRANT_API_KEY  # If auth enabled
)
```

**Step 3: Deploy Application**

```bash
# Deploy API
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# Deploy Streamlit
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

**Pros:**
- Persistent storage
- Multi-user support
- Production-ready
- Can scale

**Cons:**
- More complex setup
- Requires infrastructure

---

### Option 4: Cloud Deployment (AWS)

**Architecture:**
```
┌──────────────┐
│   CloudFront │ (CDN)
└───────┬──────┘
        │
┌───────▼──────┐
│  ALB/NGINX   │ (Load Balancer)
└───────┬──────┘
        │
┌───────▼──────────────┐
│   ECS/EC2 Cluster    │
│  ┌────────────────┐  │
│  │  CareLedger    │  │
│  │  Containers    │  │
│  └────────────────┘  │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│   Qdrant (Managed    │
│   or Self-hosted)    │
└──────────────────────┘
```

**Step 1: Prepare Docker Image**

```bash
# Build and tag
docker build -t careledger:latest .
docker tag careledger:latest your-ecr-repo/careledger:latest

# Push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin your-ecr-repo
docker push your-ecr-repo/careledger:latest
```

**Step 2: Create ECS Task Definition**

```json
{
  "family": "careledger",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "careledger-api",
      "image": "your-ecr-repo/careledger:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "GEMINI_API_KEY",
          "value": "your-key"
        },
        {
          "name": "QDRANT_HOST",
          "value": "qdrant.internal"
        }
      ],
      "memory": 2048,
      "cpu": 1024
    }
  ]
}
```

**Step 3: Deploy Qdrant**

Option A: Use Qdrant Cloud
```bash
# Sign up at cloud.qdrant.io
# Get connection details
# Update environment variables
```

Option B: Self-hosted on EC2
```bash
# Launch EC2 instance
# Install Docker
# Run Qdrant container
docker run -d -p 6333:6333 \
  -v /data/qdrant:/qdrant/storage \
  qdrant/qdrant
```

**Step 4: Set up Load Balancer**

- Create Application Load Balancer
- Configure target groups
- Set up health checks
- Configure SSL/TLS

**Step 5: Set up CloudFront (Optional)**

- Create distribution
- Point to ALB
- Configure caching
- Add WAF rules

**Pros:**
- Highly scalable
- Managed services
- Auto-scaling
- High availability

**Cons:**
- More expensive
- Complex setup
- Requires AWS knowledge

---

### Option 5: Kubernetes Deployment

**Best for**: Large scale, multi-tenant

**Prerequisites:**
- Kubernetes cluster (EKS, GKE, or self-hosted)
- kubectl configured
- Helm (optional)

**Step 1: Create Deployments**

`deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: careledger-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: careledger-api
  template:
    metadata:
      labels:
        app: careledger-api
    spec:
      containers:
      - name: api
        image: your-registry/careledger:latest
        ports:
        - containerPort: 8000
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: careledger-secrets
              key: gemini-api-key
        - name: QDRANT_HOST
          value: qdrant-service
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: careledger-api-service
spec:
  selector:
    app: careledger-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Step 2: Deploy Qdrant**

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: qdrant
spec:
  serviceName: qdrant
  replicas: 1
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:
      - name: qdrant
        image: qdrant/qdrant:latest
        ports:
        - containerPort: 6333
        volumeMounts:
        - name: qdrant-storage
          mountPath: /qdrant/storage
  volumeClaimTemplates:
  - metadata:
      name: qdrant-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 50Gi
```

**Step 3: Apply**

```bash
# Create secrets
kubectl create secret generic careledger-secrets \
  --from-literal=gemini-api-key=your_key

# Deploy
kubectl apply -f deployment.yaml

# Check status
kubectl get pods
kubectl get services
```

---

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| GEMINI_API_KEY | Google Gemini API key | Yes | - |
| QDRANT_HOST | Qdrant server host | No | localhost |
| QDRANT_PORT | Qdrant server port | No | 6333 |
| QDRANT_API_KEY | Qdrant API key (if auth enabled) | No | - |
| DEBUG | Enable debug mode | No | True |

## Security Checklist

### Development
- [x] Use .env for secrets
- [x] Don't commit API keys
- [x] Use HTTPS locally (optional)

### Production
- [ ] Enable HTTPS/TLS
- [ ] Set up authentication
- [ ] Enable Qdrant API key
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable logging
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Use secrets management (AWS Secrets Manager, etc.)
- [ ] Enable WAF
- [ ] Set up DDoS protection

## Backup & Recovery

### Backup Qdrant Data

```bash
# Using Docker volume
docker run --rm -v qdrant_storage:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/qdrant-backup-$(date +%Y%m%d).tar.gz /data

# Or using Qdrant snapshot API
curl -X POST http://localhost:6333/collections/patient_memory/snapshots
```

### Restore

```bash
# Extract backup
tar xzf qdrant-backup-20260115.tar.gz -C /path/to/qdrant/storage

# Or use Qdrant restore API
curl -X PUT http://localhost:6333/collections/patient_memory/snapshots/upload \
  -F 'snapshot=@snapshot.dat'
```

## Monitoring

### Metrics to Monitor

1. **Application Metrics**:
   - Request rate
   - Response time
   - Error rate
   - Queue length

2. **Infrastructure Metrics**:
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network I/O

3. **Business Metrics**:
   - Active patients
   - Queries per patient
   - Ingestion rate
   - Storage growth

### Tools

- **Prometheus + Grafana**: For metrics
- **ELK Stack**: For logs
- **CloudWatch**: For AWS
- **Datadog**: All-in-one

### Sample Prometheus Config

```yaml
scrape_configs:
  - job_name: 'careledger'
    static_configs:
      - targets: ['careledger-api:8000']
    metrics_path: '/metrics'
```

## Scaling

### Horizontal Scaling

```bash
# Kubernetes
kubectl scale deployment careledger-api --replicas=5

# Docker Compose
docker-compose up -d --scale api=5
```

### Vertical Scaling

- Increase container resources
- Upgrade instance types
- Add GPUs for embeddings

### Database Scaling

- Qdrant clustering (enterprise)
- Read replicas
- Sharding by patient_id

## Cost Optimization

### Development
- Use in-memory Qdrant
- Free tier Gemini API
- Local deployment

### Production
- Use reserved instances
- Implement caching
- Optimize embedding models
- Batch processing
- Auto-scaling

## Troubleshooting

### Logs

```bash
# Docker
docker logs careledger-api

# Kubernetes
kubectl logs -f deployment/careledger-api

# View all logs
kubectl logs -l app=careledger-api --all-containers=true
```

### Common Issues

1. **Qdrant connection failed**
   - Check QDRANT_HOST and PORT
   - Verify network connectivity
   - Check firewall rules

2. **Out of memory**
   - Increase container memory
   - Reduce batch sizes
   - Enable pagination

3. **Slow queries**
   - Check Qdrant indices
   - Enable caching
   - Optimize embedding generation

---

**Ready to deploy?** Start with local development, then progress to production as needed.
