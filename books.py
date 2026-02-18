from fastapi import FastAPI, Body

app = FastAPI()

BOOKS = [
  {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
  {'title': 'Title Two', 'author': 'Author Two', 'category': 'history'},
  {'title': 'Title Three', 'author': 'Author Three', 'category': 'geography'},
  {'title': 'Title Four', 'author': 'Author Four', 'category': 'geography'},
  {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
  {'title': 'Title Six', 'author': 'Author One', 'category': 'philosophy'}
]

@app.get('/books')
async def read_all_books():
  return BOOKS

# '/' в конце адреса дает возможность самостоятельного
# введения параметра в стиле ?title=...
# это пример query параметра
@app.get('/books/withtitle/')
async def read_book(book_title: str):
  for book in BOOKS:
    # casefold (перевод в малый регистр)
    if book.get('title').casefold() == book_title.casefold():
      return book
    
@app.get('/books/withcategory/')
async def read_books_by_category(book_category: str):
  books_to_return = []
  for book in BOOKS:
    if book.get('category').casefold() == book_category.casefold():
      books_to_return.append(book)
  return books_to_return

@app.get('/books/byauthor/')
async def read_books_by_author(book_author: str):
  books_to_return = []
  for book in BOOKS:
    if book.get('author').casefold() == book_author.casefold():
      books_to_return.append(book)
  return books_to_return

# '/books/{...}/' это пример path параметра в сочетании с query параметром (ПОРЯДОК РОУТОВ ВАЖЕН)
@app.get('/books/{book_author}/')
async def read_books_by_author_and_category(book_author: str, category: str):
  books_to_return = []
  for book in BOOKS:
    # \ нужен для понимания компилятором, что условие продолжается на некст строке
    if book.get('author').casefold() == book_author.casefold() and \
    book.get('category').casefold() == category.casefold():
      books_to_return.append(book)
  return books_to_return

@app.post('/books/create_book')
async def create_book(new_book=Body()):
  BOOKS.append(new_book)

@app.put('/books/update_book')
async def update_book(updated_book=Body()):
  for i in range(len(BOOKS)):
    if BOOKS[i].get('title').casefold() == updated_book.get('title').casefold():
      BOOKS[i] = updated_book
      break
    
# '/books/delete_book/{...}' это пример чистого path параметра (динамическое значение)
@app.delete('/books/delete_book/{book_title}')
async def delete_book(book_title: str):
  for i in range(len(BOOKS)):
    if BOOKS[i].get('title').casefold() == book_title.casefold():
      BOOKS.pop(i)
      break