from fastapi import FastAPI, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

app = FastAPI()

BOOKS = []

class Book:
  id: int
  title: str
  author: str
  description: str
  rating: int
  published_date: int

  def __init__(self, id, title, author, description, rating, published_date):
    self.id = id
    self.title = title
    self.author = author
    self.description = description
    self.rating = rating
    self.published_date = published_date

class BookRequest(BaseModel):
  # просто необязательное id: int | None = None
  # необязательное с параметрами (больше 0 и с описанием), по дефолту пустое
  id: int | None = Field(default=None, ge=0, description='ID is optional')
  title: str = Field(min_length=3)
  author: str = Field(min_length=1)
  description: str = Field(min_length=1, max_length=100)
  rating: int = Field(ge=1, le=5) # ge - greater or equal | gt greater than
  published_date: int = Field(ge=0, le=2026)

  model_config = { # редактирование стандартной схемы в /docs
    "json_schema_extra": {
      "example": {
        "title": "Book title",
        "author": "Author name",
        "rating": 5,
        "description": "A little about book",
        "published_date": 2026
      }
    }
  }
    
BOOKS = [
  Book(0, 'My system design interview', 'Amigo', 'I Bombed My System Design Interview on Rate Limiting', 4, 2006),
  Book(1, 'The Rise of the ‘Context Engineer’', 'Amigo', 'The real skill is curating what the AI sees before you even ask your question.', 3, 2015),
  Book(2, 'A Single Timeout Setting', 'Amigo', 'System is defaults, retries, and what happens at 2 a.m. when nothing responds.', 5, 2000),
  Book(3, 'HP1', 'Author 1', 'Book Description', 1, 2006),
  Book(4, 'HP2', 'Author 2', 'Book Description', 1, 2025),
  Book(5, 'HP3', 'Author 3', 'Book Description', 1, 1978)
]

@app.get('/books', status_code=status.HTTP_200_OK)
async def read_all_books():
  return BOOKS

@app.get('/books/{book_id}', status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(ge=0)):
  for book in BOOKS:
    if book.id == book_id:
      return book
  # ошибка на сервере при не существующем айди
  raise HTTPException(status_code=404, detail='Item not found')

@app.get('/books/rating/', status_code=status.HTTP_200_OK)
async def read_books_by_rating(book_rating: int = Query(ge=1, le=5)):
  books_to_return = [] 
  for book in BOOKS:
    if book.rating == book_rating:
      books_to_return.append(book)
  return books_to_return

@app.get('/books/publication/', status_code=status.HTTP_200_OK)
async def read_books_by_published_date(book_published_date: int = Query(ge=0, le=2026)):
  books_to_return = [] 
  for book in BOOKS:
    if book.published_date == book_published_date:
      books_to_return.append(book)
  return books_to_return

@app.post('/createbook', status_code=status.HTTP_201_CREATED)
async def add_book(book_request: BookRequest):
  # model_dump превращает в обычный словарь | ** распаковывает на аргументы конструктору
  new_book = Book(**book_request.model_dump())
  BOOKS.append(find_book_id(new_book))

def find_book_id(book: Book):
  book.id = BOOKS[-1].id + 1 if len(BOOKS) > 0 else 1
  return book

@app.put('/books/update_book', status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_request: BookRequest):
  founded = False
  for i in range(len(BOOKS)):
    if BOOKS[i].id == book_request.id:
      BOOKS[i] = book_request
      founded = True
      break
  if not founded:
    raise HTTPException(status_code=404, detail='Item not found')

@app.delete('/books/delete_book/{book_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(ge=0)):
  founded = False
  for i in range(len(BOOKS)):
    if BOOKS[i].id == book_id:
      BOOKS.pop(i)
      founded = True
      break
  if not founded:
    raise HTTPException(status_code=404, detail='Item not found')