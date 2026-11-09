from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
import models


# Create tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ---------- Database session ----------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Request and response models ----------

class BookRequest(BaseModel):
    title: str
    author: str


class BookResponse(BookRequest):
    id: int
    model_config = ConfigDict(from_attributes=True)


class MemberRequest(BaseModel):
    name: str


class MemberResponse(MemberRequest):
    id: int
    model_config = ConfigDict(from_attributes=True)


class IssueRequest(BaseModel):
    member_id: int
    book_id: int


class IssueResponse(IssueRequest):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==================================================
# BOOK APIs
# ==================================================

# GET all books
@app.get("/Books", response_model=list[BookResponse])
def get_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()


# GET book by ID
@app.get("/Books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(
        models.Book.id == book_id
    ).first()

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


# POST - Add one book
@app.post("/Books", response_model=BookResponse)
def create_book(book: BookRequest, db: Session = Depends(get_db)):
    new_book = models.Book(
        title=book.title,
        author=book.author
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


# PUT - Update a book
@app.put("/Books/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book: BookRequest,
    db: Session = Depends(get_db)
):
    existing_book = db.query(models.Book).filter(
        models.Book.id == book_id
    ).first()

    if existing_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    existing_book.title = book.title
    existing_book.author = book.author

    db.commit()
    db.refresh(existing_book)

    return existing_book


# DELETE - Delete a book
@app.delete("/Books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(
        models.Book.id == book_id
    ).first()

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    # Prevent deleting a book that has an issue record
    issue = db.query(models.Issue).filter(
        models.Issue.book_id == book_id
    ).first()

    if issue is not None:
        raise HTTPException(
            status_code=400,
            detail="Return the book before deleting it"
        )

    db.delete(book)
    db.commit()

    return {"message": "Book deleted successfully"}


# ==================================================
# MEMBER APIs
# ==================================================

# GET all members
@app.get("/Members", response_model=list[MemberResponse])
def get_members(db: Session = Depends(get_db)):
    return db.query(models.Member).all()


# GET member by ID
@app.get("/Members/{member_id}", response_model=MemberResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(models.Member).filter(
        models.Member.id == member_id
    ).first()

    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    return member


# POST - Add one member
@app.post("/Members", response_model=MemberResponse)
def create_member(
    member: MemberRequest,
    db: Session = Depends(get_db)
):
    new_member = models.Member(name=member.name)

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return new_member


# PUT - Update a member
@app.put("/Members/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: int,
    member: MemberRequest,
    db: Session = Depends(get_db)
):
    existing_member = db.query(models.Member).filter(
        models.Member.id == member_id
    ).first()

    if existing_member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    existing_member.name = member.name

    db.commit()
    db.refresh(existing_member)

    return existing_member


# DELETE - Delete a member
@app.delete("/Members/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(models.Member).filter(
        models.Member.id == member_id
    ).first()

    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    issue = db.query(models.Issue).filter(
        models.Issue.member_id == member_id
    ).first()

    if issue is not None:
        raise HTTPException(
            status_code=400,
            detail="Resolve the member's issue records first"
        )

    db.delete(member)
    db.commit()

    return {"message": "Member deleted successfully"}


# ==================================================
# ISSUE AND RETURN APIs
# ==================================================

# GET all issue records
@app.get("/Issues", response_model=list[IssueResponse])
def get_issues(db: Session = Depends(get_db)):
    return db.query(models.Issue).all()


# POST - Issue a book to a member
@app.post("/Issues", response_model=IssueResponse)
def issue_book(
    issue: IssueRequest,
    db: Session = Depends(get_db)
):
    book = db.query(models.Book).filter(
        models.Book.id == issue.book_id
    ).first()

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    member = db.query(models.Member).filter(
        models.Member.id == issue.member_id
    ).first()

    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    # Prevent issuing a book that already has an active issue record
    existing_issue = db.query(models.Issue).filter(
        models.Issue.book_id == issue.book_id
    ).first()

    if existing_issue is not None:
        raise HTTPException(
            status_code=400,
            detail="This book is already issued"
        )

    new_issue = models.Issue(
        member_id=issue.member_id,
        book_id=issue.book_id
    )

    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    return new_issue


# DELETE an issue record to return the book
@app.delete("/Issues/{issue_id}")
def return_book(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(
        models.Issue.id == issue_id
    ).first()

    if issue is None:
        raise HTTPException(
            status_code=404,
            detail="Issue record not found"
        )

    db.delete(issue)
    db.commit()

    return {"message": "Book returned successfully"}