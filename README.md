# First Cloud Journey Assistant

An intelligent RAG-based chatbot designed to assist the First Cloud AI Journey (FCAJ) community with AWS and cloud computing knowledge, program rules, and administrative information.

## Tech Stack

### AI/ML Framework
- **LangChain** - Orchestration framework for LLM applications
- **Groq** - High-performance LLM inference (Llama 3.1 8B)
- **HuggingFace Transformers** - Multilingual embeddings (paraphrase-multilingual-MiniLM-L12-v2)

### Vector Database
- **FAISS** - Efficient similarity search and document retrieval

### Frontend
- **Streamlit** - Interactive web interface

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

### Language
- **Python 3.x** - Core programming language

## Setup Guide:

### Option 1: Run with Docker (Recommended)

1. **Install Docker:**
   - Download Docker Desktop: https://www.docker.com/products/docker-desktop

2. **Build and run:**
```bash
docker-compose up --build
```

3. **Access:**
   - Open browser: http://localhost:8501

### Option 2: Run locally

1. **Clone repository:**
```bash
git clone https://github.com/hoanglong1812003/chatbotfcaj.git
cd chatbotfcaj
```

2. **Install packages:**
```bash
pip install -r requirements.txt
```

3. **Configure API key:**
```bash
cp .env.example .env
# Edit .env and add GROQ_API_KEY
```

4. **Prepare data:**
- Create `data/` folder
- Place PDF/TXT documents in `data/` folder

5. **Process documents:**
```bash
python process_docs.py
```

6. **Run chatbot:**
```bash
streamlit run app.py
```

## Docker Commands:

```bash
# Build image
docker build -t fcj-chatbot .

# Run container
docker run -p 8501:8501 --env-file .env fcj-chatbot

# Stop container
docker-compose down

# View logs
docker-compose logs -f
```

## Directory Structure:
```
├── data/                 # Training documents (not pushed to git)
├── vectorstore/          # Vector database (auto-generated, not pushed)
├── app.py               # Main application
├── process_docs.py      # Document processing script
├── requirements.txt     # Dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose config
├── .env.example        # Template for API keys
├── .gitignore          # Exclude sensitive files
└── README.md           # Documentation
```

## Security Notes:
- `.env` file contains API keys - DO NOT push to git
- `data/` folder may contain sensitive documents - excluded
- Vector database is auto-generated - no need to push

## Usage:
- Re-run `process_docs.py` whenever adding new documents
- Chatbot will answer based on trained documents
- If information is not found, chatbot will notify

## CI/CD Pipeline

Automated deployment pipeline with GitHub Actions:
- **Lint**: Code quality checks (flake8, black)
- **Test**: Automated testing with pytest
- **Build**: Docker image creation
- **Deploy**: Auto-deploy to development on `develop` branch

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed CI/CD documentation.
