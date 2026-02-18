from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models, schemas, database
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

from pydantic import ValidationError
from typing import Optional
from datetime import date, timedelta
import datetime

@app.get("/", response_class=HTMLResponse)
async def welcome(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_exec(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.username == username,
        models.User.password == password
    ).first()
    
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})
    
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie("user_id", str(user.id))
    response.set_cookie("user_role", user.role)
    response.set_cookie("user_name", user.name)
    return response

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup_exec(
    request: Request,
    role: str = Form(...),
    name: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        schemas.UserCreate(name=name, username=username, password=password)
        
        existing_user = db.query(models.User).filter(models.User.username == username).first()
        if existing_user:
            return templates.TemplateResponse("signup.html", {"request": request, "error": "Username already taken"})
            
        new_user = models.User(name=name, username=username, password=password, role=role)
        db.add(new_user)
        db.commit()
        return RedirectResponse(url="/login", status_code=303)
    except ValueError as e:
        return templates.TemplateResponse("signup.html", {"request": request, "error": str(e)})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login")
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("user_id")
    response.delete_cookie("user_role")
    return response

def is_admin(request: Request):
    return request.cookies.get("user_role") == "admin"

@app.get("/maintenance", response_class=HTMLResponse)
async def maintenance_index(request: Request):
    if not is_admin(request):
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("maintenance/index.html", {"request": request})

@app.get("/maintenance/add-membership", response_class=HTMLResponse)
async def add_membership_page(request: Request):
    if not is_admin(request): return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("maintenance/add_membership.html", {"request": request})

@app.post("/maintenance/add-membership")
async def add_membership(
    request: Request,
    name: str = Form(...),
    address: str = Form(...),
    phone: str = Form(...),
    duration: str = Form(...),
    db: Session = Depends(get_db)
):
    if not is_admin(request): return RedirectResponse(url="/dashboard")
    
    last_member = db.query(models.Membership).order_by(models.Membership.id.desc()).first()
    new_id = (last_member.id + 1) if last_member else 1
    mem_num = f"M{new_id:03}"
    
    start_date = date.today()
    if duration == "6 Months":
        expiry_date = start_date + timedelta(days=180)
    elif duration == "1 Year":
        expiry_date = start_date + timedelta(days=365)
    else:
        expiry_date = start_date + timedelta(days=730)
        
    new_member = models.Membership(
        membership_number=mem_num,
        name=name,
        address=address,
        phone=phone,
        start_date=start_date,
        expiry_date=expiry_date,
        duration=duration
    )
    db.add(new_member)
    db.commit()
    return templates.TemplateResponse("maintenance/add_membership.html", {
        "request": request, 
        "success": f"Membership created successfully! Number: {mem_num}"
    })

@app.get("/maintenance/update-membership", response_class=HTMLResponse)
async def update_membership_page(request: Request):
    if not is_admin(request): return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("maintenance/update_membership.html", {"request": request})

@app.post("/maintenance/update-membership/fetch", response_class=HTMLResponse)
async def fetch_membership(
    request: Request,
    membership_number: str = Form(...),
    db: Session = Depends(get_db)
):
    if not is_admin(request): return RedirectResponse(url="/dashboard")
    member = db.query(models.Membership).filter(models.Membership.membership_number == membership_number).first()
    if not member:
        return templates.TemplateResponse("maintenance/update_membership.html", {"request": request, "error": "Membership not found"})
    return templates.TemplateResponse("maintenance/update_membership.html", {"request": request, "membership": member})

@app.post("/maintenance/update-membership")
async def update_membership(
    request: Request,
    membership_number: str = Form(...),
    action: str = Form(...),
    db: Session = Depends(get_db)
):
    if not is_admin(request): return RedirectResponse(url="/dashboard")
    member = db.query(models.Membership).filter(models.Membership.membership_number == membership_number).first()
    
    if action == "extend":
        member.expiry_date = member.expiry_date + timedelta(days=180)
        member.duration = "Extended"
        msg = "Membership extended by 6 months."
    else:
        member.expiry_date = date.today()
        member.duration = "Cancelled"
        msg = "Membership cancelled."
        
    db.commit()
    return templates.TemplateResponse("maintenance/update_membership.html", {"request": request, "success": msg})

@app.get("/maintenance/add-book", response_class=HTMLResponse)
async def add_book_page(request: Request):
    if not is_admin(request): return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("maintenance/add_book.html", {"request": request})

@app.post("/maintenance/add-book")
async def add_book(
    request: Request,
    type: str = Form(...),
    name: str = Form(...),
    author: str = Form(...),
    serial_number: str = Form(...),
    category: str = Form(...),
    db: Session = Depends(get_db)
):
    if not is_admin(request): return RedirectResponse(url="/dashboard")
    
    existing_book = db.query(models.Book).filter(models.Book.serial_number == serial_number).first()
    if existing_book:
        return templates.TemplateResponse("maintenance/add_book.html", {"request": request, "error": "Serial Number already exists"})
    
    new_book = models.Book(
        type=type,
        name=name,
        author=author,
        serial_number=serial_number,
        category=category,
        status="available"
    )
    db.add(new_book)
    db.commit()
    return templates.TemplateResponse("maintenance/add_book.html", {"request": request, "success": "Item added successfully!"})

@app.get("/maintenance/update-book", response_class=HTMLResponse)
async def update_book_page(request: Request):
    if not is_admin(request): return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("maintenance/update_book.html", {"request": request})

@app.post("/maintenance/update-book/fetch", response_class=HTMLResponse)
async def fetch_book(
    request: Request,
    serial_number: str = Form(...),
    db: Session = Depends(get_db)
):
    if not is_admin(request): return RedirectResponse(url="/dashboard")
    book = db.query(models.Book).filter(models.Book.serial_number == serial_number).first()
    if not book:
        return templates.TemplateResponse("maintenance/update_book.html", {"request": request, "error": "Item not found"})
    return templates.TemplateResponse("maintenance/update_book.html", {"request": request, "book": book})

@app.post("/maintenance/update-book")
async def update_book_exec(
    request: Request,
    serial_number: str = Form(...),
    type: str = Form(...),
    name: str = Form(...),
    author: str = Form(...),
    category: str = Form(...),
    db: Session = Depends(get_db)
):
    if not is_admin(request): return RedirectResponse(url="/dashboard")
    book = db.query(models.Book).filter(models.Book.serial_number == serial_number).first()
    if not book:
        return templates.TemplateResponse("maintenance/update_book.html", {"request": request, "error": "Item not found"})
    
    book.type = type
    book.name = name
    book.author = author
    book.category = category
    db.commit()
    return templates.TemplateResponse("maintenance/update_book.html", {"request": request, "success": "Item updated successfully!"})

@app.get("/maintenance/user-management", response_class=HTMLResponse)
async def user_management_page(request: Request):
    if not is_admin(request): return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("maintenance/user_management.html", {"request": request})

@app.post("/maintenance/user-management")
async def user_management_exec(
    request: Request,
    account_type: str = Form(...),
    name: str = Form(...),
    username: str = Form(...),
    password: Optional[str] = Form(None),
    role: str = Form(...),
    db: Session = Depends(get_db)
):
    if not is_admin(request): return RedirectResponse(url="/dashboard")
    
    if account_type == "new":
        existing_user = db.query(models.User).filter(models.User.username == username).first()
        if existing_user:
            return templates.TemplateResponse("maintenance/user_management.html", {"request": request, "error": "Username already taken"})
        
        if not password or len(password) < 8:
            return templates.TemplateResponse("maintenance/user_management.html", {"request": request, "error": "Password must be at least 8 characters"})
            
        new_user = models.User(name=name, username=username, password=password, role=role)
        db.add(new_user)
        db.commit()
        return templates.TemplateResponse("maintenance/user_management.html", {"request": request, "success": "User created successfully!"})
    else:
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            return templates.TemplateResponse("maintenance/user_management.html", {"request": request, "error": "User not found"})
        
        user.name = name
        user.role = role
        if password:
            user.password = password
        db.commit()
        return templates.TemplateResponse("maintenance/user_management.html", {"request": request, "success": "User updated successfully!"})

@app.get("/transactions", response_class=HTMLResponse)
async def transactions_index(request: Request):
    return templates.TemplateResponse("transactions/index.html", {"request": request})

@app.get("/transactions/book-available", response_class=HTMLResponse)
async def book_available_page(request: Request):
    return templates.TemplateResponse("transactions/book_available.html", {"request": request, "books": None})

@app.post("/transactions/book-available", response_class=HTMLResponse)
async def book_available_search(
    request: Request,
    search_by: str = Form(...),
    search_value: str = Form(""),
    db: Session = Depends(get_db)
):
    if not search_value:
        return templates.TemplateResponse("transactions/book_available.html", {"request": request, "books": None, "error": "Please enter a search value"})
    
    query = db.query(models.Book)
    if search_by == "name":
        books = query.filter(models.Book.name.ilike(f"%{search_value}%")).all()
    elif search_by == "author":
        books = query.filter(models.Book.author.ilike(f"%{search_value}%")).all()
    else:
        books = query.filter(models.Book.category.ilike(f"%{search_value}%")).all()
        
    return templates.TemplateResponse("transactions/book_available.html", {"request": request, "books": books})

@app.get("/transactions/issue-book", response_class=HTMLResponse)
async def issue_book_page(request: Request, book: Optional[str] = None, db: Session = Depends(get_db)):
    today = date.today().isoformat()
    return_date = (date.today() + timedelta(days=15)).isoformat()
    
    author = None
    if book:
        book_obj = db.query(models.Book).filter(models.Book.name == book).first()
        if book_obj:
            author = book_obj.author
            
    return templates.TemplateResponse("transactions/issue_book.html", {
        "request": request, 
        "book_name": book,
        "author": author,
        "today": today, 
        "return_date": return_date
    })

@app.post("/transactions/issue-book")
async def issue_book_exec(
    request: Request,
    book_name: str = Form(...),
    issue_date: date = Form(...),
    return_date: date = Form(...),
    remarks: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    user_id = request.cookies.get("user_id")
    if not user_id: return RedirectResponse(url="/login")
    
    book = db.query(models.Book).filter(models.Book.name == book_name, models.Book.status == "available").first()
    if not book:
        return templates.TemplateResponse("transactions/issue_book.html", {
            "request": request, "error": "Book not available or not found", 
            "today": date.today().isoformat(), "return_date": (date.today() + timedelta(days=15)).isoformat()
        })
    
    if issue_date < date.today():
        return templates.TemplateResponse("transactions/issue_book.html", {
            "request": request, "error": "Issue date cannot be in the past", 
            "today": date.today().isoformat(), "return_date": (date.today() + timedelta(days=15)).isoformat()
        })
    
    if return_date > issue_date + timedelta(days=15):
        return templates.TemplateResponse("transactions/issue_book.html", {
            "request": request, "error": "Return date must be within 15 days", 
            "today": date.today().isoformat(), "return_date": (date.today() + timedelta(days=15)).isoformat()
        })

    transaction = models.Transaction(
        book_id=book.id,
        user_id=int(user_id),
        issue_date=issue_date,
        return_date=return_date,
        status="pending",
        remarks=remarks
    )
    
    book.status = "issued"
    
    db.add(transaction)
    db.commit()
    return templates.TemplateResponse("transactions/issue_book.html", {
        "request": request, 
        "success": f"Item '{book_name}' has been issued successfully!",
        "today": date.today().isoformat(), "return_date": (date.today() + timedelta(days=15)).isoformat()
    })

@app.get("/transactions/return-book", response_class=HTMLResponse)
async def return_book_page(request: Request):
    return templates.TemplateResponse("transactions/return_book.html", {"request": request, "today": date.today().isoformat()})

@app.post("/transactions/return-book/fetch", response_class=HTMLResponse)
async def fetch_return_details(
    request: Request,
    serial_number: str = Form(...),
    db: Session = Depends(get_db)
):
    book = db.query(models.Book).filter(models.Book.serial_number == serial_number).first()
    if not book:
        return templates.TemplateResponse("transactions/return_book.html", {"request": request, "error": "Item not found", "today": date.today().isoformat()})
    
    transaction = db.query(models.Transaction).filter(
        models.Transaction.book_id == book.id, 
        models.Transaction.status == "pending"
    ).first()
    
    if not transaction:
        return templates.TemplateResponse("transactions/return_book.html", {"request": request, "error": "No active borrowing record for this item", "today": date.today().isoformat()})
        
    return templates.TemplateResponse("transactions/return_book.html", {"request": request, "transaction": transaction, "today": date.today().isoformat()})

@app.post("/transactions/return-book")
async def return_book_exec(
    request: Request,
    transaction_id: int = Form(...),
    actual_return_date: date = Form(...),
    db: Session = Depends(get_db)
):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    
    fine = 0.0
    if actual_return_date > transaction.return_date:
        days_late = (actual_return_date - transaction.return_date).days
        fine = days_late * 10.0
        
    transaction.actual_return_date = actual_return_date
    transaction.fine_amount = fine
    db.commit()
    
    return RedirectResponse(url=f"/transactions/fine-pay?transaction_id={transaction.id}", status_code=303)

@app.get("/transactions/fine-pay", response_class=HTMLResponse)
async def fine_pay_page(request: Request, transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    return templates.TemplateResponse("transactions/fine_pay.html", {"request": request, "transaction": transaction})

@app.post("/transactions/fine-pay")
async def fine_pay_exec(
    request: Request,
    transaction_id: int = Form(...),
    fine_paid: bool = Form(False),
    remarks: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    
    if transaction.fine_amount > 0 and not fine_paid:
        return templates.TemplateResponse("transactions/fine_pay.html", {"request": request, "transaction": transaction, "error": "Please confirm fine payment"})
    
    transaction.fine_paid = fine_paid
    transaction.status = "returned"
    transaction.remarks = remarks
    
    book = db.query(models.Book).filter(models.Book.id == transaction.book_id).first()
    book.status = "available"
    
    db.commit()
    return RedirectResponse(url="/transactions", status_code=303)

@app.get("/reports", response_class=HTMLResponse)
async def reports_index(request: Request):
    return templates.TemplateResponse("reports/index.html", {"request": request})

@app.get("/reports/issued-books", response_class=HTMLResponse)
async def issued_books_report(request: Request, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(models.Transaction.status == "pending").all()
    return templates.TemplateResponse("reports/issued_books.html", {"request": request, "transactions": transactions})

@app.get("/reports/returned-books", response_class=HTMLResponse)
async def returned_books_report(request: Request, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(models.Transaction.status == "returned").all()
    return templates.TemplateResponse("reports/returned_books.html", {"request": request, "transactions": transactions})

@app.get("/reports/fine-collection", response_class=HTMLResponse)
async def fine_collection_report(request: Request, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(models.Transaction.fine_amount > 0).all()
    return templates.TemplateResponse("reports/fine_collection.html", {"request": request, "transactions": transactions})

@app.get("/reports/memberships", response_class=HTMLResponse)
async def memberships_report(request: Request, db: Session = Depends(get_db)):
    memberships = db.query(models.Membership).all()
    return templates.TemplateResponse("reports/memberships.html", {
        "request": request, 
        "memberships": memberships,
        "today_date": date.today()
    })

@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

def create_default_admin():
    db = database.SessionLocal()
    admin = db.query(models.User).filter(models.User.role == "admin").first()
    if not admin:
        default_admin = models.User(
            name="System Admin",
            username="admin",
            password="Password123",
            role="admin"
        )
        db.add(default_admin)
        db.commit()
    db.close()

create_default_admin()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
