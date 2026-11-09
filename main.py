from database import SessionLocal,Base,engine
from models import Book, Member, Issue
import models
from collections import defaultdict

Base.metadata.create_all(bind=engine)

db=SessionLocal()
print("Connected database:", db.execute(
    __import__("sqlalchemy").text("SELECT DATABASE()")
).scalar())

print("Members from MySQL:", db.execute(
    __import__("sqlalchemy").text("SELECT * FROM members")
).fetchall())

details = [
    {
        "Book_id": book.id,
        "Book_Name": book.title,
        "Book_Author": book.author
    }
    for book in db.query(Book).all()
]
persons = []
mtobid = defaultdict(list)
persons=[]
mtobid=defaultdict(list)


print("\n===== Library Management System =====")
print("1. Add Book")
print("2. View Books")
print("3. Search Book")
print("4. Add Member")
print("5. View Members")
print("6. Issue Book")
print("7. Return Book")
print("8. Delete Book")
print("9. Exit")


def Enter_details():
    book={
        "Book_id":int(input("Enter your Book id is:")),
        "Book_Name":(input("Enter Book Name is:")),
        "Book_Author":(input("Enter Author Name is:"))
}
    details.append(book)
    db_book = Book(
        id=book["Book_id"],
        title=book["Book_Name"],
        author=book["Book_Author"]
    )

    db.add(db_book)
    db.commit()
   


def add_members():
    name = input("Enter your name is : ").strip()

    if not name:
        print("Please enter a valid name.")
        return

    existing_member = db.query(Member).filter(
        Member.name.ilike(name)
    ).first()

    if existing_member:
        print("This member already exists.")
        return

    db_member = Member(name=name)

    db.add(db_member)
    db.commit()

    persons.append(db_member.name)

    print("Member added successfully:", db_member.name)

    


while True:

    choice = int(input("Enter your choice: "))

    if choice == 1:
        print("Adding Book")
        Enter_details()

    elif choice == 2:
        print("View Books")
        books = db.query(Book).all()
        for book in books:
            print(book.id, book.title, book.author)

    elif choice == 3:
        s_id=int(input("Enter Book id for search:"))
        print("Search Book")
        book_found=False
        for i in range(len(details)):
           d=details[i]
           d_id=d["Book_id"]
           if d_id==s_id:
               print("Our book details:",d)
               book_found=True
               break
        if book_found==False:
               print("No Book with:",s_id)
        

    elif choice == 4:
        print("Add Member")
        add_members()


    elif choice == 5:
        print("View Members")

        persons = [
            member.name
            for member in db.query(Member).all()
        ]

        if persons:
            for person in persons:
                print(person)
        else:
            print("No members found.")

    
    elif choice == 6:
        print("Issue Book")

        username = input("Enter your Name: ").strip()

        # Check member in database
        member = db.query(Member).filter(
            Member.name.ilike(username)
        ).first()

        if member is None:
            print("There is no person with this name")
            continue

        # Display available books
        books = db.query(Book).all()

        if not books:
            print("No books are available.")
            continue

        print("Available books:")

        for book in books:
            print(book.id, book.title, book.author)

        u_id = int(input("Enter book id: "))

        # Check selected book
        selected_book = db.query(Book).filter(
            Book.id == u_id
        ).first()

        if selected_book is None:
            print("Book is not there with this id:", u_id)
            continue

        # Check whether the book is already issued
        existing_issue = db.query(Issue).filter(
            Issue.book_id == u_id
        ).first()

        if existing_issue:
            print("This book is already issued.")
            continue

        # Store issue details in MySQL
        new_issue = Issue(
            member_id=member.id,
            book_id=selected_book.id
        )

        db.add(new_issue)
        db.commit()
        db.refresh(new_issue)

        print("Book issued successfully to:", member.name)
        print("Issue ID:", new_issue.id)
        print("Member ID:", member.id)
        print("Book ID:", selected_book.id)
    
    elif choice == 7:
        print("Return Book")

        name = input("Enter your Name: ").strip()

        members = db.query(Member).all()

        member = None

        for person in members:
            if person.name.strip().lower() == name.lower():
                member = person
                break

        if member is None:
            print("This name is not present in the members list")
            continue

        print("Member found:", member.name)

        book_id = int(input("Enter your Book id: "))

        issue = db.query(Issue).filter(
            Issue.member_id == member.id,
            Issue.book_id == book_id
        ).first()

        if issue is None:
            print("This member has not issued this book.")
            continue

        db.delete(issue)
        db.commit()

        print("Book returned successfully!")
        print("Returned by:", member.name)
        print("Returned Book ID:", book_id)




    # elif choice == 7:
    #     print("Return Book")
    #     name=input("Enter your Name:")

    #     if name.lower() not in [person.lower() for person in persons]:
    #         print("There is no person with this name")
    #         continue

    #     id=int(input("Enter your Book id:"))
    #     if name in mtobid[id]:
    #         print("Return your book")
    #         mtobid[id].remove(name)
    #         print("Remove Name is:",name) 
    #     else:
    #         print("You have already Returned")
        
    
    elif choice == 8:
        print("Delete Book")
        id1 = int(input("Enter Book id you want to delete:"))
        book_found = False

        # Delete from Python list
        for i in range(len(details)):
            if details[i]["Book_id"] == id1:
                deleted_book = details.pop(i)
                print("Book is Deleted:", deleted_book)
                book_found = True
                break

        # Delete from database
        book = db.query(Book).filter(Book.id == id1).first()

        if book:
            db.delete(book)
            db.commit()
            print("Book is Deleted from database")
            book_found = True


        if not book_found:
            print("No book with this id:", id1)
            
                

    elif choice == 9:
        print("Thank you for using Library Management System")
        break

    else:
        print("Invalid choice. Please enter a number from 1 to 9.")