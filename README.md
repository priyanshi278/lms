# LibGuard Library Management System

A premium, glassmorphism-inspired Library Management System built with FastAPI and SQLAlchemy.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.8+
- Virtual Environment (`venv`)

### 2. Setup
```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies (if not already installed)
pip install fastapi "uvicorn[standard]" sqlalchemy jinja2 python-multipart pydantic
```

### 3. Database Initialization
Run the seeding script to populate the system with sample data:
```powershell
python seed_db.py
```

### 4. Run the Application
```powershell
python main.py
```
The app will be available at `http://127.0.0.1:8000`

---

## 📖 Sample Usage Flow

### Admin Journey
- **Login**: Use `admin` / `Password123`
- **Maintenance**: Add new books, create memberships, or manage users via the Maintenance dashboard.
- **Reports**: View fine collections, membership lists, and active book issues.

### User Journey
- **Sign Up**: Create an account via the Sign Up page.
- **Transactions**: 
    - Search for available books.
    - Issue a book (automatically calculates return date).
    - Return a book (calculates late fines if applicable).
- **Fine Payment**: Clear outstanding dues for returned items.

---

## 🛠️ Tech Stack
- **Backend**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Jinja2 Templates, Vanilla CSS (Glassmorphism)
- **Validation**: Pydantic V2
