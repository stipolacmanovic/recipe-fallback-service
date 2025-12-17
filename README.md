# Wine Search API

A FastAPI-based REST API for searching wines.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the development server:
```bash
uvicorn main:app --reload
```

The API will be available at:
- API: http://127.0.0.1:8000
- Interactive API docs: http://127.0.0.1:8000/docs
- Alternative API docs: http://127.0.0.1:8000/redoc

## Project Structure

```
.
├── main.py           # FastAPI application
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## Development

- The `--reload` flag enables auto-reload on code changes
- API documentation is automatically generated at `/docs` and `/redoc`



