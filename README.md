# SecureRAG – Permission-Aware AI Document Assistant

SecureRAG is a multi-tenant Retrieval-Augmented Generation (RAG) application that allows users to ask questions about organisational documents while enforcing role-based and user-specific access permissions.

It is designed to prevent users from retrieving information belonging to other organisations or documents they are not authorised to access.

## Key Features

- **Multi-tenant architecture:** Separates document access between different organisations.
- **Role-based access control (RBAC):** Controls document retrieval according to user roles.
- **User-specific permissions:** Supports access to documents assigned to individual users.
- **Secure authentication:** JWT-based login with Argon2 password hashing.
- **Admin-controlled registration:** Allows administrators to create users within their own organisation.
- **Semantic document retrieval:** Uses Sentence Transformers embeddings and Qdrant vector search.
- **Permission-aware retrieval:** Applies access filters before using retrieved documents and performs an additional permission check.
- **Audit logging:** Records document retrieval activity using SQLite.
- **Interactive interface:** Provides a Streamlit-based chatbot, user profile and admin user-management pages.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend | FastAPI |
| Frontend | Streamlit |
| Vector Database | Qdrant |
| Embedding Model | Sentence Transformers – all-MiniLM-L6-v2 |
| Authentication | JWT |
| Password Hashing | Argon2 |
| Database | SQLite |
| Data Handling | JSON |
| Testing | Pytest |

## System Architecture

1. Users authenticate through the login interface.
2. FastAPI validates credentials and issues a JWT access token.
3. The authenticated user's tenant ID, user ID and roles determine document permissions.
4. The question is converted into an embedding using Sentence Transformers.
5. Qdrant retrieves relevant document chunks using tenant and permission filters.
6. Retrieved chunks undergo an additional access-control check.
7. Only authorised chunks are used to generate the response.
8. Retrieval activity is recorded in the SQLite audit log.

## Project Structure

```text
SecureRAG/
│
├── main.py
├── app.py
├── ingest.py
├── evaluate.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── documents.json
│   ├── users.json
│   └── evaluation.json
│
├── tests/
│   └── test_acl.py
│
└── evaluation_results.csv
```

The `storage/` directory is generated locally to store Qdrant data and the SQLite audit database.

## Installation and Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd SecureRAG
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Ingest the documents

```bash
python ingest.py
```

Run ingestion before starting the backend. Stop the backend before running ingestion again when using local Qdrant storage.

### 5. Start the FastAPI backend

Open a terminal:

```bash
uvicorn main:app --reload
```

API documentation:

`http://127.0.0.1:8000/docs`

### 6. Start the Streamlit frontend

Open another terminal:

```bash
streamlit run app.py
```

Open the application at:

`http://localhost:8501`

## Evaluation

The application was evaluated using 13 predefined test cases covering document retrieval, role-based access, user-specific permissions and tenant isolation.

| Evaluation Metric | Result |
|---|---:|
| Test cases | 13 |
| Retrieval hit / correct-denial rate | 92.3% |
| Unauthorized retrievals | 0 |
| Automated ACL tests | 5/5 passed |

The evaluation uses a small synthetic dataset and is intended as a project-level demonstration, not a guarantee of production security or retrieval accuracy.

### Run automated tests

```bash
python -m pytest tests/test_acl.py -v
```

### Run retrieval evaluation

```bash
python evaluate.py
```

The evaluation script generates `evaluation_results.csv`.

## Security Considerations

- Passwords are stored using Argon2 hashing.
- JWT tokens are used for authenticated API requests.
- Tenant IDs and roles are derived from authenticated user information.
- Admin-only operations are independently validated by the backend.
- Retrieved document chunks are checked against access permissions before being used.
- The included accounts and documents are demonstration data only.

Before any real deployment, configure a strong private `JWT_SECRET`, replace demo credentials, protect user and audit data, and use an appropriately secured production database and deployment environment.

## Future Improvements

- Improve semantic retrieval and relevance ranking.
- Add document upload and management.
- Integrate an optional local LLM for more advanced answer generation.
- Add richer audit-log visualisation.
- Expand evaluation with a larger and more diverse test dataset.

## Author

B.Tech Artificial Intelligence and Data Science Student

**Project:** SecureRAG – Permission-Aware AI Document Assistant
