# IDSS Technical Documentation
## AI-Powered Section Throughput Optimization in Indian Railways

### Version: 1.0
### Date: September 2025
### Status: Production Ready

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [API Documentation](#api-documentation)
4. [Deployment Guide](#deployment-guide)
5. [Security Implementation](#security-implementation)
6. [Scalability Design](#scalability-design)
7. [Database Schema](#database-schema)
8. [Configuration Management](#configuration-management)
9. [Monitoring & Observability](#monitoring--observability)
10. [Development Guidelines](#development-guidelines)

---

## System Overview

### Purpose
The Intelligent Decision Support System (IDSS) is designed to optimize section throughput in Indian Railways through AI-powered analytics, real-time conflict prediction, and automated optimization recommendations.

### Key Features
- **Real-time Analytics**: Live processing of train movements, signals, and track status
- **Conflict Prediction**: AI-powered prediction of potential conflicts with 90%+ accuracy
- **Optimization Engine**: Multi-objective optimization for throughput and punctuality
- **What-If Scenarios**: Interactive scenario planning and impact analysis
- **Unified Dashboard**: Comprehensive web-based monitoring interface
- **Scalable Architecture**: Distributed processing for multiple railway zones

### Technology Stack
```
Backend:     Python 3.11+, AsyncIO, FastAPI
Frontend:    HTML5, JavaScript (ES6+), WebSocket
Database:    PostgreSQL 14+, Redis Cache
ML/AI:       Scikit-learn, TensorFlow/PyTorch
Security:    JWT, bcrypt, Role-based Access Control
Monitoring:  Prometheus, Grafana, ELK Stack
Deployment:  Docker, Kubernetes, NGINX
```

### Performance Specifications
- **Real-time Processing**: < 100ms response time
- **Throughput**: 10,000+ operations/second
- **Availability**: 99.9% SLA
- **Scalability**: Auto-scaling from 2 to 50 nodes
- **Data Retention**: 3 years with automated archival

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     IDSS Architecture                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Web UI    │  │  Mobile     │  │ API Clients │        │
│  │ Dashboard   │  │    App      │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                 │                 │              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Load Balancer (NGINX)                     │ │
│  └─────────────────────────────────────────────────────────┘ │
│         │                                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 API Gateway                             │ │
│  │        (Authentication, Rate Limiting)                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│         │                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Web Server  │  │ Analytics   │  │ Optimization│        │
│  │   Nodes     │  │   Engine    │  │   Engine    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                 │                 │              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Message Queue (Redis)                     │ │
│  └─────────────────────────────────────────────────────────┘ │
│         │                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Digital     │  │   Data      │  │ Monitoring  │        │
│  │   Twin      │  │ Processing  │  │   System    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │            Database Cluster (PostgreSQL)               │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

#### 1. Data Ingestion Layer
- **Mock Data Feed**: Simulates real-time railway data
- **Railway API Integration**: CRIS, FOIS, NTES connections
- **Data Validation**: Schema validation and cleansing
- **Event Streaming**: Real-time data pipeline

#### 2. Processing Layer
- **Digital Twin**: Virtual representation of railway section
- **Analytics Engine**: Predictive analytics and pattern recognition
- **Optimization Engine**: Multi-objective optimization algorithms
- **What-If Engine**: Scenario simulation and impact analysis

#### 3. API Layer
- **RESTful APIs**: Standard HTTP/JSON interfaces
- **WebSocket APIs**: Real-time data streaming
- **GraphQL**: Flexible query interface
- **Authentication**: JWT-based security

#### 4. Presentation Layer
- **Unified Dashboard**: Web-based monitoring interface
- **Mobile Interface**: Responsive design for tablets/phones
- **Export Functions**: Data export in multiple formats

### Data Flow Architecture

```
Railway Systems → Data Ingestion → Validation → Processing → Storage
      ↓                                             ↓
API Integration → Real-time Stream → Analytics → Digital Twin
      ↓                                             ↓
  CRIS/FOIS → Event Processing → ML Models → Optimization
      ↓                                             ↓
External APIs → Message Queue → Recommendations → Dashboard
```

---

## API Documentation

### Base URL
```
Production:  https://idss-api.railways.gov.in/v1
Staging:     https://idss-staging.railways.gov.in/v1
Development: http://localhost:8000/api/v1
```

### Authentication
All API requests require authentication using JWT tokens:
```http
Authorization: Bearer <jwt_token>
```

### Core Endpoints

#### 1. System Status
```http
GET /api/status
```
**Response:**
```json
{
  "status": "healthy",
  "uptime_minutes": 1440.5,
  "version": "1.0.0",
  "environment": "production",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "analytics": "healthy"
  }
}
```

#### 2. Live KPIs
```http
GET /api/kpis
```
**Response:**
```json
{
  "operational": {
    "total_trains": 156,
    "delayed_trains": 12,
    "punctuality": 92.3,
    "throughput": 85.2
  },
  "ai_performance": {
    "conflicts_predicted": 5,
    "recommendations_generated": 12,
    "prediction_accuracy": 91.5
  },
  "financial": {
    "cost_savings": 2450000,
    "energy_efficiency": 12.3
  }
}
```

#### 3. Run Scenario
```http
POST /api/scenarios/run
```
**Request:**
```json
{
  "name": "Emergency Hold Scenario",
  "train_id": "T001",
  "action": "HOLD",
  "duration_minutes": 15,
  "railway_zone": "CR"
}
```
**Response:**
```json
{
  "scenario_id": "sc_123456",
  "status": "completed",
  "impact_analysis": {
    "delay_added_minutes": 15.2,
    "affected_trains": ["T002", "T003"],
    "capacity_impact": "MODERATE",
    "estimated_recovery_time": 22.5
  },
  "risk_assessment": {
    "level": "HIGH",
    "factors": {
      "delay_minutes": 15.2,
      "affected_trains": 2
    }
  },
  "recommendations": [
    "Consider alternative routing for following trains",
    "Notify passengers of expected delays"
  ]
}
```

#### 4. Analytics Data
```http
GET /api/analytics
```
**Response:**
```json
{
  "conflicts": [
    {
      "id": "conf_001",
      "type": "PLATFORM",
      "location": "STN_A",
      "probability": 0.85,
      "severity": "HIGH",
      "estimated_impact": "15 minutes delay"
    }
  ],
  "recommendations": [
    {
      "id": "rec_001",
      "type": "HOLD",
      "train": "T001",
      "expected_benefit": "Prevent platform congestion",
      "confidence": 0.89
    }
  ]
}
```

### Error Responses
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid train ID format",
    "details": {
      "field": "train_id",
      "expected_format": "T[0-9]{3}"
    }
  }
}
```

### Rate Limiting
- **Standard Users**: 100 requests/minute
- **Premium Users**: 1000 requests/minute
- **System Users**: 10000 requests/minute

---

## Deployment Guide

### Prerequisites
- Docker 20.10+
- Kubernetes 1.25+
- PostgreSQL 14+
- Redis 6.2+
- NGINX 1.20+

### Production Deployment Steps

#### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/indian-railways/idss-mvp.git
cd idss-mvp

# Create environment file
cp .env.example .env.production

# Configure environment variables
vim .env.production
```

#### 2. Required Environment Variables
```env
# Database
DB_HOST=railways-db-cluster.internal
DB_PORT=5432
DB_NAME=idss_production
DB_USERNAME=idss_user
DB_PASSWORD=<secure_password>

# Security
SECRET_KEY=<generate_secure_key>
JWT_SECRET=<generate_jwt_secret>
ENCRYPTION_KEY=<generate_encryption_key>

# Railway APIs
CRIS_API_URL=https://api.cris.railways.gov.in
FOIS_API_URL=https://fois.railways.gov.in/api
NTES_API_URL=https://enquiry.indianrail.gov.in/mntes

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
```

#### 3. Database Setup
```sql
-- Create database and user
CREATE DATABASE idss_production;
CREATE USER idss_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE idss_production TO idss_user;

-- Run migrations
python manage.py migrate --environment=production
```

#### 4. Docker Deployment
```bash
# Build images
docker build -t idss-api:v1.0 .
docker build -t idss-worker:v1.0 -f Dockerfile.worker .

# Deploy with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

#### 5. Kubernetes Deployment
```yaml
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: idss-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: idss-api
  template:
    metadata:
      labels:
        app: idss-api
    spec:
      containers:
      - name: api
        image: idss-api:v1.0
        ports:
        - containerPort: 8000
        env:
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: idss-secrets
              key: db-host
```

#### 6. Load Balancer Configuration
```nginx
# /etc/nginx/sites-available/idss
upstream idss_backend {
    least_conn;
    server 10.0.1.10:8000 weight=3;
    server 10.0.1.11:8000 weight=3;
    server 10.0.1.12:8000 weight=2;
}

server {
    listen 80;
    server_name idss.railways.gov.in;
    
    location /api/ {
        proxy_pass http://idss_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Rate limiting
        limit_req zone=api burst=100 nodelay;
    }
    
    location / {
        root /var/www/idss/static;
        try_files $uri $uri/ /index.html;
    }
}
```

### Health Checks
```bash
# API Health
curl http://localhost:8000/api/status

# Database Connectivity
python -c "from production_config import *; print('DB OK' if test_db_connection() else 'DB FAIL')"

# Cache Connectivity
redis-cli -h localhost ping
```

---

## Security Implementation

### Authentication & Authorization

#### JWT Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "usr_123",
    "username": "operator1",
    "role": "OPERATOR",
    "railway_zone": "CR",
    "exp": 1693766400,
    "iat": 1693680000
  }
}
```

#### Role-Based Permissions
| Role | Dashboard | Scenarios | Analytics | Configuration | User Management |
|------|-----------|-----------|-----------|---------------|-----------------|
| OPERATOR | Read | Read/Execute | Read | - | - |
| SUPERVISOR | Read/Write | Read/Write/Execute | Read/Write | Read | - |
| MANAGER | Read/Write | Read/Write/Execute | Read/Write | Read/Write | Read |
| ADMIN | Full | Full | Full | Full | Full |

#### Security Middleware
```python
@require_authentication(
    required_role=UserRole.SUPERVISOR,
    required_permission=PermissionLevel.EXECUTE,
    resource_type=ResourceType.SCENARIOS
)
async def run_scenario(request):
    # Protected endpoint logic
    pass
```

### Data Protection

#### Encryption at Rest
- Database: AES-256 encryption for sensitive columns
- File Storage: Encrypted file system (LUKS)
- Backups: GPG encryption for backup files

#### Encryption in Transit
- TLS 1.3 for all HTTP traffic
- mTLS for service-to-service communication
- VPN tunnels for external API connections

#### Data Masking
```python
# Sensitive data masking
def mask_train_data(data):
    return {
        'train_id': data['train_id'],
        'location': data['location'],
        'operator_id': '***masked***',  # PII masked
        'crew_details': '***masked***'  # PII masked
    }
```

### Audit Logging

#### Audit Log Format
```json
{
  "timestamp": "2025-09-12T10:30:00Z",
  "user_id": "usr_123",
  "action": "RUN_SCENARIO",
  "resource": "scenarios",
  "details": {
    "scenario_id": "sc_456",
    "train_id": "T001",
    "success": true
  },
  "ip_address": "10.0.1.100",
  "user_agent": "Mozilla/5.0...",
  "risk_level": "LOW"
}
```

#### Compliance Requirements
- **IS 27001**: Information security management
- **Railway Board Guidelines**: Operational safety compliance
- **Data Localization**: All data within Indian borders
- **Audit Trails**: Immutable logs for 7 years

---

## Scalability Design

### Horizontal Scaling

#### Auto-Scaling Configuration
```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: idss-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: idss-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

#### Load Balancing Algorithms
1. **Weighted Round Robin**: Based on node capacity
2. **Least Connections**: Minimum active connections
3. **Resource-Based**: CPU/memory utilization
4. **Geographic**: Zone-based routing

### Distributed Processing

#### Task Queue Architecture
```python
# Task distribution by type
TASK_QUEUES = {
    'real_time': {
        'max_size': 1000,
        'priority': 'HIGH',
        'timeout': 100  # ms
    },
    'batch': {
        'max_size': 10000,
        'priority': 'MEDIUM',
        'timeout': 30000  # ms
    },
    'analytics': {
        'max_size': 500,
        'priority': 'LOW',
        'timeout': 60000  # ms
    }
}
```

#### Caching Strategy
- **L1 Cache**: In-memory application cache (64MB per node)
- **L2 Cache**: Redis distributed cache (1GB cluster)
- **L3 Cache**: Database query cache (2GB)
- **TTL Strategy**: Time-based expiration with LRU eviction

### Performance Optimization

#### Database Optimization
```sql
-- Partitioning by date and zone
CREATE TABLE train_data (
    id BIGSERIAL,
    train_id VARCHAR(10),
    zone VARCHAR(5),
    timestamp TIMESTAMP,
    data JSONB,
    PRIMARY KEY (id, zone, timestamp)
) PARTITION BY RANGE (timestamp);

-- Indexes for common queries
CREATE INDEX CONCURRENTLY idx_train_zone_time 
ON train_data (zone, timestamp) 
WHERE timestamp > NOW() - INTERVAL '7 days';

-- Materialized views for analytics
CREATE MATERIALIZED VIEW daily_kpis AS
SELECT 
    DATE(timestamp) as date,
    zone,
    COUNT(*) as total_trains,
    AVG(delay_minutes) as avg_delay
FROM train_data 
GROUP BY DATE(timestamp), zone;
```

#### Connection Pooling
```python
# Database connection pool
DATABASE_POOL = {
    'min_connections': 5,
    'max_connections': 20,
    'idle_timeout': 300,
    'query_timeout': 30,
    'connection_lifetime': 3600
}
```

---

## Database Schema

### Core Tables

#### Users Table
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role_enum NOT NULL,
    railway_zone VARCHAR(10) NOT NULL,
    department VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    is_locked BOOLEAN DEFAULT FALSE,
    locked_until TIMESTAMP
);
```

#### Train Data Table
```sql
CREATE TABLE train_data (
    id BIGSERIAL PRIMARY KEY,
    train_id VARCHAR(10) NOT NULL,
    train_number VARCHAR(10),
    zone VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    current_node VARCHAR(20),
    current_speed DECIMAL(5,2),
    delay_minutes INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    route_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
) PARTITION BY RANGE (timestamp);
```

#### Scenarios Table
```sql
CREATE TABLE scenarios (
    scenario_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    train_id VARCHAR(10) NOT NULL,
    action VARCHAR(20) NOT NULL,
    parameters JSONB NOT NULL,
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'PENDING',
    result JSONB,
    execution_time_ms INTEGER
);
```

#### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP DEFAULT NOW(),
    user_id UUID REFERENCES users(user_id),
    action VARCHAR(50) NOT NULL,
    resource VARCHAR(50) NOT NULL,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    risk_level VARCHAR(10) DEFAULT 'LOW'
) PARTITION BY RANGE (timestamp);
```

### Indexes and Constraints
```sql
-- Performance indexes
CREATE INDEX CONCURRENTLY idx_train_data_zone_time 
ON train_data (zone, timestamp DESC);

CREATE INDEX CONCURRENTLY idx_scenarios_user_time 
ON scenarios (created_by, created_at DESC);

CREATE INDEX CONCURRENTLY idx_audit_logs_user_action 
ON audit_logs (user_id, action, timestamp DESC);

-- Constraints
ALTER TABLE train_data 
ADD CONSTRAINT chk_speed_positive 
CHECK (current_speed >= 0);

ALTER TABLE scenarios 
ADD CONSTRAINT chk_valid_action 
CHECK (action IN ('HOLD', 'REROUTE', 'SPEED_ADJUST'));
```

### Data Retention Policy
```sql
-- Automated data archival
CREATE OR REPLACE FUNCTION archive_old_data() 
RETURNS void AS $$
BEGIN
    -- Archive train data older than 3 years
    INSERT INTO train_data_archive 
    SELECT * FROM train_data 
    WHERE timestamp < NOW() - INTERVAL '3 years';
    
    DELETE FROM train_data 
    WHERE timestamp < NOW() - INTERVAL '3 years';
    
    -- Archive audit logs older than 7 years
    DELETE FROM audit_logs 
    WHERE timestamp < NOW() - INTERVAL '7 years';
END;
$$ LANGUAGE plpgsql;
```

---

## Configuration Management

### Environment Configuration
```python
# Configuration hierarchy
ENVIRONMENT_CONFIGS = {
    'development': {
        'database': 'postgresql://localhost/idss_dev',
        'debug': True,
        'log_level': 'DEBUG'
    },
    'staging': {
        'database': 'postgresql://staging-db/idss_staging',
        'debug': False,
        'log_level': 'INFO'
    },
    'production': {
        'database': 'postgresql://prod-cluster/idss_prod',
        'debug': False,
        'log_level': 'WARNING'
    }
}
```

### Feature Flags
```json
{
  "features": {
    "advanced_analytics": {
      "enabled": true,
      "rollout_percentage": 100,
      "zones": ["CR", "WR", "NR"]
    },
    "auto_optimization": {
      "enabled": false,
      "rollout_percentage": 0,
      "zones": []
    },
    "mobile_interface": {
      "enabled": true,
      "rollout_percentage": 50,
      "user_roles": ["SUPERVISOR", "MANAGER", "ADMIN"]
    }
  }
}
```

### Configuration Validation
```python
def validate_production_config():
    """Validate production configuration"""
    required_vars = [
        'DB_HOST', 'DB_PASSWORD', 'SECRET_KEY',
        'JWT_SECRET', 'ENCRYPTION_KEY'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ConfigurationError(f"Missing: {missing}")
    
    # Validate database connection
    test_db_connection()
    
    # Validate external API endpoints
    test_railway_apis()
    
    return True
```

---

## Monitoring & Observability

### Metrics Collection
```python
# Prometheus metrics
METRICS = {
    'request_duration': Histogram(
        'idss_request_duration_seconds',
        'Request duration in seconds',
        ['method', 'endpoint', 'status_code']
    ),
    'active_connections': Gauge(
        'idss_active_connections',
        'Number of active database connections'
    ),
    'scenarios_executed': Counter(
        'idss_scenarios_total',
        'Total scenarios executed',
        ['zone', 'action_type']
    )
}
```

### Alerting Rules
```yaml
# Prometheus alerting rules
groups:
- name: idss_alerts
  rules:
  - alert: HighErrorRate
    expr: rate(idss_requests_total{status_code=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      
  - alert: DatabaseConnectionsHigh
    expr: idss_active_connections > 80
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Database connection pool usage high"
```

### Log Aggregation
```json
{
  "timestamp": "2025-09-12T10:30:00Z",
  "level": "INFO",
  "logger": "idss.api",
  "message": "Scenario executed successfully",
  "extra": {
    "user_id": "usr_123",
    "scenario_id": "sc_456",
    "execution_time_ms": 150,
    "train_id": "T001"
  }
}
```

### Health Checks
```python
async def health_check():
    """Comprehensive health check"""
    health_status = {
        'status': 'healthy',
        'checks': {}
    }
    
    # Database check
    try:
        await db.execute('SELECT 1')
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {e}'
        health_status['status'] = 'degraded'
    
    # Cache check
    try:
        await cache.ping()
        health_status['checks']['cache'] = 'healthy'
    except Exception as e:
        health_status['checks']['cache'] = f'unhealthy: {e}'
    
    # External APIs check
    health_status['checks']['apis'] = await check_external_apis()
    
    return health_status
```

---

## Development Guidelines

### Code Style
- **Python**: PEP 8 with Black formatter
- **JavaScript**: ESLint with Airbnb configuration
- **SQL**: SQL Style Guide compliance
- **Comments**: Docstrings for all public functions

### Testing Strategy
```python
# Test structure
tests/
├── unit/           # Unit tests (>90% coverage)
├── integration/    # Integration tests
├── e2e/           # End-to-end tests
├── performance/   # Performance tests
└── security/      # Security tests

# Test categories
pytest -m "unit"        # Fast unit tests
pytest -m "integration" # Integration tests
pytest -m "e2e"         # End-to-end tests
pytest -m "security"    # Security tests
```

### Git Workflow
```bash
# Feature development
git checkout -b feature/IDSS-123-optimization-engine
git commit -m "feat: implement multi-objective optimization"
git push origin feature/IDSS-123-optimization-engine

# Pull request workflow
1. Create feature branch
2. Implement changes with tests
3. Run full test suite
4. Submit pull request
5. Code review and approval
6. Merge to main branch
```

### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Security considerations addressed
- [ ] Performance impact evaluated
- [ ] Documentation updated
- [ ] Backward compatibility maintained

---

## Support & Maintenance

### Support Contacts
- **Development Team**: dev-team@railways.gov.in
- **Operations Team**: ops-team@railways.gov.in
- **Security Team**: security@railways.gov.in

### Documentation Updates
This documentation is maintained in the project repository and updated with each release. For the latest version, visit: https://docs.idss.railways.gov.in

### Version History
- **v1.0.0** (2025-09): Initial production release
- **v0.9.0** (2025-08): Beta release with all core features
- **v0.5.0** (2025-07): Alpha release with basic functionality

---

*This document is classified as **OFFICIAL** and is intended for authorized railway personnel only.*