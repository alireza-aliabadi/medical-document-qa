# medical-document-qa
AI-powered Medical Knowledge Assistant featuring OCR, Retrieval-Augmented Generation (RAG), QLoRA fine-tuning, semantic search, evaluation pipeline, and production-ready deployment with FastAPI, Docker.

# AI Medical Knowledge Assistant

> AI-powered Medical Knowledge Assistant featuring OCR, Retrieval-Augmented Generation (RAG), QLoRA fine-tuning, semantic search, evaluation pipeline, and production-ready deployment with FastAPI, Docker, Kubernetes, and modern AI infrastructure.

---

# 🎯 Project Goal

Build a production-grade Medical AI platform that demonstrates the complete lifecycle of an LLM application, including:

- Medical document ingestion
- OCR
- Data preprocessing
- Dataset generation
- QLoRA fine-tuning
- Retrieval-Augmented Generation (RAG)
- Evaluation
- Model serving
- Production deployment
- AI observability

---

# 🚀 Project Objectives

- Upload and process medical documents
- Extract searchable knowledge from PDFs
- Fine-tune a lightweight LLM for medical question answering
- Build a scalable RAG pipeline
- Deploy production-ready inference APIs
- Demonstrate AI Platform engineering best practices
- Showcase end-to-end AI system development

---

# 🏗️ High-Level Architecture

```text
                React Dashboard
                       │
                       ▼
                 FastAPI Gateway
                       │
        ┌──────────────┼───────────────┐
        │              │               │
        ▼              ▼               ▼
 Document Service   Chat Service   Evaluation Service
        │              │               │
        ▼              ▼               ▼
   OCR Pipeline      RAG Engine     Benchmarks
        │              │
        ▼              ▼
 Chunking Service   Fine-tuned LLM
        │              │
        ▼              ▼
 Embedding Service  vLLM
        │
        ▼
     Qdrant
        │
        ▼
     PostgreSQL
```

---

# 🛠 Technology Stack

## Backend

- Python 3.12
- FastAPI
- SQLAlchemy
- Alembic
- Celery
- Redis

## AI / LLM

- Qwen 2.5 1.5B
- Hugging Face Transformers
- TRL
- PEFT
- Unsloth
- bitsandbytes

## Embeddings

- BAAI/bge-small-en-v1.5

## Vector Database

- Qdrant

## Database

- PostgreSQL

## Object Storage

- MinIO

## OCR

- OCRmyPDF
- Tesseract OCR

## Frontend

- React
- TypeScript
- Vite
- TailwindCSS

## Monitoring

- OpenTelemetry
- Prometheus
- Grafana

## Experiment Tracking

- MLflow

## Infrastructure

- Docker
- Docker Compose
- Kubernetes
- Helm
- GitHub Actions

---

# 📅 Development Roadmap

---

# Phase 1 — Project Foundation

## Goal

Build a production-ready project skeleton.

---

## Milestone 1.1 — Repository Initialization

### Features

- Repository structure
- Python environment
- Docker Compose
- Makefile
- Environment configuration
- Pre-commit hooks

### Deliverables

- Initial project
- Docker environment
- Development workflow

---

## Milestone 1.2 — Backend Foundation

### Features

- FastAPI
- SQLAlchemy
- Alembic
- JWT Authentication
- Logging
- Configuration management

### Deliverables

- REST API
- Health endpoint
- Authentication

---

## Milestone 1.3 — Frontend Foundation

### Features

- React
- TailwindCSS
- Dashboard
- Authentication pages
- API client

### Deliverables

- Basic UI
- Login
- Dashboard layout

---

## Milestone 1.4 — Infrastructure

### Features

- PostgreSQL
- Redis
- MinIO
- Qdrant

### Deliverables

- Docker Compose stack
- Local development environment

---

# Phase 2 — Medical Document Processing

## Goal

Build the complete document ingestion pipeline.

---

## Milestone 2.1 — Medical PDF Upload

### Features

- Upload PDFs
- Metadata extraction
- Storage in MinIO

### Deliverables

- Upload API
- File management

---

## Milestone 2.2 — OCR Pipeline

### Features

- OCR
- Text extraction
- Page indexing

### Deliverables

- Searchable document text

---

## Milestone 2.3 — Chunking Pipeline

### Features

- Semantic chunking
- Metadata generation
- Citation metadata

### Deliverables

- Search-ready chunks

---

## Milestone 2.4 — Embedding Pipeline

### Features

- Embedding generation
- Background workers
- Qdrant indexing

### Deliverables

- Semantic search index

---

# Phase 3 — Retrieval-Augmented Generation (RAG)

## Goal

Build an intelligent medical assistant.

---

## Milestone 3.1 — Retriever

### Features

- Semantic retrieval
- Metadata filtering
- Hybrid search

---

## Milestone 3.2 — Chat API

### Features

- Streaming responses
- Conversation history
- Session management

---

## Milestone 3.3 — Citation Engine

### Features

- Source highlighting
- Confidence score
- Page references

---

## Milestone 3.4 — Prompt Engineering

### Features

- Prompt templates
- Context optimization
- Medical safety prompts

---

# Phase 4 — Fine-Tuning Pipeline

## Goal

Train a medical question-answering model.

---

## Milestone 4.1 — Dataset Builder

### Features

- Medical document parsing
- Question generation
- Answer generation
- Dataset cleaning
- Deduplication

### Pipeline

```text
Medical Documents
        │
        ▼
Preprocessing
        │
        ▼
Question Generation
        │
        ▼
Answer Generation
        │
        ▼
Instruction Dataset
```

---

## Milestone 4.2 — Training Pipeline

### Features

- QLoRA
- LoRA
- 4-bit quantization
- Gradient checkpointing
- Training scripts

### Deliverables

- Fine-tuned model

---

## Milestone 4.3 — Evaluation

### Metrics

- Exact Match (EM)
- F1 Score
- Hallucination Rate
- Citation Accuracy
- Latency

### Deliverables

- Evaluation reports

---

## Milestone 4.4 — Inference

### Features

- vLLM deployment
- Streaming inference
- REST API

---

# Phase 5 — AI Platform Features

## Goal

Build enterprise AI infrastructure.

---

## Milestone 5.1 — Model Registry

### Features

- Versioning
- Metadata
- Checkpoints

---

## Milestone 5.2 — Experiment Tracking

### Features

- MLflow
- Loss tracking
- Metrics
- Artifact storage

---

## Milestone 5.3 — Dataset Versioning

### Features

- Dataset snapshots
- Lineage
- Reproducibility

---

## Milestone 5.4 — Evaluation Dashboard

### Features

- Accuracy charts
- Latency charts
- Cost analysis
- Token usage

---

# Phase 6 — Production Engineering

## Goal

Prepare the platform for production deployment.

---

## Milestone 6.1 — Observability

### Features

- OpenTelemetry
- Prometheus
- Grafana
- Structured logging
- Distributed tracing

---

## Milestone 6.2 — Security

### Features

- JWT
- RBAC
- API Keys
- Rate limiting
- Secrets management

---

## Milestone 6.3 — CI/CD

### Features

- GitHub Actions
- Linting
- Unit tests
- Docker builds
- Security scanning

---

## Milestone 6.4 — Kubernetes Deployment

### Features

- Helm charts
- Ingress
- ConfigMaps
- Secrets
- Horizontal Pod Autoscaler

---

# Phase 7 — Advanced AI Features

## Goal

Transform the project into a production AI platform.

---

## Milestone 7.1 — Medical AI Agent

### Features

- Tool calling
- Drug lookup
- Medical search
- Calculator

---

## Milestone 7.2 — Multi-document QA

### Features

- Query multiple PDFs
- Cross-document citations
- Semantic ranking

---

## Milestone 7.3 — Medical Knowledge Graph

### Features

- Disease extraction
- Drug extraction
- Treatment extraction
- Relationship mapping

---

## Milestone 7.4 — Medical Copilot

### Features

- Guideline summarization
- Treatment comparison
- Patient-friendly explanations
- Evidence-backed responses

---

# 📂 Repository Structure

```text
ai-medical-knowledge-assistant/
│
├── backend/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── services/
│   ├── workers/
│   └── tests/
│
├── frontend/
│
├── training/
│   ├── datasets/
│   ├── preprocessing/
│   ├── finetuning/
│   ├── evaluation/
│   └── inference/
│
├── embeddings/
│
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   ├── helm/
│   └── monitoring/
│
├── docs/
│
├── scripts/
│
├── .github/
│
├── README.md
├── PROJECT_PROGRESS.md
├── CONTRIBUTING.md
├── LICENSE
└── Makefile
```

---

# 📈 Resume Highlights

This project demonstrates experience in:

- AI Platform Engineering
- Medical AI
- Fine-tuning LLMs (QLoRA)
- Retrieval-Augmented Generation (RAG)
- Semantic Search
- OCR Pipelines
- Dataset Engineering
- LLM Evaluation
- FastAPI Development
- Docker & Kubernetes
- MLflow Experiment Tracking
- OpenTelemetry Observability
- CI/CD with GitHub Actions
- Production AI Infrastructure

---

# 🎯 Expected Outcome

By the end of this project, you'll have a portfolio-quality application that showcases:

- End-to-end AI system development
- Modern LLM engineering practices
- Production-ready backend architecture
- AI infrastructure and deployment skills
- Fine-tuning and evaluation workflows
- Scalable, observable, and maintainable software engineering
