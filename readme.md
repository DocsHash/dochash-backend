# Document Hash Backend API

Backend system for document hashing and verification through blockchain on Starlette + PostgreSQL + Web3.

## Technologies

**Stack:** Starlette, Msgspec, PostgreSQL, Web3.py, Docker  
**Architecture:** API server + Blockchain worker + Event database

## Quick Start

```bash
docker-compose up --build
curl http://localhost:8000/
```

## Launch Options

### Production (API + Worker separately)
```bash
docker-compose up postgres api worker
# API: 4 uvicorn workers on :8000
# Worker: 1 blockchain monitoring process
```

### Development (all in one)
```bash
docker-compose --profile single up postgres single
# Single process on :8001
```

### API only (without worker)
```bash
docker-compose up postgres api
# For testing API without blockchain
```

### Local development
```bash
pip install -r requirements.txt
docker-compose up postgres
python3 -m app.main
```

## API Endpoints

| Method | Path | Description | Input | Output |
|--------|------|-------------|-------|--------|
| GET | `/` | Health check | - | `{"status": "ok"}` |
| POST | `/api/process-document` | PDF processing | multipart file | verification_id + hash |
| POST | `/api/verify-document` | Verification | JSON/file | verified + timestamp |

## Hashing Algorithm

**Critically important:** The system uses **SHA512** for compatibility with blockchain contract

**Python (Backend):**
```python
hashlib.sha512(file_content).hexdigest()
```

**JavaScript (Contract):**
```javascript
crypto.createHash('sha512').update(fileBuffer).digest('hex')
```

Any change to the hashing algorithm will break compatibility between systems

## Configuration (.env)

### Localhost (Hardhat)
```bash
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
BLOCKCHAIN_NETWORK=localhost
```

### Polygon Mumbai
```bash
RPC_URL=https://rpc-mumbai.maticvigil.com/
CONTRACT_ADDRESS=your_contract_address
BLOCKCHAIN_NETWORK=mumbai
```

### Polygon Mainnet
```bash
RPC_URL=https://polygon-rpc.com/
CONTRACT_ADDRESS=your_contract_address
BLOCKCHAIN_NETWORK=polygon
```

## Commands

### Main
```bash
# Project creation
python setup_project.py

# Production launch
docker-compose up postgres api worker

# Development
docker-compose --profile single up postgres single

# Stop
docker-compose down
```

### API Testing

#### Health check
```bash
curl http://localhost:8000/
```

#### Document processing
```bash
curl -X POST -F "file=@pdf-1.pdf" http://localhost:8000/api/process-document
```

#### Document verification three ways

**1. By verification_id:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"verification_id":"nf8IdRjm"}' \
  http://localhost:8000/api/verify-document
  
  {"verified":true,"message":"Документ найден в блокчейне","timestamp":"2025-07-09T15:42:07.673746","creator":"0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"}
  
```

**2. By document_hash:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"document_hash":"f8ed1414e5044e0301dbd7128f0a9e845188283887b81b82fde63c55bd43f5b7f34b3dc61b8489e1cc1237ef4b431de50543b04068b61a2e2a93336543d3e558"}' \
  http://localhost:8000/api/verify-document
```

**3. By file:**
```bash
curl -X POST -F "file=@pdf-6.pdf" http://localhost:8000/api/verify-document
```

**Expected verification result:**
```json
{
  "verified": true,
  "message": "Document found in blockchain",
  "timestamp": "2025-07-09T15:30:45",
  "creator": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
}
```

### Monitoring
```bash
# Logs of all services
docker-compose logs -f

# API logs only
docker-compose logs -f api

# Worker logs only
docker-compose logs -f worker

# Container status
docker-compose ps

# Database
docker-compose exec postgres psql -U postgres -d document_hash

# Last processed block
cat data/last_block.txt

# Number of documents
docker-compose exec postgres psql -U postgres -d document_hash \
  -c "SELECT COUNT(*) FROM document_records;"
```

## Complete System Workflow

### 1. Document storage in blockchain (external JavaScript)
```bash
node document-verifier.js store ./pdf-6.pdf
# Result: verification_id = nf8IdRjm
```

### 2. Synchronization through Worker
```
🔍 Scanning blocks 16 - 16
🔍 Processing event from block 16
🔍 Creator: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
💾 Saved document: nf8IdRjm
✅ Processed 1 events
```

### 3. Verification through API
```bash
# Reprocessing the same file
curl -X POST -F "file=@pdf-6.pdf" http://localhost:8000/api/process-document
# Result: "is_unique":false, "message":"Document already exists with ID: nf8IdRjm"
```

## Security Architecture

### Uniqueness verification
- **document_hash** - checked for existence in database
- **verification_id** - generated with collision checking
- **file** - PDF format validation

### Collision handling
```python
# In case of verification_id collision, system automatically generates new ID
existing_id = await database.get_by_verification_id(verification_id)
if existing_id:
    while existing_id:
        verification_id, _, _ = DocumentProcessor.process_document(file_content, filename)
        existing_id = await database.get_by_verification_id(verification_id)
```

## File Structure

```
backend/
├── docker-compose.yml       # Infrastructure
├── Dockerfile              # Container
├── entrypoint.sh           # Entry points
├── requirements.txt        # Dependencies
├── .env                    # Configuration
└── app/
    ├── api_handlers.py     # API logic
    ├── app_factory.py      # Application factory
    ├── asgi.py            # Multi-worker API
    ├── worker.py          # Blockchain worker
    ├── main.py            # Single process
    ├── models.py          # Database
    ├── schemas.py         # Msgspec schemas
    ├── config.py          # Settings
    └── services/
        ├── document_processor.py
        ├── blockchain_service.py
        └── blockchain_worker.py
```

## Use Cases

### MVP/Demo
```bash
# Quick start for demonstration
docker-compose --profile single up postgres single
```

### Production
```bash
# Scalable architecture
docker-compose up postgres api worker
# Can add more API instances
```

### Development
```bash
# Local development without Docker
pip install -r requirements.txt
docker-compose up postgres
python -m app.main
```

### API Testing
```bash
# API only without blockchain worker
docker-compose up postgres api
```

### Worker Debugging
```bash
# Worker only for blockchain debugging
docker-compose up postgres worker
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| API unavailable | `docker-compose ps`, check ports |
| Worker not working | `docker-compose logs worker`, check RPC_URL |
| Database unavailable | `docker-compose up postgres`, check health |
| Blockchain unavailable | `curl $RPC_URL`, check network |
| No data permissions | `chmod -R 777 data/` |
| Different document hashes | Check hashing algorithm (should be SHA512) |
| Document not found | Ensure Worker synchronized data from blockchain |

## Environment Variables

```bash
# Required
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/document_hash
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3

# Optional
BLOCKCHAIN_NETWORK=localhost
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
DEBUG=true
LOG_LEVEL=INFO
API_WORKERS=4
```

## Performance

- **API:** Async Starlette + Msgspec = high performance
- **Worker:** Blockchain event batching
- **Database:** Indexes for fast search
- **Scaling:** Multiple API workers + Single worker
- **Hashing:** SHA512 for blockchain contract compatibility