# 🚀 DEPLOYMENT GUIDE
## Healthcare-AI-Quantum-System - Production Deployment

**Version:** 1.0.0
**Last Updated:** December 23, 2025

---

## TABLE OF CONTENTS

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Docker Deployment](#docker-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Cloud Deployments](#cloud-deployments)
7. [Monitoring & Observability](#monitoring--observability)
8. [Backup & Disaster Recovery](#backup--disaster-recovery)
9. [Security Hardening](#security-hardening)
10. [Troubleshooting](#troubleshooting)

---

## PRE-DEPLOYMENT CHECKLIST

### Required Credentials

- [ ] OpenAI API Key (for GPT-4o)
- [ ] Anthropic API Key (for Claude Opus)
- [ ] IBM Quantum Token (for QAOA)
- [ ] FHIR Server Credentials (Epic, Cerner, etc.)
- [ ] SSL/TLS Certificates
- [ ] Database passwords (strong, rotated)
- [ ] JWT Secret Key (min 32 chars, cryptographically random)

### Infrastructure Requirements

**Minimum (Development/Testing):**
- [ ] CPU: 8 cores
- [ ] RAM: 16 GB
- [ ] Disk: 100 GB SSD
- [ ] Network: 100 Mbps

**Recommended (Production):**
- [ ] CPU: 16+ cores (with hyperthreading)
- [ ] RAM: 32+ GB (ECC recommended)
- [ ] Disk: 500 GB SSD NVMe (RAID 10)
- [ ] Network: 1 Gbps+ (redundant)
- [ ] GPU: NVIDIA T4 or better (optional, for inference)

### Compliance Verification

- [ ] HIPAA Security Risk Assessment completed
- [ ] KVKK Data Protection Impact Assessment
- [ ] Business Associate Agreements signed
- [ ] Data Processing Agreements in place
- [ ] Incident Response Plan documented
- [ ] Disaster Recovery Plan tested
- [ ] Security Audit completed
- [ ] Penetration Testing performed

### Software Requirements

```bash
# Required software
- Python 3.11 or higher
- Docker 24.0+ and Docker Compose 2.0+
- PostgreSQL 15+
- MongoDB 7+
- Redis 7+
- Apache Kafka 3.6+

# Optional but recommended
- Kubernetes 1.28+ (for production)
- Nginx or Traefik (reverse proxy)
- Prometheus + Grafana (monitoring)
- ELK Stack (centralized logging)
```

---

## ENVIRONMENT SETUP

### 1. Clone and Configure

```bash
# Clone repository
cd /Users/sardag/Desktop
cd HealthCare-AI-Quantum-System

# Create environment file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` with production values:

```bash
# ============ CRITICAL: PRODUCTION SETTINGS ============

# Application
APP_ENV=production  # MUST be 'production'
SECRET_KEY=$(openssl rand -hex 32)  # Generate strong key

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=8  # CPU cores * 2
API_RELOAD=false  # MUST be false in production

# Database - Use strong passwords
POSTGRES_USER=healthcare_admin
POSTGRES_PASSWORD=$(openssl rand -base64 24)  # Strong password
POSTGRES_HOST=postgres  # Or external DB host
POSTGRES_PORT=5432
POSTGRES_DB=healthcare_ai

# MongoDB
MONGODB_URL=mongodb://admin:STRONG_PASSWORD@mongodb:27017/healthcare_ai?authSource=admin

# Redis
REDIS_URL=redis://:STRONG_PASSWORD@redis:6379/0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# AI/ML - Add your API keys
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXX
ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXXXX
DEFAULT_LLM_PROVIDER=openai
DEFAULT_LLM_MODEL=gpt-4o

# Quantum
IBM_QUANTUM_TOKEN=YOUR_IBM_QUANTUM_TOKEN
ENABLE_QUANTUM_OPTIMIZATION=true
QUANTUM_BACKEND=ibm_brisbane  # or ibmq_qasm_simulator

# FHIR
FHIR_BASE_URL=https://fhir.your-hospital.com/api/FHIR/R4
FHIR_CLIENT_ID=your_client_id
FHIR_CLIENT_SECRET=your_client_secret

# Security
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# HIPAA/KVKK
HIPAA_MODE=true  # MUST be true
ENABLE_AUDIT_LOGGING=true  # MUST be true
LOG_RETENTION_DAYS=2555  # 7 years for HIPAA

# Feature Flags
ENABLE_CLINICAL_DECISION_AGENT=true
ENABLE_RESOURCE_OPTIMIZATION_AGENT=true
ENABLE_PATIENT_MONITORING_AGENT=true

# Monitoring
ENABLE_PROMETHEUS_METRICS=true
PROMETHEUS_PORT=9090
```

### 3. Generate Strong Secrets

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate database passwords
openssl rand -base64 24

# Generate JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## DATABASE SETUP

### Option 1: Docker Databases (Development)

```bash
# Start databases
docker-compose up -d postgres mongodb redis kafka

# Wait for services to be ready
sleep 30

# Verify databases are running
docker-compose ps
```

### Option 2: External Databases (Production)

**PostgreSQL:**
```bash
# Connect to your PostgreSQL server
psql -h your-db-host -U postgres

# Create database and user
CREATE DATABASE healthcare_ai;
CREATE USER healthcare_admin WITH ENCRYPTED PASSWORD 'STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE healthcare_ai TO healthcare_admin;

# Enable required extensions
\c healthcare_ai
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  # For full-text search
```

**MongoDB:**
```bash
# Connect to MongoDB
mongosh --host your-mongo-host

# Create database and user
use healthcare_ai
db.createUser({
  user: "healthcare_admin",
  pwd: "STRONG_PASSWORD",
  roles: [
    { role: "readWrite", db: "healthcare_ai" },
    { role: "dbAdmin", db: "healthcare_ai" }
  ]
})
```

**Redis:**
```bash
# Edit redis.conf
requirepass STRONG_PASSWORD
maxmemory 2gb
maxmemory-policy allkeys-lru

# Restart Redis
systemctl restart redis
```

**Kafka:**
```bash
# Create required topics
kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic vital-signs \
  --partitions 10 \
  --replication-factor 3

kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic alerts \
  --partitions 5 \
  --replication-factor 3
```

### 4. Run Database Migrations

```bash
# Install dependencies
pip install -r requirements.txt

# Run Alembic migrations
alembic upgrade head

# Verify migration
alembic current
```

### 5. Create Initial Admin User

```bash
# Run Python script to create admin
python3 << EOF
import asyncio
from core.database.connection import AsyncSessionLocal
from core.database.models import User
from core.security.auth import get_password_hash
from uuid import uuid4

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = User(
            user_id=uuid4(),
            username="admin",
            email="admin@hospital.com",
            hashed_password=get_password_hash("CHANGE_THIS_PASSWORD"),
            full_name="System Administrator",
            roles=["admin", "physician", "nurse"]
        )
        db.add(admin)
        await db.commit()
        print(f"✅ Admin user created: {admin.username}")

asyncio.run(create_admin())
EOF
```

---

## DOCKER DEPLOYMENT

### 1. Build Docker Image

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 healthcare && \
    chown -R healthcare:healthcare /app

USER healthcare

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "main.py"]
```

Build and run:

```bash
# Build image
docker build -t healthcare-ai:1.0.0 .

# Run container
docker run -d \
  --name healthcare-api \
  --env-file .env \
  -p 8000:8000 \
  --restart unless-stopped \
  healthcare-ai:1.0.0

# Check logs
docker logs -f healthcare-api
```

### 2. Docker Compose (Full Stack)

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### 3. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    image: healthcare-ai:1.0.0
    container_name: healthcare-api
    restart: always
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - mongodb
      - redis
      - kafka
    networks:
      - healthcare-network
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - healthcare-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  mongodb:
    image: mongo:7
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_PASSWORD}
    volumes:
      - mongodb_data:/data/db
    networks:
      - healthcare-network

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 2gb
    volumes:
      - redis_data:/data
    networks:
      - healthcare-network

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    restart: always
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    volumes:
      - kafka_data:/var/lib/kafka/data
    networks:
      - healthcare-network

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    restart: always
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    volumes:
      - zookeeper_data:/var/lib/zookeeper
    networks:
      - healthcare-network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    networks:
      - healthcare-network

volumes:
  postgres_data:
  mongodb_data:
  redis_data:
  kafka_data:
  zookeeper_data:

networks:
  healthcare-network:
    driver: bridge
```

Run production stack:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## KUBERNETES DEPLOYMENT

### 1. Create Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: healthcare-ai
  labels:
    name: healthcare-ai
    environment: production
```

```bash
kubectl apply -f k8s/namespace.yaml
```

### 2. Create Secrets

```bash
# Create secret from .env file
kubectl create secret generic healthcare-secrets \
  --from-env-file=.env \
  --namespace=healthcare-ai

# Create TLS secret for HTTPS
kubectl create secret tls healthcare-tls \
  --cert=ssl/certificate.crt \
  --key=ssl/private.key \
  --namespace=healthcare-ai
```

### 3. Deploy PostgreSQL

```yaml
# k8s/postgres-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: healthcare-ai
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: healthcare-secrets
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: healthcare-secrets
              key: POSTGRES_PASSWORD
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: healthcare-secrets
              key: POSTGRES_DB
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 50Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: healthcare-ai
spec:
  ports:
  - port: 5432
  clusterIP: None
  selector:
    app: postgres
```

```bash
kubectl apply -f k8s/postgres-deployment.yaml
```

### 4. Deploy Application

```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: healthcare-api
  namespace: healthcare-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: healthcare-api
  template:
    metadata:
      labels:
        app: healthcare-api
    spec:
      containers:
      - name: api
        image: healthcare-ai:1.0.0
        ports:
        - containerPort: 8000
          name: http
        envFrom:
        - secretRef:
            name: healthcare-secrets
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 20
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: healthcare-api-service
  namespace: healthcare-ai
spec:
  selector:
    app: healthcare-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

```bash
kubectl apply -f k8s/api-deployment.yaml
```

### 5. Create Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: healthcare-ingress
  namespace: healthcare-ai
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.healthcare-ai.com
    secretName: healthcare-tls
  rules:
  - host: api.healthcare-ai.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: healthcare-api-service
            port:
              number: 80
```

```bash
kubectl apply -f k8s/ingress.yaml
```

### 6. Deploy Monitoring

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus + Grafana
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace healthcare-ai \
  --set grafana.adminPassword=STRONG_PASSWORD
```

### 7. Verify Deployment

```bash
# Check pods
kubectl get pods -n healthcare-ai

# Check services
kubectl get svc -n healthcare-ai

# Check ingress
kubectl get ingress -n healthcare-ai

# View logs
kubectl logs -f deployment/healthcare-api -n healthcare-ai

# Execute commands in pod
kubectl exec -it deployment/healthcare-api -n healthcare-ai -- /bin/bash
```

---

## CLOUD DEPLOYMENTS

### AWS Deployment

**1. ECS Fargate:**

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name healthcare-ai

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster healthcare-ai \
  --service-name api \
  --task-definition healthcare-api:1 \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}"
```

**2. Infrastructure (RDS + DocumentDB + ElastiCache + MSK):**

```bash
# RDS PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier healthcare-postgres \
  --db-instance-class db.r6g.xlarge \
  --engine postgres \
  --engine-version 15.4 \
  --master-username admin \
  --master-user-password STRONG_PASSWORD \
  --allocated-storage 100 \
  --storage-encrypted

# DocumentDB (MongoDB-compatible)
aws docdb create-db-cluster \
  --db-cluster-identifier healthcare-docdb \
  --engine docdb \
  --master-username admin \
  --master-user-password STRONG_PASSWORD

# ElastiCache Redis
aws elasticache create-cache-cluster \
  --cache-cluster-id healthcare-redis \
  --cache-node-type cache.r6g.large \
  --engine redis \
  --num-cache-nodes 1

# MSK (Kafka)
aws kafka create-cluster \
  --cluster-name healthcare-kafka \
  --broker-node-group-info file://broker-info.json \
  --kafka-version 3.6.0
```

### Google Cloud Deployment

**1. GKE Cluster:**

```bash
# Create GKE cluster
gcloud container clusters create healthcare-cluster \
  --num-nodes=3 \
  --machine-type=n2-standard-4 \
  --region=us-central1 \
  --enable-autoscaling \
  --min-nodes=3 \
  --max-nodes=10

# Get credentials
gcloud container clusters get-credentials healthcare-cluster --region=us-central1

# Deploy application
kubectl apply -f k8s/
```

**2. Managed Services:**

```bash
# Cloud SQL (PostgreSQL)
gcloud sql instances create healthcare-postgres \
  --database-version=POSTGRES_15 \
  --tier=db-n1-standard-4 \
  --region=us-central1

# Firestore (MongoDB alternative)
gcloud firestore databases create --location=us-central1

# Memorystore (Redis)
gcloud redis instances create healthcare-redis \
  --size=5 \
  --region=us-central1

# Pub/Sub (Kafka alternative)
gcloud pubsub topics create vital-signs
gcloud pubsub topics create alerts
```

### Azure Deployment

**1. AKS Cluster:**

```bash
# Create resource group
az group create --name healthcare-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group healthcare-rg \
  --name healthcare-aks \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 10

# Get credentials
az aks get-credentials --resource-group healthcare-rg --name healthcare-aks

# Deploy
kubectl apply -f k8s/
```

**2. Managed Services:**

```bash
# Azure Database for PostgreSQL
az postgres server create \
  --resource-group healthcare-rg \
  --name healthcare-postgres \
  --location eastus \
  --admin-user admin \
  --admin-password STRONG_PASSWORD \
  --sku-name GP_Gen5_4

# Cosmos DB (MongoDB API)
az cosmosdb create \
  --name healthcare-cosmos \
  --resource-group healthcare-rg \
  --kind MongoDB

# Azure Cache for Redis
az redis create \
  --resource-group healthcare-rg \
  --name healthcare-redis \
  --location eastus \
  --sku Standard \
  --vm-size c1

# Event Hubs (Kafka alternative)
az eventhubs namespace create \
  --name healthcare-events \
  --resource-group healthcare-rg \
  --location eastus
```

---

## MONITORING & OBSERVABILITY

### 1. Prometheus Metrics

The application exposes Prometheus metrics at `/metrics`:

```python
# Metrics exposed:
- http_requests_total (counter)
- http_request_duration_seconds (histogram)
- agent_executions_total (counter)
- agent_execution_duration_seconds (histogram)
- database_connections_active (gauge)
- kafka_messages_processed_total (counter)
```

### 2. Grafana Dashboards

Import pre-built dashboards:

```bash
# Access Grafana
kubectl port-forward -n healthcare-ai svc/prometheus-grafana 3000:80

# Login: admin / STRONG_PASSWORD
# Import dashboards:
- 12345: FastAPI Overview
- 67890: PostgreSQL Stats
- 11223: Kafka Metrics
```

### 3. Application Logging

Logs are structured JSON and sent to stdout:

```json
{
  "timestamp": "2025-12-23T10:15:30Z",
  "level": "INFO",
  "module": "agents.clinical_decision",
  "message": "Diagnosis completed",
  "patient_id": "[REDACTED]",
  "confidence": 0.87,
  "execution_time_ms": 2340
}
```

**Centralized Logging (ELK Stack):**

```bash
# Deploy ELK
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch -n healthcare-ai
helm install kibana elastic/kibana -n healthcare-ai
helm install filebeat elastic/filebeat -n healthcare-ai
```

### 4. Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/db

# Agent health
curl http://localhost:8000/health/agents
```

### 5. Alerts

Configure Prometheus alerts:

```yaml
# prometheus-alerts.yaml
groups:
- name: healthcare-ai
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    annotations:
      summary: "High error rate detected"

  - alert: SlowAgentExecution
    expr: histogram_quantile(0.95, agent_execution_duration_seconds) > 10
    for: 5m
    annotations:
      summary: "Agent execution time > 10s"

  - alert: DatabaseConnectionPoolExhausted
    expr: database_connections_active > 90
    for: 2m
    annotations:
      summary: "Database connection pool nearly full"
```

---

## BACKUP & DISASTER RECOVERY

### 1. Database Backups

**PostgreSQL:**

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"

pg_dump -h localhost -U healthcare_admin healthcare_ai | \
  gzip > $BACKUP_DIR/healthcare_ai_$DATE.sql.gz

# Encrypt backup
gpg --encrypt --recipient admin@hospital.com \
  $BACKUP_DIR/healthcare_ai_$DATE.sql.gz

# Upload to S3
aws s3 cp $BACKUP_DIR/healthcare_ai_$DATE.sql.gz.gpg \
  s3://healthcare-backups/postgres/

# Keep last 30 days locally
find $BACKUP_DIR -name "*.gz.gpg" -mtime +30 -delete
```

**MongoDB:**

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mongodb"

mongodump --host localhost --db healthcare_ai \
  --out $BACKUP_DIR/healthcare_ai_$DATE

tar -czf $BACKUP_DIR/healthcare_ai_$DATE.tar.gz \
  $BACKUP_DIR/healthcare_ai_$DATE

# Encrypt and upload
gpg --encrypt --recipient admin@hospital.com \
  $BACKUP_DIR/healthcare_ai_$DATE.tar.gz

aws s3 cp $BACKUP_DIR/healthcare_ai_$DATE.tar.gz.gpg \
  s3://healthcare-backups/mongodb/
```

### 2. Automated Backup (Kubernetes CronJob)

```yaml
# k8s/backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: healthcare-ai
spec:
  schedule: "0 2 * * *"  # 2 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: healthcare-secrets
                  key: POSTGRES_PASSWORD
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h postgres -U healthcare_admin healthcare_ai | \
              gzip > /backups/healthcare_ai_$(date +%Y%m%d_%H%M%S).sql.gz
            volumeMounts:
            - name: backup-storage
              mountPath: /backups
          restartPolicy: OnFailure
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
```

### 3. Disaster Recovery Plan

**RTO (Recovery Time Objective):** 4 hours
**RPO (Recovery Point Objective):** 1 hour

**Recovery Steps:**

1. **Restore Databases:**
```bash
# PostgreSQL
gunzip < backup.sql.gz | psql -h localhost -U healthcare_admin healthcare_ai

# MongoDB
tar -xzf backup.tar.gz
mongorestore --host localhost --db healthcare_ai backup/healthcare_ai
```

2. **Redeploy Application:**
```bash
# Kubernetes
kubectl apply -f k8s/

# Docker
docker-compose -f docker-compose.prod.yml up -d
```

3. **Verify Services:**
```bash
# Health check
curl http://api.hospital.com/health

# Test authentication
curl -X POST http://api.hospital.com/token \
  -d "username=admin&password=PASSWORD"
```

---

## SECURITY HARDENING

### 1. Nginx Reverse Proxy

```nginx
# nginx.conf
upstream healthcare_api {
    server api:8000;
}

server {
    listen 80;
    server_name api.hospital.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.hospital.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # Proxy Settings
    location / {
        proxy_pass http://healthcare_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if any)
    location /static/ {
        alias /var/www/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 2. Firewall Rules

```bash
# UFW (Ubuntu)
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp  # SSH
ufw allow 80/tcp  # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable

# Allow only from specific IPs
ufw allow from 10.0.0.0/8 to any port 5432  # PostgreSQL
ufw allow from 10.0.0.0/8 to any port 27017  # MongoDB
```

### 3. Secret Management

Use external secret management:

```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name healthcare-ai/production/api-keys \
  --secret-string file://secrets.json

# HashiCorp Vault
vault kv put secret/healthcare-ai/production \
  openai_key="sk-..." \
  anthropic_key="sk-ant-..." \
  jwt_secret="..."

# Kubernetes External Secrets
kubectl apply -f external-secrets.yaml
```

### 4. Network Policies (Kubernetes)

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
  namespace: healthcare-ai
spec:
  podSelector:
    matchLabels:
      app: healthcare-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: mongodb
    ports:
    - protocol: TCP
      port: 27017
```

---

## TROUBLESHOOTING

### Common Issues

**1. Database Connection Errors:**

```bash
# Check database is running
docker ps | grep postgres

# Test connection
psql -h localhost -U healthcare_admin -d healthcare_ai

# Check logs
docker logs postgres

# Verify credentials in .env
echo $POSTGRES_PASSWORD
```

**2. Agent Execution Failures:**

```bash
# Check API keys are set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Test LLM connectivity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check agent logs
docker logs healthcare-api | grep "agents"
```

**3. Kafka Streaming Issues:**

```bash
# Check Kafka is running
docker ps | grep kafka

# List topics
kafka-topics.sh --list --bootstrap-server localhost:9092

# Check consumer lag
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group healthcare-monitoring --describe

# Restart Kafka consumer
docker-compose restart kafka
```

**4. High Memory Usage:**

```bash
# Check memory usage
docker stats

# Reduce API workers
API_WORKERS=4  # Instead of 8

# Increase container memory limit
docker update --memory 4g healthcare-api
```

**5. SSL/TLS Certificate Issues:**

```bash
# Check certificate expiry
openssl x509 -in certificate.crt -noout -dates

# Renew Let's Encrypt certificate
certbot renew

# Test SSL configuration
curl -vI https://api.hospital.com
```

### Debug Mode

Enable debug logging:

```bash
# Set in .env
LOG_LEVEL=DEBUG

# Restart application
docker-compose restart api

# View debug logs
docker logs -f healthcare-api
```

### Performance Profiling

```bash
# Install profiling tools
pip install py-spy

# Profile running application
py-spy top --pid $(pgrep -f "python main.py")

# Generate flame graph
py-spy record -o profile.svg --pid $(pgrep -f "python main.py")
```

---

## MAINTENANCE

### Regular Tasks

**Daily:**
- [ ] Check application logs for errors
- [ ] Verify database backups completed
- [ ] Monitor API response times
- [ ] Review security alerts

**Weekly:**
- [ ] Update dependencies (security patches)
- [ ] Review resource usage trends
- [ ] Test disaster recovery procedures
- [ ] Rotate access logs

**Monthly:**
- [ ] Security audit
- [ ] Performance optimization review
- [ ] Update documentation
- [ ] Test backup restoration
- [ ] Review and renew SSL certificates

### Scaling Guidelines

**Horizontal Scaling (Add more pods/containers):**

```bash
# Kubernetes
kubectl scale deployment healthcare-api --replicas=10 -n healthcare-ai

# Docker Compose
docker-compose up -d --scale api=5
```

**Vertical Scaling (Increase resources):**

```yaml
# Update resources in deployment
resources:
  requests:
    memory: "4Gi"
    cpu: "2000m"
  limits:
    memory: "8Gi"
    cpu: "4000m"
```

---

## SUPPORT

### Emergency Contacts

- **On-Call Engineer:** +1-800-EMERGENCY
- **Security Team:** security@hospital.com
- **Database Admin:** dba@hospital.com

### Escalation Path

1. **P1 (Critical):** Immediate escalation to on-call
2. **P2 (Major):** Escalate within 1 hour
3. **P3 (Minor):** Escalate within 4 hours
4. **P4 (Low):** Regular business hours

---

**🚀 DEPLOYMENT GUIDE COMPLETE**

For questions or issues, refer to:
- Main README.md
- FINAL_IMPLEMENTATION.md
- TROUBLESHOOTING.md
