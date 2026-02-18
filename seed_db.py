import models
import database
from datetime import date, timedelta
from sqlalchemy.orm import Session

def seed():
    db = database.SessionLocal()
    
    db.query(models.Transaction).delete()
    db.query(models.Book).delete()
    db.query(models.Membership).delete()
    db.query(models.User).delete()
    db.commit()

    users = [
        models.User(name="System Admin", username="admin", password="Password123", role="admin"),
        models.User(name="John Doe", username="john", password="Password123", role="user"),
        models.User(name="Jane Smith", username="jane", password="Password123", role="user"),
    ]
    db.add_all(users)
    db.commit()

    memberships = [
        models.Membership(
            membership_number="M001", name="John Doe", address="123 Library St", 
            phone="555-0101", start_date=date.today() - timedelta(days=30), 
            expiry_date=date.today() + timedelta(days=150), duration="6 Months"
        ),
        models.Membership(
            membership_number="M002", name="Jane Smith", address="456 Book Ave", 
            phone="555-0102", start_date=date.today() - timedelta(days=60), 
            expiry_date=date.today() + timedelta(days=305), duration="1 Year"
        ),
    ]
    db.add_all(memberships)
    db.commit()

    books = [
        models.Book(serial_number="B001", name="The Great Gatsby", author="F. Scott Fitzgerald", category="Classic", type="Book", status="issued"),
        models.Book(serial_number="B002", name="1984", author="George Orwell", category="Dystopian", type="Book", status="available"),
        models.Book(serial_number="B003", name="Inception", author="Christopher Nolan", category="Sci-Fi", type="Movie", status="available"),
        models.Book(serial_number="B004", name="The Hobbit", author="J.R.R. Tolkien", category="Fantasy", type="Book", status="available"),
        models.Book(serial_number="B005", name="Interstellar", author="Christopher Nolan", category="Sci-Fi", type="Movie", status="issued"),
    ]
    db.add_all(books)
    db.commit()

    late_issue = date.today() - timedelta(days=20)
    expected_return = late_issue + timedelta(days=15)
    
    t1 = models.Transaction(
        book_id=1, user_id=2, issue_date=late_issue, 
        return_date=expected_return, status="pending"
    )
    
    t2 = models.Transaction(
        book_id=5, user_id=3, issue_date=date.today() - timedelta(days=2), 
        return_date=date.today() + timedelta(days=13), status="pending"
    )
    
    db.add_all([t1, t2])
    db.commit()
    
    db.close()

if __name__ == "__main__":
    seed()
