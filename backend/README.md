# Backend - E-Commerce Marketplace

FastAPI backend for the multi-vendor e-commerce marketplace.

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `GET /api/health` - Health check

## Development

The server runs on http://localhost:8000
API documentation available at http://localhost:8000/docs
