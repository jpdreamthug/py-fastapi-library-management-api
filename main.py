from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from crud import (
    get_all_authors,
    get_all_books,
    create_book,
    get_author_by_name,
    create_author,
    get_author,
)
from database import (
    engine,
    Base,
    SessionLocal,
)
from schemas import (
    Author,
    Book,
    BookCreate,
    AuthorCreate,
)

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root() -> dict:
    return {"message": "Hello World"}


@app.get("/authors/", response_model=list[Author])
def read_authors(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db),
) -> list[Author]:
    return get_all_authors(db=db, skip=skip, limit=limit)


@app.post("/authors/", response_model=Author)
def create_new_author(
        author: AuthorCreate,
        db: Session = Depends(get_db)
) -> Author:
    db_author = get_author_by_name(db=db, name=author.name)

    if db_author:
        raise HTTPException(
            status_code=400,
            detail="Such name for Author already exists"
        )

    return create_author(db=db, author=author)


@app.get("/authors/{author_id}", response_model=Author)
def read_single_author(
        author_id: int,
        db: Session = Depends(get_db)
) -> Author:
    db_author = get_author(db=db, author_id=author_id)

    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")

    return db_author


@app.get("/books/", response_model=list[Book])
def read_books(
        author_id: int | None = None,
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 10,
) -> list[Book]:
    return get_all_books(db=db, author_id=author_id, skip=skip, limit=limit)


@app.post("/books/", response_model=Book)
def create_new_book(
        book: BookCreate,
        db: Session = Depends(get_db),
) -> Book:
    return create_book(db=db, book=book)
