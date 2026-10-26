# Build 88: Weaviate Recipe Semantic Search Engine

> **Category**: Databases — Vector/Search > **Core Technologies**: Weaviate Vector Database, FastAPI, NumPy, Pydantic V2, Python 3.12, Vanilla JS Dashboard > **Status**: Complete & Verified (36/36 Automated Tests Passing)

## Stack

- **Primary Technology**: Weaviate (Databases - Vector/Search)
- **Python Packages**: `﻿annotated-doc`, `annotated-types`, `anyio`, `certifi`, `charset-normalizer`, `click`

## Setup & Environment

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Copy `.env.example` to `.env` if you want to override default local configuration.

## Usage

```powershell
python -m unittest discover -v
```

## Data & Privacy

- Processes data locally and stores state in gitignored local storage or sandboxed databases.
- Zero secrets, credentials, or personally identifiable information (PII) are hardcoded or committed.
